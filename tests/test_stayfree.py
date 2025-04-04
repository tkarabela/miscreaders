from miscreaders.stayfree import StayfreeXlsReader
import datetime


def test_get_usage_time_df(datadir):
    reader = StayfreeXlsReader(datadir / "test.xls")
    df = reader.get_usage_time_df()

    assert len(df) == 6222
    assert df.columns == ['date', 'app', 'duration', 'device']
    assert df.row(0) == (datetime.date(2023, 11, 10), 'addititious', datetime.timedelta(0), '')
    assert df.row(-1) == (datetime.date(2024, 3, 10), 'xylometer', datetime.timedelta(0), '')
    assert df.get_column("duration").sum() == datetime.timedelta(days=14, seconds=10476)


def test_get_usage_count_df(datadir):
    reader = StayfreeXlsReader(datadir / "test.xls")
    df = reader.get_usage_count_df()

    assert len(df) == 6222
    assert df.columns == ['date', 'app', 'count', 'device']
    assert df.row(0) == (datetime.date(2023, 11, 10), 'addititious', 0, '')
    assert df.row(-1) == (datetime.date(2024, 3, 10), 'xylometer', 0, '')
    assert df.get_column("count").sum() == 8082


def test_get_device_unlocks_df(datadir):
    reader = StayfreeXlsReader(datadir / "test.xls")
    df = reader.get_device_unlocks_df()

    assert len(df) == 122
    assert df.columns == ['date', 'count']
    assert df.row(0) == (datetime.date(2023, 11, 10), 4)
    assert df.row(-1) == (datetime.date(2024, 3, 10), 0)
    assert df.get_column("count").sum() == 3898
