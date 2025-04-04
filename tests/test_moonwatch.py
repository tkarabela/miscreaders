from miscreaders.moonwatch import MoonwatchLogReader, MoonwatchLogDirectoryReader
import datetime


def test_get_df1(datadir):
    reader = MoonwatchLogReader(datadir / "test1.jsonl")
    df = reader.get_df()

    assert len(df) == 5
    assert df.columns == ['type', 'time', 'duration', 'hostname', 'username', 'idle_for', 'process_path', 'tags']
    assert df.row(0) == (
    'ActiveWindowEvent', datetime.datetime(2025, 4, 2, 21, 40, 24, 543149), datetime.timedelta(seconds=15),
    'test-hostname', 'test-user', datetime.timedelta(seconds=82), 'C:\\test-program.exe', [])
    assert df.row(-1) == (
    'ActiveWindowEvent', datetime.datetime(2025, 4, 2, 0, 19, 27, 306595), datetime.timedelta(seconds=15),
    'test-hostname', 'test-user', datetime.timedelta(seconds=173), 'C:\\other-program.exe', ['tag-a', 'tag-b'])
    assert df.get_column("duration").sum() == datetime.timedelta(seconds=75)


def test_get_df2(datadir):
    reader = MoonwatchLogReader(datadir / "test2.jsonl.gz")
    df = reader.get_df()

    assert len(df) == 10
    assert df.columns == ['type', 'time', 'duration', 'hostname', 'username', 'idle_for', 'process_path', 'tags']
    assert df.row(0) == (
    'ActiveWindowEvent', datetime.datetime(2025, 4, 2, 0, 12, 57, 111274), datetime.timedelta(seconds=15),
    'test-hostname', 'test-user', datetime.timedelta(seconds=57), 'C:\\test-program.exe', [])
    assert df.row(-1) == (
    'ActiveWindowEvent', datetime.datetime(2025, 4, 2, 0, 10, 42, 68445), datetime.timedelta(seconds=15),
    'test-hostname', 'test-user', datetime.timedelta(seconds=170), 'C:\\test-program.exe', [])
    assert df.get_column("duration").sum() == datetime.timedelta(seconds=150)


def test_iter_dfs_in_dir(datadir):
    dfs = list(MoonwatchLogDirectoryReader(datadir).iter_dfs())
    assert len(dfs) == 2


def test_get_df_from_dir(datadir):
    df = MoonwatchLogDirectoryReader(datadir).get_df()
    assert len(df) == 15
    assert df.columns == ['type', 'time', 'duration', 'hostname', 'username', 'idle_for', 'process_path', 'tags']
    assert df.row(0) == (
    'ActiveWindowEvent', datetime.datetime(2025, 4, 2, 0, 12, 57, 111274), datetime.timedelta(seconds=15),
    'test-hostname', 'test-user', datetime.timedelta(seconds=57), 'C:\\test-program.exe', [])
    assert df.row(-1) == (
    'ActiveWindowEvent', datetime.datetime(2025, 4, 2, 0, 19, 27, 306595), datetime.timedelta(seconds=15),
    'test-hostname', 'test-user', datetime.timedelta(seconds=173), 'C:\\other-program.exe', ['tag-a', 'tag-b'])
    assert df.get_column("duration").sum() == datetime.timedelta(seconds=225)
