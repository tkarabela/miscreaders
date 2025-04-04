"""
Stayfree
========

.. autoclass:: StayfreeXlsReader

.. invisible-code-block: python

    path_to_xls = "tests/test_stayfree/test.xls"

"""

import re
from datetime import timedelta
from pathlib import Path
import polars as pl
import polars.datatypes as pt
import xlrd  # type: ignore[import-untyped]

from ..common import PathOrStr


class StayfreeXlsReader:
    """
    Reader for StayFree XLS export file

    References:
        https://stayfreeapps.com
        https://userguide.stayfreeapps.com/settings/backup-restore

    """
    def __init__(self, xls_path: PathOrStr) -> None:
        """
        Args:
            xls_path: Path to exported file
        """
        self.path = Path(xls_path)

    def get_usage_time_df(self) -> pl.DataFrame:
        """
        Return dataframe with app usage time

        Example:
            >>> from miscreaders.stayfree import StayfreeXlsReader
            >>> reader = StayfreeXlsReader(path_to_xls)
            >>> reader.get_usage_time_df()
            shape: (6_222, 4)
            ┌────────────┬─────────────┬──────────────┬────────┐
            │ date       ┆ app         ┆ duration     ┆ device │
            │ ---        ┆ ---         ┆ ---          ┆ ---    │
            │ date       ┆ str         ┆ duration[μs] ┆ str    │
            ╞════════════╪═════════════╪══════════════╪════════╡
            │ 2023-11-10 ┆ addititious ┆ 0µs          ┆        │
            │ 2023-11-11 ┆ addititious ┆ 0µs          ┆        │
            │ 2023-11-12 ┆ addititious ┆ 0µs          ┆        │
            │ 2023-11-13 ┆ addititious ┆ 0µs          ┆        │
            │ 2023-11-14 ┆ addititious ┆ 6s           ┆        │
            │ …          ┆ …           ┆ …            ┆ …      │
            │ 2024-03-06 ┆ xylometer   ┆ 53m 8s       ┆        │
            │ 2024-03-07 ┆ xylometer   ┆ 0µs          ┆        │
            │ 2024-03-08 ┆ xylometer   ┆ 30m 54s      ┆        │
            │ 2024-03-09 ┆ xylometer   ┆ 0µs          ┆        │
            │ 2024-03-10 ┆ xylometer   ┆ 0µs          ┆        │
            └────────────┴─────────────┴──────────────┴────────┘

        """
        sheet_df = self._read_sheet(0)
        total_usage_row_idx = sheet_df.with_row_index().filter(pl.col("App") == "Total Usage").item(0, 0)
        sheet_df = sheet_df.limit(total_usage_row_idx)
        device_dfs = []

        for (device_name,), device_df in sheet_df.group_by("Device"):
            device_df = (
                device_df
                .drop("Device")
                .transpose(include_header=True, column_names="App", header_name="date")
                .select(
                    pl.col("date").str.strptime(pt.Date, "%B %_d, %Y"),
                    pl.exclude("date").map_elements(self.parse_duration, pt.Duration)
                )
                .unpivot(index="date")
                .rename({"variable": "app", "value": "duration"})
                .with_columns(pl.lit(device_name).alias("device"))
            )
            device_dfs.append(device_df)

        return pl.concat(device_dfs)

    def get_usage_count_df(self) -> pl.DataFrame:
        """
        Return dataframe with app open counts

        Example:
            >>> from miscreaders.stayfree import StayfreeXlsReader
            >>> reader = StayfreeXlsReader(path_to_xls)
            >>> reader.get_usage_count_df()
            shape: (6_222, 4)
            ┌────────────┬─────────────┬───────┬────────┐
            │ date       ┆ app         ┆ count ┆ device │
            │ ---        ┆ ---         ┆ ---   ┆ ---    │
            │ date       ┆ str         ┆ i32   ┆ str    │
            ╞════════════╪═════════════╪═══════╪════════╡
            │ 2023-11-10 ┆ addititious ┆ 0     ┆        │
            │ 2023-11-11 ┆ addititious ┆ 0     ┆        │
            │ 2023-11-12 ┆ addititious ┆ 0     ┆        │
            │ 2023-11-13 ┆ addititious ┆ 0     ┆        │
            │ 2023-11-14 ┆ addititious ┆ 1     ┆        │
            │ …          ┆ …           ┆ …     ┆ …      │
            │ 2024-03-06 ┆ xylometer   ┆ 3     ┆        │
            │ 2024-03-07 ┆ xylometer   ┆ 0     ┆        │
            │ 2024-03-08 ┆ xylometer   ┆ 2     ┆        │
            │ 2024-03-09 ┆ xylometer   ┆ 0     ┆        │
            │ 2024-03-10 ┆ xylometer   ┆ 0     ┆        │
            └────────────┴─────────────┴───────┴────────┘
        """
        sheet_df = self._read_sheet(1)
        total_usage_row_idx = sheet_df.with_row_index().filter(pl.col("App") == "Total Usage").item(0, 0)
        sheet_df = sheet_df.limit(total_usage_row_idx)
        device_dfs = []

        for (device_name,), device_df in sheet_df.group_by("Device"):
            device_df = (
                device_df
                .drop("Device")
                .transpose(include_header=True, column_names="App", header_name="date")
                .select(
                    pl.col("date").str.strptime(pt.Date, "%B %_d, %Y"),
                    pl.exclude("date").cast(pt.Int32)
                )
                .unpivot(index="date")
                .rename({"variable": "app", "value": "count"})
                .with_columns(pl.lit(device_name).alias("device"))
            )
            device_dfs.append(device_df)

        return pl.concat(device_dfs)

    def get_device_unlocks_df(self) -> pl.DataFrame:
        """
        Return dataframe with device unlock counts

        Example:
            >>> from miscreaders.stayfree import StayfreeXlsReader
            >>> reader = StayfreeXlsReader(path_to_xls)
            >>> reader.get_device_unlocks_df()
            shape: (122, 2)
            ┌────────────┬───────┐
            │ date       ┆ count │
            │ ---        ┆ ---   │
            │ date       ┆ i32   │
            ╞════════════╪═══════╡
            │ 2023-11-10 ┆ 4     │
            │ 2023-11-11 ┆ 26    │
            │ 2023-11-12 ┆ 22    │
            │ 2023-11-13 ┆ 19    │
            │ 2023-11-14 ┆ 21    │
            │ …          ┆ …     │
            │ 2024-03-06 ┆ 39    │
            │ 2024-03-07 ┆ 35    │
            │ 2024-03-08 ┆ 26    │
            │ 2024-03-09 ┆ 10    │
            │ 2024-03-10 ┆ 0     │
            └────────────┴───────┘

        """
        sheet_df = self._read_sheet(2)
        return (
            sheet_df
            .limit(1)
            .transpose(include_header=True)[1:]
            .select(
                pl.selectors.by_index(0).str.strptime(pt.Date, "%B %_d, %Y").alias("date"),
                pl.selectors.by_index(1).cast(pt.Int32).alias("count")
            )
        )

    @staticmethod
    def parse_duration(text: str) -> timedelta:
        """Convert ``"1h 10m 26s"`` into ``datetime.timedelta``"""
        m = re.fullmatch(r"((?P<h>\d+)h)? ?((?P<m>\d+)m)? ?((?P<s>\d+)s)?", text)
        assert m is not None
        d = m.groupdict()
        return timedelta(hours=int(d.get("h") or 0), minutes=int(d.get("m") or 0), seconds=int(d.get("s") or 0))

    def _read_sheet(self, i: int) -> pl.DataFrame:
        workbook = xlrd.open_workbook(self.path)
        worksheet = workbook.sheet_by_index(i)
        df = pl.DataFrame({
            worksheet.cell_value(rowx=0, colx=col): [worksheet.cell_value(rowx=row, colx=col)
                                                     for row in range(1, worksheet.nrows)]
            for col in range(worksheet.ncols)
        }).rename({"": "App"}).drop(["Total Usage"])
        return df
