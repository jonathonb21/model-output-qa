from fastapi.testclient import TestClient

from model_output_qa.api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_validate_endpoint():
    response = client.post(
        "/validate",
        json={"prompt_id": "demo", "answer": "return 1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True


def test_validate_batch_endpoint():
    response = client.post(
        "/validate/batch",
        json={
            "records": [
                {"prompt_id": "a", "answer": "return 1"},
                {"prompt_id": "b", "answer": "TODO"},
            ]
        },
    )
    body = response.json()
    assert body["total"] == 2
    assert body["passed"] == 1
    assert body["failed"] == 1
