from fastapi.testclient import TestClient

from finops_api.main import app


def test_live_health() -> None:
    client = TestClient(app)
    response = client.get('/health/live')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_ready_health_has_component_checks() -> None:
    client = TestClient(app)
    response = client.get('/health/ready')
    assert response.status_code == 200
    body = response.json()
    assert body['status'] in {'ready', 'degraded'}
    assert 'checks' in body
    assert 'database' in body['checks']
    assert 'redis' in body['checks']


def test_context_requires_org_header() -> None:
    client = TestClient(app)
    response = client.get('/v1/system/context')
    assert response.status_code == 422


def test_context_accepts_org_header() -> None:
    client = TestClient(app)
    response = client.get(
        '/v1/system/context',
        headers={
            'X-Org-Id': '00000000-0000-0000-0000-000000000001',
            'X-Request-Id': 'req-test-id',
            'X-Trace-Id': 'trace-test-id',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['data']['org_id'] == '00000000-0000-0000-0000-000000000001'
    assert body['meta']['org_id'] == '00000000-0000-0000-0000-000000000001'
    assert response.headers['X-Request-Id'] == 'req-test-id'
    assert response.headers['X-Trace-Id'] == 'trace-test-id'
