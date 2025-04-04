"""
Moonwatch.rs
============

.. autoclass:: MoonwatchLogReader

.. autoclass:: MoonwatchLogDirectoryReader

.. invisible-code-block: python

    path_to_jsonl = "tests/test_moonwatch/test.jsonl"
    path_to_dir = "tests/test_moonwatch"

"""

import gzip
from typing import Iterator, Type
import polars as pl
import polars.datatypes as pt
from pathlib import Path

from ..common import PathOrStr


class MoonwatchLogReader:
    """
    Reader for Moonwatch.rs log file

    References:
        https://github.com/tkarabela/moonwatch-rs

    """
    def __init__(self, jsonl_path: PathOrStr) -> None:
        """
        Args:
            jsonl_path: Path to JSONL file (``*.jsonl``, ``*.jsonl.gz``)
        """
        self.json_path = Path(jsonl_path)

    def get_df(self) -> pl.DataFrame:
        r"""
        Return dataframe with log content

        Example:
            >>> from miscreaders.moonwatch import MoonwatchLogReader
            >>> reader = MoonwatchLogReader(path_to_jsonl)
            >>> reader.get_df()
            shape: (5, 8)
            ┌────────────┬────────────┬────────────┬───────────┬───────────┬───────────┬───────────┬───────────┐
            │ type       ┆ time       ┆ duration   ┆ hostname  ┆ username  ┆ idle_for  ┆ process_p ┆ tags      │
            │ ---        ┆ ---        ┆ ---        ┆ ---       ┆ ---       ┆ ---       ┆ ath       ┆ ---       │
            │ enum       ┆ datetime[μ ┆ duration[μ ┆ str       ┆ str       ┆ duration[ ┆ ---       ┆ list[str] │
            │            ┆ s]         ┆ s]         ┆           ┆           ┆ μs]       ┆ str       ┆           │
            ╞════════════╪════════════╪════════════╪═══════════╪═══════════╪═══════════╪═══════════╪═══════════╡
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 1m 22s    ┆ C:\test-p ┆ []        │
            │ owEvent    ┆ 21:40:24.5 ┆            ┆ name      ┆           ┆           ┆ rogram.ex ┆           │
            │            ┆ 43149      ┆            ┆           ┆           ┆           ┆ e         ┆           │
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 3m 38s    ┆ C:\other- ┆ ["tag-a"] │
            │ owEvent    ┆ 00:20:12.3 ┆            ┆ name      ┆           ┆           ┆ program.e ┆           │
            │            ┆ 26975      ┆            ┆           ┆           ┆           ┆ xe        ┆           │
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 3m 23s    ┆ C:\test-p ┆ []        │
            │ owEvent    ┆ 00:19:57.3 ┆            ┆ name      ┆           ┆           ┆ rogram.ex ┆           │
            │            ┆ 17296      ┆            ┆           ┆           ┆           ┆ e         ┆           │
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 3m 8s     ┆ C:\test-p ┆ []        │
            │ owEvent    ┆ 00:19:42.3 ┆            ┆ name      ┆           ┆           ┆ rogram.ex ┆           │
            │            ┆ 14747      ┆            ┆           ┆           ┆           ┆ e         ┆           │
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 2m 53s    ┆ C:\other- ┆ ["tag-a", │
            │ owEvent    ┆ 00:19:27.3 ┆            ┆ name      ┆           ┆           ┆ program.e ┆ "tag-b"]  │
            │            ┆ 06595      ┆            ┆           ┆           ┆           ┆ xe        ┆           │
            └────────────┴────────────┴────────────┴───────────┴───────────┴───────────┴───────────┴───────────┘

        """
        if self.json_path.suffix == ".gz":
            with gzip.open(self.json_path, "rb") as fp:
                df = pl.read_ndjson(fp, schema=self._MOONWATCH_SCHEMA_RAW)
        else:
            df = pl.read_ndjson(self.json_path, schema=self._MOONWATCH_SCHEMA_RAW)

        return df.with_columns(
            pl.duration(seconds="duration").alias("duration"),
            pl.duration(seconds="idle_for").alias("idle_for"),
        )

    _MOONWATCH_SCHEMA_RAW: dict[str, Type[pl.DataType] | pl.DataType] = {
        "type": pt.Enum(["ActiveWindowEvent"]),
        "time": pt.Datetime,
        "duration": pt.Int32,
        "hostname": pt.String,
        "username": pt.String,
        "idle_for": pt.Int32,
        "process_path": pt.String,
        "tags": pt.List(pt.String),
    }


