from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "REST APP CONTACTS v1.0"}