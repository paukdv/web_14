from unittest.mock import MagicMock, patch
import pytest
from src.database.models import User
from src.services.auth import auth_service


@pytest.fixture()
def access_token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    current_user.roles = "admin"
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


def test_create_contact(client, access_token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/contacts",
            json={
                "id": 1,
                "first_name": "user",
                "last_name": "user2",
                "phone_number": "0987777",
                "birthday": "1968-10-30",
                "email": "usercontact@gmail.com",
                "additional_data": "Empty"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["first_name"] == "user"
        assert data["last_name"] == "user2"
        assert data["phone_number"] == "0987777"
        assert data["birthday"] == "1968-10-30"
        assert data["email"] == "usercontact@gmail.com"
        assert data["additional_data"] == "Empty"
        assert "id" in data


def test_get_contact_found(client, access_token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["first_name"] == "user"
        assert data["last_name"] == "user2"
        assert data["phone_number"] == "0987777"
        assert data["birthday"] == "1968-10-30"
        assert data["email"] == "usercontact@gmail.com"
        assert data["additional_data"] == "Empty"


def test_get_contact_not_found(client, access_token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/2",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Not found"


# def test_get_contacts(client, access_token):
#     with patch('FastAPILimiter) as init_mock:
#         with patch.object(auth_service, 'redis') as r_mock:
#             r_mock.get.return_value = None
#             response = client.get(
#                 "/api/contacts",
#                 headers={"Authorization": f"Bearer {access_token}"}
#             )
#             assert response.status_code == 200, response.text
#             data = response.json()
#             assert isinstance(data, list)
#             assert data[0]["first_name"] == "user"
#             assert "id" in data[0]
#
#         init_mock.assert_called_once()
#
#
def test_update_contact(client, access_token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            "/api/contacts/1",
            json={
                "id": 1,
                "first_name": "new_user_name",
                "last_name": "user2",
                "phone_number": "0987777",
                "birthday": "1968-10-30",
                "email": "usercontact@gmail.com",
                "additional_data": "Empty"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["first_name"] == "new_user_name"


def test_update_contact_not_found(client, access_token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            "/api/tags/2",
            json={
                "id": 2,
                "first_name": "new_user_name",
                "last_name": "user2",
                "phone_number": "0987777",
                "birthday": "1968-10-30",
                "email": "usercontact@gmail.com",
                "additional_data": "Empty"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Not Found"


def test_delete_contact(client, access_token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print(response.status_code)
        assert response.status_code == 204, response.text


def test_repeat_delete_contact(client, access_token):
    with patch.object(auth_service, 'redis') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/contacts/2",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Not found"
