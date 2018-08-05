import pytest
import json
import waterbot_api
import db

@pytest.fixture
def client():
    waterbot_api.app.config['TESTING'] = True
    client = waterbot_api.app.test_client()
    yield client

def test_index_get(client):
    rv = client.get('/')
    assert b'<title>Waterbot</title>' in rv.data

def test_config_get(client):
    rv = client.get('/api/v0/config')
    response = json.loads(rv.data)
    assert("common_gpio" in response)

def test_config_post(client):
    rv = client.post('/api/v0/config')
    response = json.loads(rv.data)
    assert("common_gpio" in response)

def test_zones_get(client):
    rv = client.get('/api/v0/zones')
    response = json.loads(rv.data)
    assert(response["1"]["name"] == "Example Zone 1")

def test_zones_post(client):
    rv = client.post('/api/v0/zones')
    response = json.loads(rv.data)
    assert(response["1"]["name"] == "Example Zone 1")

def test_zone_get(client):
    rv = client.get('/api/v0/zone/2')
    response = json.loads(rv.data)
    assert(response["name"] == "Example Zone 2")
    assert(response["seconds"] == 1200)

def test_zone_get(client):
    rv = client.post('/api/v0/zone/3')
    response = json.loads(rv.data)
    assert(response["name"] == "Example Zone 3")
    assert(response["seconds"] == 1800)

def test_tasks_get(client, mocker):
    stub_get_db = mocker.patch("waterbot_api.get_db")
    stub_tasks = mocker.patch("db.tasks")
    waterbot_api.get_db.return_value = "foo"
    db.tasks.return_value = [{"key":"value"}]

    rv = client.get('/api/v0/tasks')
    response = json.loads(rv.data)
    assert(response[0]["key"] == "value")
    stub_tasks.assert_called_once_with("foo")

def test_tasks_post(client, mocker):
    stub_get_db = mocker.patch("waterbot_api.get_db")
    stub_tasks = mocker.patch("db.tasks")
    waterbot_api.get_db.return_value = "foo"
    db.tasks.return_value = [{"key":"value"}]

    rv = client.get('/api/v0/tasks')
    response = json.loads(rv.data)
    assert(response[0]["key"] == "value")
    stub_tasks.assert_called_once_with("foo")

def test_task_get(client, mocker):
    stub_get_db = mocker.patch("waterbot_api.get_db")
    stub_task = mocker.patch("db.task")
    waterbot_api.get_db.return_value = "foo"
    db.task.return_value = [{"key":"value"}]

    rv = client.get('/api/v0/task/17')
    response = json.loads(rv.data)
    assert(response["key"] == "value")
    stub_task.assert_called_once_with("foo", 17)

def test_task_post(client, mocker):
    stub_get_db = mocker.patch("waterbot_api.get_db")
    stub_task = mocker.patch("db.task")
    waterbot_api.get_db.return_value = "foo"
    db.task.return_value = [{"key":"value"}]

    rv = client.post('/api/v0/task/17')
    response = json.loads(rv.data)

    assert(response["key"] == "value")
    stub_task.assert_called_once_with("foo", 17)

def test_task_not_found(client, mocker):
    stub_get_db = mocker.patch("waterbot_api.get_db")
    stub_task = mocker.patch("db.task")
    waterbot_api.get_db.return_value = "foo"
    db.task.return_value = []

    rv = client.post('/api/v0/task/17')
    response = json.loads(rv.data)

    assert("not found" in response["error"])
    stub_task.assert_called_once_with("foo", 17)

def test_cancel_task(client, mocker):
    stub_get_db = mocker.patch("waterbot_api.get_db")
    stub_cancel_task = mocker.patch("db.task_terminate")
    stub_task = mocker.patch("db.task")
    waterbot_api.get_db.return_value = "foo"
    db.task_terminate.return_value = 1
    db.task.return_value = [{"task_id":17}]

    rv = client.post('/api/v0/cancel-task/17')
    response = json.loads(rv.data)

    assert(response["task_id"] == 17)
    stub_cancel_task.assert_called_once_with("foo", 17)
    stub_task.assert_called_once_with("foo", 17)

def test_cancel_task_with_no_effect(client, mocker):
    stub_get_db = mocker.patch("waterbot_api.get_db")
    stub_cancel_task = mocker.patch("db.task_terminate")
    waterbot_api.get_db.return_value = "foo"
    db.task_terminate.return_value = 0

    rv = client.post('/api/v0/cancel-task/17')
    response = json.loads(rv.data)

    assert("not changed" in response["error"])
    stub_cancel_task.assert_called_once_with("foo", 17)

def test_water_zone(client, mocker):
    stub_get_db = mocker.patch("waterbot_api.get_db")
    stub_water_zone = mocker.patch("db.water_zone")
    stub_task = mocker.patch("db.task")
    waterbot_api.get_db.return_value = "foo"
    db.water_zone.return_value = (1, 99)
    db.task.return_value = [{"task_id":99}]

    rv = client.post('/api/v0/water-zone/4/99')
    response = json.loads(rv.data)

    assert(response["task_id"] == 99)
    stub_water_zone.assert_called_once_with("foo", 4, 99)
    stub_task.assert_called_once_with("foo", 99)

def test_water_zone_error(client, mocker):
    stub_get_db = mocker.patch("waterbot_api.get_db")
    stub_water_zone = mocker.patch("db.water_zone")
    waterbot_api.get_db.return_value = "foo"
    db.water_zone.return_value = (0, None)

    rv = client.post('/api/v0/water-zone/4/99')
    response = json.loads(rv.data)

    assert("Failed to create task" in response["error"])
    stub_water_zone.assert_called_once_with("foo", 4, 99)

def test_water_zone_does_not_exist(client, mocker):
    rv = client.post('/api/v0/water-zone/5/99')
    response = json.loads(rv.data)

    assert("not known" in response["error"])

def test_water_zone_too_short(client, mocker):
    rv = client.post('/api/v0/water-zone/4/0')
    response = json.loads(rv.data)

    assert("less than one second" in response["error"])

def test_water_zone_too_long(client, mocker):
    rv = client.post('/api/v0/water-zone/4/3601')
    response = json.loads(rv.data)

    assert("longer than one hour" in response["error"])
