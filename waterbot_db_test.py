import os.path
import pytest
import time
import math
import waterbot_db

def setup_function(function):
    global conn
    conn = waterbot_db.get_db(":memory:")

def teardown_function(function):
    global conn
    if conn:
        conn.close()
        conn = None

def test_start_with_empty_tasks():
    assert(len(waterbot_db.tasks(conn)) == 0)

def test_task_does_not_exist():
    assert(len(waterbot_db.task(conn, 9999)) == 0)

def test_water_zone():
    before = math.floor(time.time())
    rowcount, task_id = waterbot_db.water_zone(conn, 78, 99)
    after = math.floor(time.time())

    assert(1 == rowcount)
    assert(1 == task_id)

    tasks = waterbot_db.task(conn, 1)
    assert(len(tasks) == 1)
    task = tasks[0]

    assert(task["zone_id"] == 78)
    assert(task["task_id"] == 1)
    assert(task["ts_submitted"] >= before)
    assert(task["ts_submitted"] <= after)
    assert(task["ts_started"] == None)
    assert(task["ts_terminated"] == None)
    assert(task["seconds"] == 99)

def test_terminate_task_sets_terminated_timestamp():
    waterbot_db.water_zone(conn, 6, 60)
    before = math.floor(time.time())
    waterbot_db.task_terminate(conn, 1)
    after = math.floor(time.time())
    task = waterbot_db.task(conn, 1)[0]

    assert(task["ts_terminated"] >= task["ts_submitted"])
    assert(task["ts_terminated"] >= before)
    assert(task["ts_terminated"] <= after)

def test_terminate_task_already_terminated_no_effect():
    waterbot_db.water_zone(conn, 6, 60)
    waterbot_db.task_terminate(conn, 1)
    assert(0 == waterbot_db.task_terminate(conn, 1))

def test_start_task_sets_started_timestamp():
    waterbot_db.water_zone(conn, 6, 60)
    before = math.floor(time.time())
    waterbot_db.task_start(conn, 1)
    after = math.floor(time.time())
    task = waterbot_db.task(conn, 1)[0]

    assert(task["ts_started"] >= task["ts_submitted"])
    assert(task["ts_started"] >= before)
    assert(task["ts_started"] <= after)

def test_start_task_already_started_no_effect():
    waterbot_db.water_zone(conn, 6, 60)
    waterbot_db.task_start(conn, 1)
    assert(0 == waterbot_db.task_start(conn, 1))

def test_start_task_already_terminated_no_effect():
    waterbot_db.water_zone(conn, 6, 60)
    waterbot_db.task_terminate(conn, 1)
    assert(0 == waterbot_db.task_start(conn, 1))

def test_pending_tasks_does_not_include_started_task():
    waterbot_db.water_zone(conn, 6, 60)
    waterbot_db.water_zone(conn, 7, 120)
    waterbot_db.water_zone(conn, 8, 180)
    waterbot_db.task_start(conn, 1)

    pending_tasks = waterbot_db.tasks_pending(conn)

    assert(len(pending_tasks) == 2)
    assert(pending_tasks[0]["zone_id"] == 7)
    assert(pending_tasks[0]["seconds"] == 120)
    assert(pending_tasks[1]["zone_id"] == 8)
    assert(pending_tasks[1]["seconds"] == 180)

def test_pending_tasks_does_not_include_terminated_task():
    waterbot_db.water_zone(conn, 6, 60)
    waterbot_db.water_zone(conn, 7, 120)
    waterbot_db.water_zone(conn, 8, 180)
    waterbot_db.task_terminate(conn, 1)

    pending_tasks = waterbot_db.tasks_pending(conn)

    assert(len(pending_tasks) == 2)
    assert(pending_tasks[0]["zone_id"] == 7)
    assert(pending_tasks[0]["seconds"] == 120)
    assert(pending_tasks[1]["zone_id"] == 8)
    assert(pending_tasks[1]["seconds"] == 180)

def test_tasks_includes_started_and_terminated_tasks():
    waterbot_db.water_zone(conn, 6, 60)
    waterbot_db.water_zone(conn, 7, 120)
    waterbot_db.water_zone(conn, 8, 180)
    waterbot_db.task_start(conn, 1)
    waterbot_db.task_terminate(conn, 2)

    pending_tasks = waterbot_db.tasks(conn)

    assert(len(pending_tasks) == 3)
    assert(pending_tasks[0]["zone_id"] == 6)
    assert(pending_tasks[1]["zone_id"] == 7)
    assert(pending_tasks[2]["zone_id"] == 8)
