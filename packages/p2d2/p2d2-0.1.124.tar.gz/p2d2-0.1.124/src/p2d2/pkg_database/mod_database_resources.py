import sqlite3
from pathlib import Path
from sqlite3 import Connection

import pandas as pd
from ezmq import Resource
from pandas import DataFrame

from . import Schema
from loguru import logger as log


class SQLiteResource(Resource):
    def __init__(self, db_path: Path, identifier: str = None):
        self.db_path = db_path
        self.identifier = identifier or db_path.stem.lower()
        super().__init__(identifier = self.identifier)
        try:
            db_path.touch(exist_ok=True)
            conn = sqlite3.connect(self.db_path, timeout=30.0)
        except Exception:
            raise
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA busy_timeout=30000")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.commit()
        finally:
            conn.close()

    def _enter(self) -> Connection:
        self._connection = sqlite3.connect(self.db_path, timeout=30.0)
        return self._connection

    def _exit(self) -> None:
        self._connection.close()

    def _peek(self) -> 'SQLiteResource':
        pass

class DataFrameResource(Resource):
    """Thread-safe resource wrapper for a DataFrame"""

    def __init__(self, identifier: str, schema: type[Schema], sqlite_resource: SQLiteResource):
        super().__init__(identifier=identifier)
        self.schema = schema.get_tables().get(identifier, None)
        self.df: DataFrame = (schema_dfs := schema.initialize_dataframes()).get(identifier, None)
        self.df.fetch = self.fetch
        self.df.commit = self.commit
        if self.schema is None: raise KeyError(f"No schema named '{identifier}' in schemas, got '{schema.get_tables()}' instead")
        if self.df is None: raise KeyError(f"No table named '{identifier}' in schemas, got '{schema_dfs}' instead")
        with sqlite_resource as conn:
            self.fetch(conn)

    def _enter(self) -> DataFrame:
        """Return the DataFrame for modification"""
        table = self.df
        table_schema = self.schema

        for col, expected_type in table_schema.__annotations__.items():
            if col in table.columns:
                if expected_type == bool:
                    table[col] = table[col].fillna(False).astype(bool)
                elif expected_type == int:
                    table[col] = table[col].fillna(0).astype('int64')
                elif expected_type == float:
                    table[col] = table[col].fillna(0.0).astype('float64')
                elif expected_type == str:
                    table[col] = table[col].fillna('').astype('object')

        return table

    def _exit(self):
        pass

    def _peek(self) -> DataFrame:
        """Read-only view of the DataFrame"""
        return self.df.copy()

    def fetch(self, sqlite_resource: SQLiteResource) -> bool:
        table_name = self.identifier
        try:
            with sqlite_resource as conn:
                df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                self.df = df
                self.df.fetch = self.fetch
                self.df.commit = self.commit
                log.debug(f"{self}: Loaded '{table_name}' from SQLite3: {len(df)} rows")
                return True
        except pd.errors.DatabaseError:
            log.warning(f"{self}: Table '{table_name}' doesn't exist yet!")
            self.commit(sqlite_resource)
            return False


    def commit(self, sqlite_resource: SQLiteResource):
        """Commit a single table to database"""
        table_name = self.identifier
        with sqlite_resource as conn:
            with self as table:
                try:
                    df_copy = table.copy()

                    # Handle datetime columns
                    for col in df_copy.columns:
                        if df_copy[col].dtype == 'datetime64[ns]' or 'datetime' in str(df_copy[col].dtype):
                            df_copy[col] = pd.to_datetime(df_copy[col]).astype('datetime64[ns]').astype(object)

                    df_copy.to_sql(table_name, conn, if_exists='replace', index=False)
                    conn.commit()
                    log.debug(f"{self}: Committed to '{table_name}' from DataFrame: {len(df_copy)} rows")
                except pd.errors.DatabaseError:
                    raise