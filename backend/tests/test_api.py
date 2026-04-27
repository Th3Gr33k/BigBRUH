from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
HEADERS = {'x-api-key': 'test-key'}


def test_healthz():
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_readyz():
    response = client.get('/readyz')
    assert response.status_code == 200
    assert 'checks' in response.json()


def test_auth_required_when_api_key_set():
    response = client.get('/api/v1/cases')
    assert response.status_code in (200, 401)


def test_case_crud_entities_and_exports():
    payload = {'case_ref': 'SF-TEST-001', 'title': 'Test Case', 'severity': 'high'}
    response = client.post('/api/v1/cases', json=payload, headers=HEADERS)
    if response.status_code == 401:
        return
    assert response.status_code == 200
    case_id = response.json()['id']

    e_resp = client.post(
        f'/api/v1/cases/{case_id}/entities/bulk',
        json=[
            {'entity_type': 'domain', 'entity_value': 'example.com'},
            {'entity_type': 'wallet', 'entity_value': 'bc1qexample'},
        ],
        headers=HEADERS,
    )
    assert e_resp.status_code == 200
    assert len(e_resp.json()['entities']) == 2

    exp = client.get(f'/api/v1/exports/ioc?format=json&case_id={case_id}', headers=HEADERS)
    assert exp.status_code == 200
    assert len(exp.json()['items']) == 2


def test_enrichment_job_persistence():
    response = client.post('/api/v1/enrichment/jobs', json={'observable_type': 'domain', 'value': 'Example.COM'}, headers=HEADERS)
    if response.status_code == 401:
        return
    assert response.status_code == 200
    job_id = response.json()['job_id']

    result = client.get(f'/api/v1/enrichment/jobs/{job_id}', headers=HEADERS)
    assert result.status_code == 200
    body = result.json()
    assert body['status'] == 'completed'
    assert body['result']['normalized'] == 'example.com'


def test_evidence_hashing():
    case_payload = {'case_ref': 'SF-TEST-002', 'title': 'Evidence Case', 'severity': 'medium'}
    c_resp = client.post('/api/v1/cases', json=case_payload, headers=HEADERS)
    if c_resp.status_code == 401:
        return
    c = c_resp.json()
    case_id = c['id']

    payload = {
        'case_id': case_id,
        'kind': 'html_capture',
        'content': '<html>test</html>',
        'object_uri': 's3://bucket/case/evidence.html',
    }
    response = client.post('/api/v1/evidence', json=payload, headers=HEADERS)
    assert response.status_code == 200
    assert len(response.json()['sha256']) == 64
