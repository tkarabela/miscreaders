"""
StayFree
========

StayFree is a productivity app for mobile, desktop and web.

References:
    - https://stayfreeapps.com
    - https://userguide.stayfreeapps.com/settings/backup-restore

Note:
    Tested with version 18.8.4 of the Android app.

.. autoclass:: StayfreeXlsReader
    :members:

.. autoclass:: StayfreeBackupReader
    :members:

"""

from .xls_reader import StayfreeXlsReader
from .backup_reader import StayfreeBackupReader

__all__ = [
    "StayfreeXlsReader",
    "StayfreeBackupReader",
]
