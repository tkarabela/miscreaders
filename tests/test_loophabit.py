from miscreaders.loophabit import LoophabitDbReader
import datetime


def test_get_repetition_df(datadir):
    reader = LoophabitDbReader(datadir / "test.db")
    df = reader.get_repetition_df()

    assert len(df) == 10
    assert df.columns == ['name', 'timestamp', 'value', 'notes']
    assert df.row(0) == ('a', datetime.date(2014, 2, 21), 2, '')
    assert df.row(-1) == ('a', datetime.date(2014, 3, 2), 2, '')


def test_habit_df(datadir):
    reader = LoophabitDbReader(datadir / "test.db")
    df = reader.get_habit_df()

    assert len(df) == 4
    assert df.columns == [
        'id',
        'archived',
        'color',
        'description',
        'freq_den',
        'freq_num',
        'highlight',
        'name',
        'position',
        'reminder_hour',
        'reminder_min',
        'reminder_days',
        'type',
        'target_type',
        'target_value',
        'unit',
        'question',
        'uuid'
    ]
    assert df.row(0) == (
        1,
        0,
        4,
        '',
        1,
        1,
        0,
        'a',
        1,
        None,
        None,
        0,
        0,
        0,
        0.0,
        '',
        '',
        'cwvnot6vdjvkwzu55s19gbgdeer84iz0'
    )
