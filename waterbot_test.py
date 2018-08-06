import pytest
import os
import time
from mock import call
from waterbot import *
import waterbot_api

@pytest.fixture
def api():
    return waterbot_api.WaterbotApi(config_filename="test_config.json", database_filename=":memory:")

@pytest.fixture
def stub_system(mocker):
    stub = mocker.patch("os.system")
    os.system.return_value = 0
    return stub

def test_reset_gpio(api, stub_system):
    reset_gpio(api)
    stub_system.assert_has_calls([
        call("gpio mode 0 out"),
        call("gpio write 0 1"),
        call("gpio mode 1 out"),
        call("gpio write 1 1"),
        call("gpio mode 2 out"),
        call("gpio write 2 1"),
        call("gpio mode 3 out"),
        call("gpio write 3 1"),
        call("gpio mode 4 out"),
        call("gpio write 4 1"),
    ])

def test_start_watering(api, stub_system):
    task = api.water_zone(3, 100)
    result = start_watering(api, task)
    assert(result == 1)
    stub_system.asset_has_calls([
        call("gpio write 0 0"),
        call("gpio write 3 0")
    ])
    task = api.task(1)
    assert(task["ts_started"] > 0)

def test_stop_watering(api, stub_system):
    task = api.water_zone(3, 100)
    api.start_task(1)
    stop_watering(api, task)
    stub_system.asset_has_calls([
        call("gpio write 0 1"),
        call("gpio write 3 1")
    ])
    task = api.task(1)
    assert(task["ts_terminated"] > 0)

def test_stop_watering_if_canceled(api, stub_system):
    task = api.water_zone(3, 100)
    api.start_task(1)
    api.terminate_task(1)
    stop_watering(api, task)
    stub_system.asset_has_calls([
        call("gpio write 0 1"),
        call("gpio write 3 1")
    ])
    task = api.task(1)
    assert(task["ts_terminated"] > 0)

def test_watered_long_enough(mocker):
    task = {"ts_started":100, "seconds":5}

    stub = mocker.patch("time.time")

    time.time.return_value = 104
    assert(has_watered_long_enough(task) == False)

    time.time.return_value = 105
    assert(has_watered_long_enough(task) == True)

    time.time.return_value = 106
    assert(has_watered_long_enough(task) == True)

def test_watering_canceled():
    active_task = {"ts_terminated":None}
    assert(was_watering_canceled(active_task) == False)

    canceled_task = {"ts_terminated":7}
    assert(was_watering_canceled(canceled_task) == True)

def test_continue_task_until_time_expires(api, stub_system, mocker):
    stub = mocker.patch("time.time")

    task = api.water_zone(3, 100)
    task_id = task["task_id"]

    start_watering(api, task)
    task = api.task(1)

    time.time.return_value = task["ts_started"] + 99
    result = continue_task(api, task_id)
    assert(result == task_id)
 
    time.time.return_value = task["ts_started"] + 100
    result = continue_task(api, task_id)
    assert(result == None)

def test_continue_task_until_canceled_before_time_expires(api, stub_system, mocker):
    stub = mocker.patch("time.time")

    task = api.water_zone(3, 100)
    task_id = task["task_id"]

    start_watering(api, task)
    task = api.task(1)

    time.time.return_value = task["ts_started"] + 1
    result = continue_task(api, task_id)
    assert(result == task_id)

    api.terminate_task(1)

    time.time.return_value = task["ts_started"] + 2
    result = continue_task(api, task_id)
    assert(result == None)

def test_start_new_task_with_nothing_pending(api):
    assert(start_new_task(api) == None)

def test_start_new_task_with_something_pending(api, stub_system):
    api.water_zone(2, 22)
    assert(start_new_task(api) == 1)
    stub_system.asset_has_calls([
        call("gpio write 0 0"),
        call("gpio write 2 0")
    ])

def test_waterbot_stay_idle(api):
    assert(poll_waterbot(api, None) == None)

def test_waterbot_start_new_task(api, stub_system):
    api.water_zone(1, 11)
    assert(poll_waterbot(api, None) == 1)
    stub_system.asset_has_calls([
        call("gpio write 0 0"),
        call("gpio write 1 0")
    ])

def test_waterbot_continue_task(api, stub_system):
    api.water_zone(1, 3600)
    api.start_task(1)
    assert(poll_waterbot(api, 1) == 1)
    stub_system.asset_has_calls([
        call("gpio write 0 0"),
        call("gpio write 1 0")
    ])

def test_waterbot_canceled_task(api, stub_system):
    api.water_zone(1, 3600)
    api.start_task(1)
    api.terminate_task(1)
    assert(poll_waterbot(api, 1) == None)
    stub_system.asset_has_calls([
        call("gpio write 0 1"),
        call("gpio write 1 1")
    ])

def test_waterbot_completed_task(api, stub_system, mocker):
    api.water_zone(1, 3600)
    api.start_task(1)
    task = api.task(1)
    stub = mocker.patch("time.time")
    time.time.return_value = task["ts_started"] + 3600
    assert(poll_waterbot(api, 1) == None)
    stub_system.asset_has_calls([
        call("gpio write 0 1"),
        call("gpio write 1 1")
    ])
