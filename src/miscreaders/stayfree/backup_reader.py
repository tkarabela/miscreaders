import sqlite3
import tempfile
from contextlib import contextmanager, closing
from pathlib import Path
from typing import Generator

import polars as pl
import polars.datatypes as pt
import zipfile

from ..common import PathOrStr


class StayfreeBackupReader:
    """
    Reader for StayFree app data backup file on Google Drive

    This parser can extract data from StayFree internal data backup
    that can be scheduled or triggered manually at *Settings* > *Storage* > *Backup & Restore*.
    The backup gets stored as `application-specific data <https://developers.google.com/workspace/drive/api/guides/appdata>`_
    on your Google Drive.

    The problem with this is that there is no blessed way of accessing such data
    (other than deleting them) for the user; it is only meant to be accessed by the app.
    For a slightly cursed way of getting access, see https://github.com/albertored/google-drive-app-data.

    Note:
        This class reports app names as eg. ``"com.google.android.youtube"``
        instead of ``"YouTube"`` that is reported by :py:class:`StayfreeXlsReader`.

    See Also:
        :py:class:`StayfreeXlsReader` for reader of the official file export format.

    """
    def __init__(self, backup_path: PathOrStr) -> None:
        """
        Args:
            backup_path: Path to exported file
        """
        self.path = Path(backup_path)

    def get_usage_time_df(self) -> pl.DataFrame:
        """
        Return dataframe with app usage time

        .. skip: start

        Example:
            >>> from miscreaders.stayfree import StayfreeBackupReader
            >>> reader = StayfreeBackupReader("stayfree-dailybackup_PhoneName.backup-xxxxxx")
            >>> reader.get_usage_time_df()
            shape: (6_222, 4)
            ┌────────────┬─────────────┬──────────────┐
            │ date       ┆ app         ┆ duration     │
            │ ---        ┆ ---         ┆ ---          │
            │ date       ┆ str         ┆ duration[μs] │
            ╞════════════╪═════════════╪══════════════╡
            │ 2023-11-10 ┆ addititious ┆ 0µs          │
            │ 2023-11-11 ┆ addititious ┆ 0µs          │
            │ 2023-11-12 ┆ addititious ┆ 0µs          │
            │ 2023-11-13 ┆ addititious ┆ 0µs          │
            │ 2023-11-14 ┆ addititious ┆ 6s           │
            │ …          ┆ …           ┆ …            │
            │ 2024-03-06 ┆ xylometer   ┆ 53m 8s       │
            │ 2024-03-07 ┆ xylometer   ┆ 0µs          │
            │ 2024-03-08 ┆ xylometer   ┆ 30m 54s      │
            │ 2024-03-09 ┆ xylometer   ┆ 0µs          │
            │ 2024-03-10 ┆ xylometer   ┆ 0µs          │
            └────────────┴─────────────┴──────────────┘

        .. skip: end

        """
        with self.get_connection("usage_stats_event") as con:
            return (
                pl.read_database(
                    "SELECT TIMESTAMP, PACKAGE_NAME, TOTAL_USAGE_TIME FROM DailyUsageStatsEntity",
                    con
                ).select(
                    pl.from_epoch("TIMESTAMP", "ms").cast(pt.Date).alias("date"),
                    pl.col("PACKAGE_NAME").alias("app"),
                    pl.duration(milliseconds="TOTAL_USAGE_TIME").alias("duration"),
                )
            )

    @contextmanager
    def get_connection(self, db_name: str) -> Generator[sqlite3.Connection, None, None]:
        """
        Return read-only connection to the database extracted from the backup archive to temporary directory
        """
        with tempfile.TemporaryDirectory() as temp_dir, zipfile.ZipFile(self.path) as fp:
            fp.extract(db_name, temp_dir)
            db_path = Path(temp_dir) / db_name
            with closing(sqlite3.Connection(f"file:{db_path}?mode=ro", uri=True)) as con:
                yield con
