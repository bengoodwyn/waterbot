import pytest
import waterbot_api
import db

@pytest.fixture
def api():
    yield waterbot_api.WaterbotApi(config_filename='.config.json', database_filename=':memory:')

def test_config(api):
    assert("common_gpio" in api.config)

def test_zones(api):
    assert(api.zones()["1"]["name"] == "Example Zone 1")

def test_zone(api):
    zone = api.zone(2)
    assert(zone["name"] == "Example Zone 2")
    assert(zone["seconds"] == 1200)

def test_tasks(api):
    api.water_zone(1, 120)
    tasks = api.tasks()

    assert(len(tasks)==1)
    assert(tasks[0]["zone_id"] == 1)
    assert(tasks[0]["seconds"] == 120)

def test_task(api):
    api.water_zone(2, 240)
    task = api.task(1)

    assert(task["zone_id"] == 2)
    assert(task["seconds"] == 240)

def test_task_not_found(api):
    with pytest.raises(waterbot_api.TaskNotFound):
        api.task(99)

def test_cancel_task(api):
    created_task = api.water_zone(3, 360)
    canceled_task = api.terminate_task(created_task["task_id"])

    created_task["ts_terminated"] = canceled_task["ts_terminated"]
    assert(created_task == canceled_task)

def test_cancel_task_already_canceled(api):
    created_task = api.water_zone(4, 480)
    canceled_task = api.terminate_task(created_task["task_id"])

    with pytest.raises(waterbot_api.TaskAlreadyTerminated):
        api.terminate_task(created_task["task_id"])

def test_water_zone(api):
    task = api.water_zone(2, 600)

    assert(task["task_id"] == 1)
    assert(task["zone_id"] == 2)
    assert(task["seconds"] == 600)
    assert(task["ts_submitted"] > 0)
    assert(task["ts_started"] == None)
    assert(task["ts_terminated"] == None)

def test_water_zone_error(api, mocker):
    mocker.patch("db.water_zone")
    db.water_zone.return_value = (0, None)
    with pytest.raises(waterbot_api.TaskNotCreated):
        api.water_zone(2, 600)

def test_water_zone_does_not_exist(api):
    with pytest.raises(waterbot_api.ZoneNotFound):
        api.water_zone(999, 600)

def test_water_zone_too_short(api):
    with pytest.raises(waterbot_api.TooShort):
        api.water_zone(1, 0)

def test_water_zone_too_long(api):
    with pytest.raises(waterbot_api.TooLong):
        api.water_zone(1, 3601)
