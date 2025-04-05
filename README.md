[![CI - build](https://img.shields.io/github/actions/workflow/status/tkarabela/miscreaders/main.yml?branch=master)](https://github.com/tkarabela/miscreaders/actions)
[![CI - coverage](https://img.shields.io/codecov/c/github/tkarabela/miscreaders)](https://app.codecov.io/github/tkarabela/miscreaders)
[![MyPy & Ruffle checked](https://img.shields.io/badge/MyPy%20%26%20Ruffle-checked-blue?style=flat)](https://github.com/tkarabela/pysubs2/actions)

# miscreaders

This library provides parsers for output of various programs.

To learn more, please [see the documentation](https://miscreaders.readthedocs.io).

## List of readers

| Program                                                   | Description                                        |
|-----------------------------------------------------------|----------------------------------------------------|
| [StayFree](https://stayfreeapps.com/)                     | Device usage statistics (mobile, desktop, browser) |
| [Loop Habit Tracker](https://github.com/iSoron/uhabits)   | Habit tracker (Android)                            |
| [Moonwatch.rs](https://github.com/tkarabela/moonwatch-rs) | Privacy-focused device usage statistics (desktop)  |

## Installation

```bash
uv pip install "git+https://github.com/tkarabela/miscreaders"
```

## Example

```python
>>> from miscreaders.stayfree import StayfreeXlsReader
>>> reader = StayfreeXlsReader("StayFree Export - Total Usage - 8_9_24.xls")
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
```

## License

MIT, see [LICENSE.txt](./LICENSE.txt).
