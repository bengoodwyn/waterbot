import sqlite3

schema = """
CREATE TABLE IF NOT EXISTS tasks (
task_id INTEGER PRIMARY KEY AUTOINCREMENT,
ts_submitted INTEGER DEFAULT (cast(strftime('%s','now') as int)),
ts_started INTEGER,
ts_terminated INTEGER,
zone_id INTEGER NOT NULL,
seconds TINYINT NOT NULL
);
"""

__task_fields = [ "task_id", "zone_id", "ts_submitted", "ts_started", "ts_terminated", "seconds" ]

def __task_row_to_dict(row):
    result = dict()
    for x in range(0, len(__task_fields)):
        result[__task_fields[x]] = row[x]
    return result

def get_db(path):
    db = sqlite3.connect(path)
    db.execute(schema)
    return db

def tasks(conn):
    c = conn.cursor()
    c.execute("SELECT {} FROM tasks;".format(','.join(__task_fields)))
    return list(map(__task_row_to_dict, c.fetchall()))

def tasks_pending(conn):
    c = conn.cursor()
    c.execute("SELECT {} FROM tasks WHERE ts_started IS NULL AND ts_terminated IS NULL;".format(','.join(__task_fields)))
    return list(map(__task_row_to_dict, c.fetchall()))

def task(conn, task_id):
    c = conn.cursor()
    c.execute("SELECT {} FROM tasks WHERE task_id=?;".format(','.join(__task_fields)), (task_id,))
    return list(map(__task_row_to_dict, c.fetchall()))

def task_start(conn, task_id):
    c = conn.cursor()
    results = c.execute("UPDATE tasks SET ts_started=(cast(strftime('%s','now') as int)) WHERE task_id=? AND ts_started IS NULL AND ts_terminated IS NULL;", (task_id,))
    conn.commit()
    return results.rowcount

def task_terminate(conn, task_id):
    c = conn.cursor()
    results = c.execute("UPDATE tasks SET ts_terminated=(cast(strftime('%s','now') as int)) WHERE task_id=? AND ts_terminated IS NULL;", (task_id,))
    conn.commit()
    return results.rowcount

def water_zone(conn, zone_id, seconds):
    c = conn.cursor()
    results = c.execute("INSERT INTO tasks (zone_id, seconds) VALUES (?,?);", (zone_id,seconds))
    conn.commit()
    return results.rowcount, results.lastrowid if 1==results.rowcount else None
