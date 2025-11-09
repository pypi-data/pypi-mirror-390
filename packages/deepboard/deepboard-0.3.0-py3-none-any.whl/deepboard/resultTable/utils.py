import sqlite3
from datetime import datetime, date
from typing import *
import subprocess

def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()

def adapt_datetime_iso(val):
    """Adapt datetime.datetime to timezone-naive ISO 8601 date."""
    return val.isoformat()

sqlite3.register_adapter(datetime.date, adapt_date_iso)
sqlite3.register_adapter(datetime, adapt_datetime_iso)

def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return date.fromisoformat(val.decode())

def convert_datetime(val):
    """Convert ISO 8601 datetime to datetime.datetime object."""
    return datetime.fromisoformat(val.decode())

sqlite3.register_converter("date", convert_date)
sqlite3.register_converter("datetime", convert_datetime)

def get_last_commit() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_diff() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None