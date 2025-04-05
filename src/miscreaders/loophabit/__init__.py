"""
Loop Habit Tracker
==================

Loop Habit Tracker is an open-source Android app for tracking habits.

References:
    - https://github.com/iSoron/uhabits
    - https://play.google.com/store/apps/details?id=org.isoron.uhabits

.. autoclass:: LoophabitDbReader
    :members:

.. autoclass:: HabitType
    :members:

.. autoclass:: EntryValue
    :members:

.. invisible-code-block: python

    path_to_db = "tests/test_loophabit/test.db"

"""

from contextlib import closing
from pathlib import Path
import sqlite3
import polars as pl
import polars.datatypes as pt

from ..common import PathOrStr


class EntryValue:
    """
    Values in column ``value`` in repetition table for habits of type ``HabitType.YES_NO``

    Attributes:
        SKIP: Value indicating that the habit is not applicable for this timestamp.
        YES_MANUAL: Value indicating that the user has performed the habit at this timestamp.
        YES_AUTO: Value indicating that the user did not perform the habit, but they were not
            expected to, because of the frequency of the habit.
        NO: Value indicating that the user did not perform the habit, even though they were
            expected to perform it.
        UNKNOWN: Value indicating that no data is available for the given timestamp.

    References:
        - https://github.com/iSoron/uhabits/blob/897a2365015d21e64dae0a0a4d0b33e79c31cfda/uhabits-core/src/jvmMain/java/org/isoron/uhabits/core/models/Entry.kt#L26
    """
    SKIP = 3
    YES_MANUAL = 2
    YES_AUTO = 1
    NO = 0
    UNKNOWN = -1


class HabitType:
    """
    Values in column ``type`` in habit table

    Attributes:
        YES_NO: Habit value has interpretation per :py:class:`EntryValue`
        NUMERICAL: Habit value has numerical interpretation

    References:
        - https://github.com/iSoron/uhabits/blob/897a2365015d21e64dae0a0a4d0b33e79c31cfda/uhabits-core/src/jvmMain/java/org/isoron/uhabits/core/models/HabitType.kt#L5
    """
    YES_NO = 0
    NUMERICAL = 1


class LoophabitDbReader:
    """
    Reader for SQLite database exported from Loop Habit Tracker

    """
    def __init__(self, db_path: PathOrStr) -> None:
        """
        Args:
            db_path: Path to exported database
        """
        self.db_path = Path(db_path)

    def get_habit_df(self) -> pl.DataFrame:
        """
        Return dataframe with habit definition

        See Also:
            :py:class:`HabitType` for meaning of the ``type`` column

        Example:
            >>> from miscreaders.loophabit import LoophabitDbReader
            >>> reader = LoophabitDbReader(path_to_db)
            >>> reader.get_habit_df().head(2)
            shape: (2, 18)
            ┌─────┬──────────┬───────┬─────────────┬───┬──────────────┬──────┬──────────┬──────────────────────┐
            │ id  ┆ archived ┆ color ┆ description ┆ … ┆ target_value ┆ unit ┆ question ┆ uuid                 │
            │ --- ┆ ---      ┆ ---   ┆ ---         ┆   ┆ ---          ┆ ---  ┆ ---      ┆ ---                  │
            │ i64 ┆ i64      ┆ i64   ┆ str         ┆   ┆ f64          ┆ str  ┆ str      ┆ str                  │
            ╞═════╪══════════╪═══════╪═════════════╪═══╪══════════════╪══════╪══════════╪══════════════════════╡
            │ 1   ┆ 0        ┆ 4     ┆             ┆ … ┆ 0.0          ┆      ┆          ┆ cwvnot6vdjvkwzu55s19 │
            │     ┆          ┆       ┆             ┆   ┆              ┆      ┆          ┆ gbgdeer84i…          │
            │ 2   ┆ 0        ┆ 0     ┆             ┆ … ┆ 0.0          ┆      ┆          ┆ owhf7kceexi8cghlbqks │
            │     ┆          ┆       ┆             ┆   ┆              ┆      ┆          ┆ 687kj3w8j9…          │
            └─────┴──────────┴───────┴─────────────┴───┴──────────────┴──────┴──────────┴──────────────────────┘
        """
        with closing(self.get_connection()) as connection:
            return pl.read_database("SELECT * FROM Habits", connection)

    def get_repetition_df(self) -> pl.DataFrame:
        """
        Return dataframe with daily data for habits

        See Also:
            :py:class:`EntryValue` for meaning of the ``value`` column

        Example:
            >>> from miscreaders.loophabit import LoophabitDbReader
            >>> reader = LoophabitDbReader(path_to_db)
            >>> reader.get_repetition_df()
            shape: (10, 4)
            ┌──────┬────────────┬───────┬───────┐
            │ name ┆ timestamp  ┆ value ┆ notes │
            │ ---  ┆ ---        ┆ ---   ┆ ---   │
            │ enum ┆ date       ┆ i64   ┆ str   │
            ╞══════╪════════════╪═══════╪═══════╡
            │ a    ┆ 2014-02-21 ┆ 2     ┆       │
            │ b    ┆ 2014-02-22 ┆ 2     ┆       │
            │ c    ┆ 2014-02-23 ┆ 2     ┆       │
            │ d    ┆ 2014-02-24 ┆ 2     ┆       │
            │ a    ┆ 2014-02-25 ┆ 0     ┆       │
            │ a    ┆ 2014-02-26 ┆ 2     ┆       │
            │ a    ┆ 2014-02-27 ┆ 2     ┆       │
            │ a    ┆ 2014-02-28 ┆ 2     ┆       │
            │ a    ┆ 2014-03-01 ┆ 2     ┆       │
            │ a    ┆ 2014-03-02 ┆ 2     ┆       │
            └──────┴────────────┴───────┴───────┘
        """
        with (closing(self.get_connection()) as connection):
            habit_df = pl.read_database("SELECT id, name FROM Habits", connection)
            habit_name_enum = pt.Enum(habit_df.get_column("name"))
            return (
                pl.read_database("""
                    SELECT H.name, R.timestamp, R.value, R.notes
                    FROM Repetitions R
                    JOIN Habits H ON R.habit = H.id
                """, connection, schema_overrides={"name": habit_name_enum})
                .with_columns(pl.from_epoch("timestamp", "ms").cast(pt.Date))
            )

    def get_connection(self) -> sqlite3.Connection:
        """
        Return read-only connection to the database
        """
        return sqlite3.Connection(f"file:{self.db_path}?mode=ro", uri=True)
