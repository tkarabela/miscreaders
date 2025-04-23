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

    See Also:
        :py:class:`StayfreeXlsReader` for reader of the official file export format.

    """
    def __init__(self, backup_path: PathOrStr) -> None:
        """
        Args:
            backup_path: Path to exported file
        """
        self.path = Path(backup_path)

    def get_usage_time_df(self, lookup_app_name: bool = True) -> pl.DataFrame:
        """
        Return dataframe with app usage time

        Args:
            lookup_app_name: Translate package names (eg. ``"com.google.android.youtube"``)
                into human-readable app names (eg. ``"YouTube"``).

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
                    """
                    SELECT
                        a.TIMESTAMP as timestamp,
                        a.PACKAGE_NAME as package_name,
                        a.TOTAL_USAGE_TIME as total_usage_time,
                        b.APP_NAME as app_name
                    FROM
                        DailyUsageStatsEntity a
                        LEFT JOIN AppInfoEntity b ON a.PACKAGE_NAME = b.PACKAGE_NAME
                    """,
                    con
                ).select(
                    pl.from_epoch("timestamp", "ms").cast(pt.Date).alias("date"),
                    (
                        pl.col("app_name").fill_null(pl.col("package_name")).alias("app")
                        if lookup_app_name
                        else pl.col("package_name").alias("app")
                    ),
                    pl.duration(milliseconds="total_usage_time").alias("duration"),
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
