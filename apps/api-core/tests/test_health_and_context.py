from fastapi.testclient import TestClient

from finops_api.main import app


def test_live_health() -> None:
    client = TestClient(app)
    response = client.get('/health/live')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_context_requires_org_header() -> None:
    client = TestClient(app)
    response = client.get('/v1/system/context')
    assert response.status_code == 422


def test_context_accepts_org_header() -> None:
    client = TestClient(app)
    response = client.get(
        '/v1/system/context',
        headers={'X-Org-Id': '00000000-0000-0000-0000-000000000001'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['data']['org_id'] == '00000000-0000-0000-0000-000000000001'
    assert body['meta']['org_id'] == '00000000-0000-0000-0000-000000000001'
