import pytest

import waterbot

@pytest.fixture
def client():
    waterbot.app.config['TESTING'] = True
    client = waterbot.app.test_client()

    yield client

def test_empty_db(client):
    rv = client.get('/')
    assert b'<title>Waterbot</title>' in rv.data
