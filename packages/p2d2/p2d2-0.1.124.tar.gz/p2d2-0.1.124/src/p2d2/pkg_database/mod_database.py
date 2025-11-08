import atexit
import signal
import sqlite3
import sys
from functools import cached_property
from pathlib import Path
from uuid import UUID

import pandas as pd
from loguru import logger as log
from pandas import DataFrame
from toomanyconfigs import CWD

from src.p2d2.pkg_database.mod_database_resources import DataFrameResource
from .mod_database_models import IDatabase
from .mod_database_resources import SQLiteResource, DataFrameResource
from .mod_schema import Schema, Table
from .pkg_util import Analytics, migrate_table_schema
from ezmq import Jobs, MessageQueue, Response, Message


class Database(IDatabase):
    def __init__(self, schema: type[Schema], cwd: Path = Path.cwd(), **kwargs):
        self.schema: type[Schema] = schema
        if not kwargs.get("name"): self.name = self.schema.__name__
        else: self.name = kwargs.get("name")

        from . import AUTOSAVE, BACKUP
        self.cwd = CWD(
            {f"{self.name}":
                {
                    f"{self.name}.db": None,
                    "changes.pkl": None,
                    "message_queue.pkl": None,
                    "config.toml": None,
                    "backups": {},
                    "cron_jobs": {
                        "autosave.py": AUTOSAVE,
                        "backup.py": BACKUP,
                    }
                }
            },
            path=cwd
        )

        self.path = self.cwd.file_structure[0]
        self.sqlite = SQLiteResource(self.path)
        self.tables: dict[str, DataFrameResource] = {}
        self.resources: dict[str, DataFrameResource | SQLiteResource] = {
            "db": self.sqlite,
        }

        self.table_schemas: dict[str, type[Table]] = self.schema.get_tables()
        for name in self.table_schemas:
            self.resources[name] = DataFrameResource(name, self.schema, self.sqlite)
            self.tables[name] = self.resources[name]

        class DatabaseJobs(Jobs):
            from . import Create, Read, Update, Delete
            resources = self.resources
            create: Create
            read: Read
            update: Update
            delete: Delete

        self.job_types = DatabaseJobs
        _ = self.message_queue
        self.fetch_all()

        atexit.register(self._cleanup)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        sys.excepthook = self._exception_handler

        _ = self.cron

    def _cleanup(self):
        log.debug(f"{self}: Program exiting, committing database")
        self.commit_all()
        self.pkl.commit()

    def _signal_handler(self, signum, frame):
        log.debug(f"{self}: Received signal {signum}, committing database")
        exit(0)

    def _exception_handler(self, exc_type, exc_value, exc_traceback):
        log.warning(f"{self}: Unhandled exception detected, committing database")
        self.commit_all()
        self.pkl.commit()
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    def __repr__(self):
        return f"[{self.name}.db]"

    def get_table(self, table_name: str) -> DataFrameResource | None:
        if table_name in self.tables:
            return self.tables[table_name]
        return None

    def fetch(self, table_name: str = None) -> bool:
        log.debug(f"{self}: Fetching table '{table_name}' from path '{self.path}'")
        table = self.get_table(table_name)
        result = table.fetch(self.sqlite)
        return result

    def fetch_all(self):
        successes = 0
        for table_name in self.table_schemas.keys():
            if self.get_table(table_name).commit(self.sqlite): successes += 1
        if successes > 0:
            log.success(f"{self}: Successfully loaded {successes} table(s) from {self.path}")

    def commit(self, table_name: str):
        log.debug(f"{self}: Committing table '{table_name}' from path '{self.path}'")
        table = self.get_table(table_name)
        table.commit(self.sqlite)

    def commit_all(self):
        for table_name in self.tables.keys():
            table = self.get_table(table_name)
            table.commit(self.sqlite)

    @cached_property
    def pkl(self):
        from .pkg_pkl import PickleChangelog
        return PickleChangelog(self)

    @cached_property
    def message_queue(self):
        from ezmq import MessageQueue
        return MessageQueue(self.job_types)

    def batch_receive(self, messages: dict[str, UUID]) ->  tuple[dict[str, Response], dict[str, Response]]:
        return self.message_queue.batch_receive(messages)

    def _create_type_check(self, table_name: str, signature: str, **kwargs) -> dict[str, str]:
        if forbidden := set(kwargs) & {"pydb", "signature", "table_name"}: raise KeyError(f"{self}: Can't use reserved terms: {forbidden}")
        message = {"pydb": self, "table_name": table_name, "signature": signature} | kwargs
        return message

    def create(self, table_name: str, signature: str, timeout: int = 30, **kwargs) -> Response:
        message_id = self.send_create(table_name, signature, **kwargs)
        return self.receive_create(message_id, timeout)

    def send_create(self, table_name: str, signature: str, **kwargs) -> UUID:
        message = self._create_type_check(table_name, signature, **kwargs)
        return self.message_queue.send(job_type="create", **message)

    def receive_create(self, message_id: UUID, timeout: int = 30) -> Response:
        return self.message_queue.receive(message_id, timeout = timeout)

    def batch_send_create(self, table_name: str, signature: str, messages: dict[str, dict[str, str]]) -> dict[str, UUID]:
        formatted: dict[str, Message] = {}
        for job_name in messages:
            kwargs = messages[job_name]
            message = self._create_type_check(table_name, signature, **kwargs)
            formatted[job_name] = Message(job_type="create", payload=message)

        if len(formatted) != len(messages): raise RuntimeError(f"There was an unexpected error in processing! Expected' {messages.keys()}', got '{formatted.keys()}'")
        return self.message_queue.batch_send(formatted)

    def batch_create(self, table_name: str, signature: str, messages: dict[str, dict[str, str]]) -> tuple[dict[str, Response], dict[str, Response]]:
        messages = self.batch_send_create(table_name, signature, messages)
        return self.batch_receive(messages)

    def read(self, table_name: str, timeout: int = 30, **conditions):
        message = {"table_name": table_name} | conditions
        return self.message_queue.send_and_receive(job_type="read", timeout = timeout, **message)

    def _update_type_check(self, table_name: str, signature: str, conditions: dict, **kwargs) -> dict[str, str]:
        if forbidden := set(kwargs) & {"pydb", "signature", "table_name", "conditions"}: raise KeyError(
            f"{self}: Can't use reserved terms: {forbidden}")
        message = {"pydb": self, "table_name": table_name, "signature": signature, "conditions": conditions} | kwargs
        return message

    def update(self, table_name: str, signature: str, conditions: dict, timeout: int = 30, **kwargs) -> Response:
        message_id = self.send_update(table_name, signature, conditions, **kwargs)
        return self.receive_update(message_id, timeout)

    def send_update(self, table_name: str, signature: str, conditions: dict, **kwargs) -> UUID:
        message = self._update_type_check(table_name, signature, conditions, **kwargs)
        return self.message_queue.send(job_type="update", **message)

    def receive_update(self, message_id: UUID, timeout: int = 30) -> Response:
        return self.message_queue.receive(message_id, timeout=timeout)

    def batch_send_update(self, table_name: str, signature: str, messages: dict[str, dict[str, any]]) -> dict[
        str, UUID]:
        formatted: dict[str, Message] = {}
        for job_name in messages:
            data = messages[job_name]
            conditions = data.pop("conditions", {})
            message = self._update_type_check(table_name, signature, conditions, **data)
            formatted[job_name] = Message(job_type="update", payload=message)

        if len(formatted) != len(messages): raise RuntimeError(
            f"There was an unexpected error in processing! Expected' {messages.keys()}', got '{formatted.keys()}'")
        return self.message_queue.batch_send(formatted)

    def batch_update(self, table_name: str, signature: str, messages: dict[str, dict[str, any]]) -> tuple[
        dict[str, Response], dict[str, Response]]:
        messages = self.batch_send_update(table_name, signature, messages)
        return self.batch_receive(messages)

    def _delete_type_check(self, table_name: str, signature: str, **kwargs) -> dict[str, str]:
        if forbidden := set(kwargs) & {"pydb", "signature", "table_name"}: raise KeyError(
            f"{self}: Can't use reserved terms: {forbidden}")
        message = {"pydb": self, "table_name": table_name, "signature": signature} | kwargs
        return message

    def delete(self, table_name: str, signature: str, timeout: int = 30, **conditions) -> Response:
        message_id = self.send_delete(table_name, signature, **conditions)
        return self.receive_delete(message_id, timeout)

    def send_delete(self, table_name: str, signature: str, **conditions) -> UUID:
        message = self._delete_type_check(table_name, signature, **conditions)
        return self.message_queue.send(job_type="delete", **message)

    def receive_delete(self, message_id: UUID, timeout: int = 30) -> Response:
        return self.message_queue.receive(message_id, timeout=timeout)

    def batch_send_delete(self, table_name: str, signature: str, messages: dict[str, dict[str, str]]) -> dict[
        str, UUID]:
        formatted: dict[str, Message] = {}
        for job_name in messages:
            kwargs = messages[job_name]
            message = self._delete_type_check(table_name, signature, **kwargs)
            formatted[job_name] = Message(job_type="delete", payload=message)

        if len(formatted) != len(messages): raise RuntimeError(
            f"There was an unexpected error in processing! Expected' {messages.keys()}', got '{formatted.keys()}'")
        return self.message_queue.batch_send(formatted)

    def batch_delete(self, table_name: str, signature: str, messages: dict[str, dict[str, str]]) -> tuple[
        dict[str, Response], dict[str, Response]]:
        messages = self.batch_send_delete(table_name, signature, messages)
        return self.batch_receive(messages)

    @cached_property
    def cron(self):
        from .mod_cron import CronManager, CronLoader
        return CronManager(self, CronLoader)