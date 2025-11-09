import sqlite3
from ..__version__ import __version__
import os

def create_database(db_path, unique_columns: tuple[str]):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create a table to store the version of Deepboard that created the DB
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Meta
    (
        key varchar(128) PRIMARY KEY,
        value varchar(128) NOT NULL
    );
    """)

    # Insert the version of Deepboard
    cursor.execute("""
    INSERT OR IGNORE INTO Meta (key, value) VALUES
    ('deepboard_version', ?);
    """, (__version__,))

    # Create Experiments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Experiments
        (
        run_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        experiment varchar(128) NOT NULL,
        config varchar(128),
        config_hash varchar(64),
        cli varchar(512),
        command varchar(256),
        comment TEXT,
        note TEXT DEFAULT '',
        tag TEXT DEFAULT '',
        color nchar(6),
        start DATETIME NOT NULL,
        status TEXT CHECK (status IN ('running', 'finished', 'failed')) DEFAULT 'running',
        commit_hash varchar(40),
        diff TEXT,
        hidden INTEGER NOT NULL DEFAULT 0
        );
    """)

    # Validate that unique_columns are valid
    valid_cols = (
        "experiment",
        "config",
        "config_hash",
        "cli",
        "command",
        "comment",
        "tag",
        "commit_hash",
        "diff")
    for col in unique_columns:
        if col not in valid_cols:
            # Remove the database to avoid incomplete DBs
            conn.close()
            os.remove(db_path)
            raise ValueError(f"Invalid unique column: {col}! Must be one of {{{', '.join(valid_cols)}}}")

    # Insert the unique columns
    cursor.execute("""
    INSERT OR IGNORE INTO Meta (key, value) VALUES
    ('unique_columns', ?);
    """, (", ".join(unique_columns), ))

    # Create Results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Results
        (
            id_ INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            metric varchar(128) NOT NULL,
            value,
            is_hparam INTEGER DEFAULT 0,
            FOREIGN KEY (run_id) REFERENCES Experiments(run_id)
        );
    """)

    # Create Logs table for scalar values
    # Wall time is in seconds
    # We must allow NULL values for the value column when the value is NaN
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Logs
    (
        id_ INTEGER PRIMARY KEY AUTOINCREMENT,
       run_id INTEGER NOT NULL,
       epoch INTEGER,
       step INTEGER NOT NULL,
       split varchar (128) NOT NULL,
       label varchar(128) NOT NULL,
       value REAL,
       wall_time REAL NOT NULL,
       run_rep INTEGER NOT NULL,
       FOREIGN KEY(run_id) REFERENCES Experiments(run_id)
    );
    """)

    # Create a ConfigFile table to store config file
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ConfigFile
    (
        run_id INTEGER NOT NULL PRIMARY KEY,
        file_content TEXT,
        FOREIGN KEY(run_id) REFERENCES Experiments(run_id)
    );
    """)

    # Create a Active Tag view to store active tags
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS ActiveTags AS
    SELECT DISTINCT tag
    FROM Experiments
    WHERE tag IS NOT NULL AND tag != '';
    """)

    # Create a ActiveColor view to store active colors
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS ActiveColors AS
    SELECT DISTINCT color
    FROM Experiments
    WHERE color IS NOT NULL AND color != '';
    """)

    # Create an Image table to store images
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Images
    (
        id_ INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        step INTEGER NOT NULL,
        epoch INTEGER,
        run_rep INTEGER NOT NULL,
        img_type varchar(64) NOT NULL, -- IMAGE or PLOT
        tag TEXT,
        image BLOB NOT NULL,
        FOREIGN KEY(run_id) REFERENCES Experiments(run_id)
    );
    """)
    # Create a table to store text data
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Fragments
    (
        id_ INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        step INTEGER NOT NULL,
        epoch INTEGER,
        run_rep INTEGER NOT NULL,
        fragment_type varchar(64) NOT NULL, -- RAW or HTML
        tag TEXT,
        fragment text NOT NULL,
        FOREIGN KEY(run_id) REFERENCES Experiments(run_id)
    );
    """)
    # Display Table
    # This table stores every column of Results, their order and whether they displayed or not
    # If order is Null, it means that the column is not displayed
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ResultDisplay
    (
        Name varchar(128) NOT NULL, display_order INTEGER, 
        alias varchar(128) NOT NULL, is_hparam INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Name)
    );
    """)  # We can put order to unique, because each NULL value will be unique

    # Add default columns
    cursor.execute("""
    INSERT
    OR IGNORE INTO ResultDisplay (Name, display_order, alias, is_hparam) VALUES
    ('run_id', 0, 'Run ID', 0),
    ('experiment', 1, 'Experiment', 0),
    ('tag', 2, 'Tag', 0),
    ('config', 3, 'Config', 0),
    ('config_hash', NULL, 'Config Hash', 0),
    ('cli', NULL, 'Cli', 0),
    ('command', NULL, 'Command', 0),
    ('comment', 4, 'Comment', 0),
    ('start', NULL, 'Start', 0),
    ('status', NULL, 'Status', 0),
    ('commit_hash', NULL, 'Commit', 0),
    ('diff', NULL, 'Diff', 0),
    ('hidden', NULL, 'Hidden', 0);
    """)

    # Create a trigger to add a new metric to the display table
    cursor.execute("""
                   CREATE TRIGGER IF NOT EXISTS after_result_insert
    AFTER INSERT ON Results
                   BEGIN
        -- Insert a row into ResultDisplay if the Name does not exist
        INSERT OR IGNORE INTO ResultDisplay (Name, display_order, alias, is_hparam)
                   SELECT NEW.metric,
                          COALESCE(MAX(display_order), 0) + 1,
                          NEW.metric,
                          NEW.is_hparam
                   FROM ResultDisplay;
                   END;
                   """)

    # Create index for speed
    command = ", ".join(unique_columns)
    cursor.execute(
        f"CREATE INDEX IF NOT EXISTS unique_exp ON Experiments({command});")
    conn.commit()
    conn.close()