import pytest
import json
import waterbot_db
import waterbot_web

@pytest.yield_fixture(scope="function")
def client():
    waterbot_web.app.config['TESTING'] = True
    ctx = waterbot_web.app.app_context()
    ctx.push()

    client = waterbot_web.app.test_client()
    client.post('/api/v0/water-zone/4/77')
    yield client

    ctx.pop()

def test_index_get(client):
    rv = client.get('/')
    assert(rv.status_code == 200)
    assert('<title>Waterbot</title>' in rv.data.decode('utf-8'))

def test_config_get(client):
    rv = client.get('/api/v0/config')
    assert(rv.status_code == 200)
    response = json.loads(rv.data.decode('utf-8'))
    assert("common_gpio" in response)

def test_config_post(client):
    rv = client.post('/api/v0/config')
    assert(rv.status_code == 200)
    response = json.loads(rv.data.decode('utf-8'))
    assert("common_gpio" in response)

def test_zones_get(client):
    rv = client.get('/api/v0/zones')
    assert(rv.status_code == 200)
    response = json.loads(rv.data.decode('utf-8'))
    assert(response["1"]["name"] == "Example Zone 1")

def test_zones_post(client):
    rv = client.post('/api/v0/zones')
    assert(rv.status_code == 200)
    response = json.loads(rv.data.decode('utf-8'))
    assert(response["1"]["name"] == "Example Zone 1")

def test_zone_get(client):
    rv = client.get('/api/v0/zone/2')
    assert(rv.status_code == 200)
    response = json.loads(rv.data.decode('utf-8'))
    assert(response["name"] == "Example Zone 2")
    assert(response["seconds"] == 1200)

def test_zone_post(client):
    rv = client.post('/api/v0/zone/3')
    assert(rv.status_code == 200)
    response = json.loads(rv.data.decode('utf-8'))
    assert(response["name"] == "Example Zone 3")
    assert(response["seconds"] == 1800)

def test_zone_not_found(client):
    rv = client.get('/api/v0/zone/999')
    assert(rv.status_code == 404)
    response = json.loads(rv.data.decode('utf-8'))
    assert("error" in response)

def test_tasks_get(client):
    rv = client.get('/api/v0/tasks')
    assert(rv.status_code == 200)
    response = json.loads(rv.data.decode('utf-8'))
    assert(response[0]["zone_id"] == 4)
    assert(response[0]["seconds"] == 77)

def test_tasks_post(client):
    rv = client.post('/api/v0/tasks')
    assert(rv.status_code == 200)
    response = json.loads(rv.data.decode('utf-8'))
    assert(response[0]["zone_id"] == 4)
    assert(response[0]["seconds"] == 77)

def test_task_get(client):
    rv = client.get('/api/v0/task/1')
    assert(rv.status_code == 200)
    response = json.loads(rv.data.decode('utf-8'))
    assert(response["zone_id"] == 4)
    assert(response["seconds"] == 77)

def test_task_post(client):
    rv = client.post('/api/v0/task/1')
    assert(rv.status_code == 200)
    response = json.loads(rv.data.decode('utf-8'))
    assert(response["zone_id"] == 4)
    assert(response["seconds"] == 77)

def test_task_not_found(client):
    rv = client.get('/api/v0/task/999')
    assert(rv.status_code == 404)
    response = json.loads(rv.data.decode('utf-8'))
    assert("error" in response)

def test_cancel_task(client):
    rv = client.post('/api/v0/cancel-task/1')
    assert(rv.status_code == 200)
    response = json.loads(rv.data.decode('utf-8'))
    assert(response["zone_id"] == 4)
    assert(response["seconds"] == 77)
    assert(response["ts_terminated"] > 0)

def test_cancel_task_not_found(client):
    rv = client.post('/api/v0/cancel-task/999')
    assert(rv.status_code == 404)
    response = json.loads(rv.data.decode('utf-8'))
    assert("error" in response)

def test_cancel_task_already_canceled(client):
    client.post('/api/v0/cancel-task/1')
    rv = client.post('/api/v0/cancel-task/1')
    assert(rv.status_code == 409)
    response = json.loads(rv.data.decode('utf-8'))
    assert("error" in response)

def test_water_zone(client):
    rv = client.post('/api/v0/water-zone/3/33')
    assert(rv.status_code == 201)
    response = json.loads(rv.data.decode('utf-8'))
    assert(response["zone_id"] == 3)
    assert(response["seconds"] == 33)

def test_water_zone_not_created(client, mocker):
    mocker.patch("waterbot_db.water_zone")
    waterbot_db.water_zone.return_value = (0, None)
    rv = client.post('/api/v0/water-zone/3/33')
    assert(rv.status_code == 500)
    response = json.loads(rv.data.decode('utf-8'))
    assert("error" in response)

def test_water_zone_does_not_exist(client):
    rv = client.post('/api/v0/water-zone/5/99')
    assert(rv.status_code == 404)
    response = json.loads(rv.data.decode('utf-8'))
    assert("error" in response)

def test_water_zone_too_short(client):
    rv = client.post('/api/v0/water-zone/4/0')
    assert(rv.status_code == 400)
    response = json.loads(rv.data.decode('utf-8'))
    assert("error" in response)

def test_water_zone_too_long(client):
    rv = client.post('/api/v0/water-zone/4/3601')
    assert(rv.status_code == 400)
    response = json.loads(rv.data.decode('utf-8'))
    assert("error" in response)
