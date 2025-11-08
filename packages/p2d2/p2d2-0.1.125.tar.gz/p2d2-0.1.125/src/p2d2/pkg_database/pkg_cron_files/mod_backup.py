BACKUP = """
from datetime import date
from pathlib import Path
from loguru import logger as log


def backup(database):
    today = date.today()
    backup_dir = Path(__file__).parent.parent / "backups"
    folder = Path(__file__).parent.parent / "backups" / str(today)

    if not backup_dir.exists():
        log.warning(f"{database}: Backup folder does not exist! Creating...")
        folder.mkdir(exist_ok=True)

    if not any(backup_dir.glob(f"{today}*")):
        log.warning(f"{database}: Backup not found for today! Creating...")
        folder.mkdir(exist_ok=True)
        if folder.exists():
            log.success(f"{database}: Successfully created backup folder at {folder}")
        else:
            raise FileNotFoundError

        for table_name in database.tables.keys():
            with database.get_table(table_name) as table:
                backup_path = folder / f"{table_name}.parquet"
                table.to_parquet(backup_path)

        log.success(f"{database}: Successfully backed up {len(database.tables)} table(s) to {folder}")

    else:
        log.info(f"{database}: Backup already exists for today! Skipping...")

INTERVAL = 60
FUNCTION = backup

"""