import json
import time
from datetime import datetime

import pandas as pd
from ezmq import Job, Resource
from loguru import logger as log


# class RequestToCRUD:
#     @staticmethod
#     def get_table_name(request: Request) -> str:
#         return request.query_params.get('table_name')
#
#     @staticmethod
#     def get_signature(request: Request) -> str:
#         return request.query_params.get('signature', 'unknown')
#
#     @staticmethod
#     def get_data(request: Request) -> dict:
#         return asyncio.run(request.json())
#
#     @classmethod
#     def to_create(cls, request: Request) -> dict:
#         return {
#             'table_name': cls.get_table_name(request),
#             'signature': cls.get_signature(request),
#             **cls.get_data(request)
#         }
#
#     @classmethod
#     def to_read(cls, request: Request) -> dict:
#         return {
#             'table_name': cls.get_table_name(request),
#             **cls.get_data(request)
#         }
#
#     @classmethod
#     def to_update(cls, request: Request) -> dict:
#         data = cls.get_data(request)
#         return {
#             'table_name': cls.get_table_name(request),
#             'signature': cls.get_signature(request),
#             'conditions': data.get('conditions', {}),
#             'updates': data.get('updates', {})
#         }
#
#     @classmethod
#     def to_delete(cls, request: Request) -> dict:
#         return {
#             'table_name': cls.get_table_name(request),
#             'signature': cls.get_signature(request),
#             **cls.get_data(request)
#         }

class Create(Job):
    required_resources = ["db"]

    def __init__(self):
        super().__init__()

    def execute(self, resources: dict[str, Resource], **kwargs):
        start_time = time.time()
        if not (pydb := kwargs.pop("pydb")): raise KeyError("'pydb' not found")
        if not (table_name := kwargs.pop("table_name")): raise KeyError("'table_name' not found")
        if not (signature := kwargs.pop("signature")): raise KeyError("'signature' not found")
        update = False

        with pydb.get_table(table_name) as table:

            try:
                unique_keys = pydb.table_schemas[table_name].get_unique_keys()
                log.debug(
                    f"Attempting to create in table '{pydb}':\n  - unique_keys: {unique_keys}\n  - kwargs: {kwargs}")

            except Exception as e:
                raise KeyError(f"Error retrieving table or unique keys: {e}")

            try:
                if len(unique_keys) > 0 and not len(table) == 0:
                    for key in unique_keys:
                        if key in kwargs and key in table.columns:
                            existing = table.loc[table[key] == kwargs[key]]
                            if not existing.empty:
                                log.debug(f"Found existing record with {key}={kwargs[key]}, updating instead")
                                update = True
            except Exception as e:
                raise RuntimeError(f"Error cross-checking unique keys: {e}")

            if not update:
                try:
                    new_idx = len(table)
                    log.debug(f"Adding new row at index: {new_idx}")

                    # Set audit columns
                    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    table.loc[new_idx, 'created_at'] = now_str  # TODO: this needs to be delegated
                    table.loc[new_idx, 'created_by'] = signature
                    table.loc[new_idx, 'modified_at'] = now_str
                    table.loc[new_idx, 'modified_by'] = signature

                    for col, value in kwargs.items():
                        log.debug(f"Setting {col} = {value} (type: {type(value)})")

                        # Serialize complex objects
                        if isinstance(value, (dict, list)):
                            import json
                            value = json.dumps(value)
                            log.debug(f"Serialized {col} to JSON string")

                        table.loc[new_idx, col] = value

                    pydb.pkl.log_change(signature, table_name, "create")
                    elapsed = time.time() - start_time
                    log.debug(f"{pydb}: Created row in {table_name}: {kwargs} (took {elapsed:.4f}s)")
                    return table

                except Exception as e:
                    import traceback
                    log.error(f"Exception in create method: {e}")
                    log.error(f"Full traceback: {traceback.format_exc()}")
                    raise

        if update:
            try:
                return Update.execute_now(
                    resources=resources,
                    pydb=pydb,
                    table_name=table_name,
                    signature=signature,
                    conditions=kwargs,
                )

            except Exception as e:
                raise RuntimeError(f"Exception in create -> update method: {e}")

    # @classmethod
    # def execute_now(cls, database: Database, table_name: str, signature, **kwargs):
    #     inst = cls(database, table_name, signature, **kwargs)
    #     return inst.execute()
    #
    # @classmethod
    # def from_request(cls, database: Database, request: Request):
    #     params = RequestToCRUD.to_create(request)
    #     return cls(database, **params)
    #
    # @classmethod
    # def execute_now_from_request(cls, database: Database, request: Request):
    #     return cls.from_request(database, request).execute()


