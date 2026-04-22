from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthz():
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_readyz():
    response = client.get('/readyz')
    assert response.status_code == 200
    assert 'checks' in response.json()


def test_case_crud_entities_and_exports():
    payload = {'case_ref': 'SF-TEST-001', 'title': 'Test Case', 'severity': 'high'}
    response = client.post('/api/v1/cases', json=payload)
    assert response.status_code == 200
    case_id = response.json()['id']

    e_resp = client.post(
        f'/api/v1/cases/{case_id}/entities/bulk',
        json=[
            {'entity_type': 'domain', 'entity_value': 'example.com'},
            {'entity_type': 'wallet', 'entity_value': 'bc1qexample'},
        ],
    )
    assert e_resp.status_code == 200
    assert len(e_resp.json()['entities']) == 2

    exp = client.get(f'/api/v1/exports/ioc?format=json&case_id={case_id}')
    assert exp.status_code == 200
    assert len(exp.json()['items']) == 2


def test_enrichment_job_persistence():
    response = client.post('/api/v1/enrichment/jobs', json={'observable_type': 'domain', 'value': 'Example.COM'})
    assert response.status_code == 200
    job_id = response.json()['job_id']

    result = client.get(f'/api/v1/enrichment/jobs/{job_id}')
    assert result.status_code == 200
    body = result.json()
    assert body['status'] == 'completed'
    assert body['result']['normalized'] == 'example.com'


def test_evidence_hashing():
    case_payload = {'case_ref': 'SF-TEST-002', 'title': 'Evidence Case', 'severity': 'medium'}
    c = client.post('/api/v1/cases', json=case_payload).json()
    case_id = c['id']

    payload = {
        'case_id': case_id,
        'kind': 'html_capture',
        'content': '<html>test</html>',
        'object_uri': 's3://bucket/case/evidence.html',
    }
    response = client.post('/api/v1/evidence', json=payload)
    assert response.status_code == 200
    assert len(response.json()['sha256']) == 64