class MoonwatchLogDirectoryReader:
    """
    Helper class for batch reading of Moonwatch.rs logs

    You can use this to read entire log directory (eg. ``~/.moonwatch-rs/log``)
    into one dataframe.

    See Also:
        `MoonwatchLogReader`

    """
    def __init__(self, dir_path: PathOrStr) -> None:
        """
        Args:
            dir_path: Path to directory with ``*.jsonl``, ``*.jsonl.gz`` files
        """
        self.dir_path = Path(dir_path)

    def iter_dfs(self) -> Iterator[pl.DataFrame]:
        """Iterate over dataframes from individual log files"""
        for path in self.dir_path.glob("*.jsonl.gz"):
            yield MoonwatchLogReader(path).get_df()

        for path in self.dir_path.glob("*.jsonl"):
            yield MoonwatchLogReader(path).get_df()

    def get_df(self, rechunk: bool = True) -> pl.DataFrame:
        r"""
        Return concatenated dataframe of all logs in directory

        Args:
            rechunk: Reallocate data into contiguous memory for better performance
                (on by default)

        Example:
            >>> from miscreaders.moonwatch import MoonwatchLogDirectoryReader
            >>> reader = MoonwatchLogDirectoryReader(path_to_dir)
            >>> reader.get_df()
            shape: (15, 8)
            ┌────────────┬────────────┬────────────┬───────────┬───────────┬───────────┬───────────┬───────────┐
            │ type       ┆ time       ┆ duration   ┆ hostname  ┆ username  ┆ idle_for  ┆ process_p ┆ tags      │
            │ ---        ┆ ---        ┆ ---        ┆ ---       ┆ ---       ┆ ---       ┆ ath       ┆ ---       │
            │ enum       ┆ datetime[μ ┆ duration[μ ┆ str       ┆ str       ┆ duration[ ┆ ---       ┆ list[str] │
            │            ┆ s]         ┆ s]         ┆           ┆           ┆ μs]       ┆ str       ┆           │
            ╞════════════╪════════════╪════════════╪═══════════╪═══════════╪═══════════╪═══════════╪═══════════╡
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 57s       ┆ C:\test-p ┆ []        │
            │ owEvent    ┆ 00:12:57.1 ┆            ┆ name      ┆           ┆           ┆ rogram.ex ┆           │
            │            ┆ 11274      ┆            ┆           ┆           ┆           ┆ e         ┆           │
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 42s       ┆ C:\test-p ┆ []        │
            │ owEvent    ┆ 00:12:42.1 ┆            ┆ name      ┆           ┆           ┆ rogram.ex ┆           │
            │            ┆ 10712      ┆            ┆           ┆           ┆           ┆ e         ┆           │
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 27s       ┆ C:\test-p ┆ []        │
            │ owEvent    ┆ 00:12:27.1 ┆            ┆ name      ┆           ┆           ┆ rogram.ex ┆           │
            │            ┆ 08317      ┆            ┆           ┆           ┆           ┆ e         ┆           │
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 12s       ┆ C:\test-p ┆ []        │
            │ owEvent    ┆ 00:12:12.0 ┆            ┆ name      ┆           ┆           ┆ rogram.ex ┆           │
            │            ┆ 97326      ┆            ┆           ┆           ┆           ┆ e         ┆           │
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 0µs       ┆ C:\test-p ┆ []        │
            │ owEvent    ┆ 00:11:57.0 ┆            ┆ name      ┆           ┆           ┆ rogram.ex ┆           │
            │            ┆ 94459      ┆            ┆           ┆           ┆           ┆ e         ┆           │
            │ …          ┆ …          ┆ …          ┆ …         ┆ …         ┆ …         ┆ …         ┆ …         │
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 1m 22s    ┆ C:\test-p ┆ []        │
            │ owEvent    ┆ 21:40:24.5 ┆            ┆ name      ┆           ┆           ┆ rogram.ex ┆           │
            │            ┆ 43149      ┆            ┆           ┆           ┆           ┆ e         ┆           │
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 3m 38s    ┆ C:\other- ┆ ["tag-a"] │
            │ owEvent    ┆ 00:20:12.3 ┆            ┆ name      ┆           ┆           ┆ program.e ┆           │
            │            ┆ 26975      ┆            ┆           ┆           ┆           ┆ xe        ┆           │
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 3m 23s    ┆ C:\test-p ┆ []        │
            │ owEvent    ┆ 00:19:57.3 ┆            ┆ name      ┆           ┆           ┆ rogram.ex ┆           │
            │            ┆ 17296      ┆            ┆           ┆           ┆           ┆ e         ┆           │
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 3m 8s     ┆ C:\test-p ┆ []        │
            │ owEvent    ┆ 00:19:42.3 ┆            ┆ name      ┆           ┆           ┆ rogram.ex ┆           │
            │            ┆ 14747      ┆            ┆           ┆           ┆           ┆ e         ┆           │
            │ ActiveWind ┆ 2025-04-02 ┆ 15s        ┆ test-host ┆ test-user ┆ 2m 53s    ┆ C:\other- ┆ ["tag-a", │
            │ owEvent    ┆ 00:19:27.3 ┆            ┆ name      ┆           ┆           ┆ program.e ┆ "tag-b"]  │
            │            ┆ 06595      ┆            ┆           ┆           ┆           ┆ xe        ┆           │
            └────────────┴────────────┴────────────┴───────────┴───────────┴───────────┴───────────┴───────────┘

        """
        return pl.concat(self.iter_dfs(), rechunk=rechunk)
