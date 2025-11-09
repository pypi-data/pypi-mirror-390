import sqlite3
from typing import Union
from pathlib import PurePath
class Cursor:
    def __init__(self, db_path: Union[str, PurePath], format_as_dict: bool = False):
        self.db_path = db_path
        self.format_as_dict = format_as_dict

    def __enter__(self):
        self._conn = sqlite3.connect(self.db_path)
        if self.format_as_dict:
            self._conn.row_factory = sqlite3.Row
        self._cursor = self._conn.cursor()
        return self._cursor

    def __exit__(self, exc_type, exc_value, traceback):
        """Commits changes if no exception occurred, then closes the connection."""
        if self._conn:
            if exc_type is None:  # No exceptions, commit changes
                self._conn.commit()
            self._conn.close()