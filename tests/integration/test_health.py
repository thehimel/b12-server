from urls import URL_HEALTH


def test_health_returns_200(client):
    response = client.get(URL_HEALTH)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