class Read(Job):
    def __init__(self):
        super().__init__()

    def execute(self, resources: dict[str, Resource], **kwargs):
        start_time = time.time()
        if not (pydb := kwargs.pop("pydb")): raise KeyError("'pydb' not found")
        if not (table_name := kwargs.pop("table_name")): raise KeyError("'table_name' not found")
        if not (signature := kwargs.pop("signature")): raise KeyError("'signature' not found")

        with pydb.get_table(table_name) as table:
            if not kwargs:
                log.debug(f"Read all {len(table)} rows from {table_name} (took {time.time() - start_time:.4f}s)")
                return table

            mask = pd.Series([True] * len(table))
            for col, value in kwargs.items():
                if col in table.columns:
                    mask &= (table[col] == value)

            result = table[mask]
            log.debug(f"Read {len(result)} rows from {table_name} (took {time.time() - start_time:.4f}s)")
            return result


#
#     @classmethod
#     def execute_now(cls, database: Database, table_name: str, **conditions):
#         return cls(database, table_name, **conditions).execute()
#
#     @classmethod
#     def from_request(cls, database: Database, request: Request):
#         params = RequestToCRUD.to_read(request)
#         return cls(database, **params)
#
#     @classmethod
#     def execute_now_from_request(cls, database: Database, request: Request):
#         return cls.from_request(database, request).execute()
#
#
class Update(Job):
    def __init__(self):
        super().__init__()

    def execute(self, resources: dict[str, Resource], **kwargs):
        start_time = time.time()
        if not (pydb := kwargs.pop("pydb")): raise KeyError("'pydb' not found")
        if not (table_name := kwargs.pop("table_name")): raise KeyError("'table_name' not found")
        if not (signature := kwargs.pop("signature")): raise KeyError("'signature' not found")
        if not (conditions := kwargs.pop("conditions")): raise KeyError("'conditions' not found")

        with pydb.get_table(table_name) as table:

            mask = pd.Series([True] * len(table))
            for col, value in conditions.items():
                if col in table.columns:
                    mask &= (table[col] == value)

            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            table.loc[mask, 'modified_at'] = now_str
            table.loc[mask, 'modified_by'] = signature

            for col, value in kwargs.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                if col in table.columns:
                    table.loc[mask, col] = value

            updated_count = mask.sum()
            pydb.pkl.log_change(signature, table_name, "update")
            log.debug(
                f"Updated {updated_count} rows in {table_name} by {signature} (took {time.time() - start_time:.4f}s)")
            return table

    @classmethod
    def execute_now(cls, **kwargs):
        return cls().execute(**kwargs)


#     @classmethod
#     def from_request(cls, database: Database, request: Request):
#         params = RequestToCRUD.to_update(request)
#         return cls(database, **params)
#
#     @classmethod
#     def execute_now_from_request(cls, database: Database, request: Request):
#         return cls.from_request(database, request).execute()
#
#
class Delete(Job):
    def __init__(self):
        super().__init__()

    def execute(self, resources: dict[str, Resource], **kwargs):
        start_time = time.time()
        if not (pydb := kwargs.pop("pydb")): raise KeyError("'pydb' not found")
        if not (table_name := kwargs.pop("table_name")): raise KeyError("'table_name' not found")
        if not (signature := kwargs.pop("signature")): raise KeyError("'signature' not found")

        with pydb.get_table(table_name) as table:
            mask = pd.Series([True] * len(table))
            for col, value in kwargs.items():
                if col in table.columns:
                    mask &= (table[col] == value)

            result = table[~mask].reset_index(drop=True)
            table = result
            deleted_count = len(table) - len(result)
            pydb.pkl.log_change(signature, table_name, "delete")
            log.debug(
                f"Deleted {deleted_count} rows from {table_name} by {signature} (took {time.time() - start_time:.4f}s)")
            return table
#
#     @classmethod
#     def execute_now(cls, database: Database, table_name: str, signature: str, **conditions):
#         return cls(database, table_name, signature, **conditions).execute()
#
#     @classmethod
#     def from_request(cls, database: Database, request: Request):
#         params = RequestToCRUD.to_delete(request)
#         return cls(database, **params)
#
#     @classmethod
#     def execute_now_from_request(cls, database: Database, request: Request):
#         return cls.from_request(database, request).execute()
