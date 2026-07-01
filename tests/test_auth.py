import pytest

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200



def test_signup_create_user_org_and_membership(client):
    response = client.post("/auth/signup", json={
        "email": "user_1@example.com",
        "password": "password123",
        "organisation_name": "newcorp"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()
        

def test_login_returns_valid_JWT(client):
    client.post(
        "/auth/signup",
        json={
            "email": "user_1@example.com",
            "password": "password123",
            "organisation_name": "newcorp",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "user_1@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_protected_route_rejects_no_token(client):
    response = client.post("/workflows")

    assert response.status_code == 401

def test_cannot_access_other_tenants_workflow(client):
    client.post(
        "/auth/signup",
        json={
            "email": "user_1@example.com",
            "password": "password123",
            "organisation_name": "newcorp",
        },
    )

    client.post(
        "/auth/signup",
        json={
            "email": "user_2@example.com",
            "password": "password123",
            "organisation_name": "othercorp",
        },
    )

    login = client.post(
        "/auth/login",
        data={
            "username": "user_1@example.com",
            "password": "password123",
        },
    )

    token = login.json()["access_token"]

    new_workflow = client.post(
        "/workflows",
        json={"name": "beginners_workflow"},
        headers={"Authorization": f"Bearer {token}"},
    )

    id = new_workflow.json()["id"]

    login2 = client.post(
        "/auth/login",
        data={
            "username": "user_2@example.com",
            "password": "password123",
        },
    )

    token2 = login2.json()["access_token"]

    response = client.get(
        f"/workflows/{id}",
        headers={"Authorization": f"Bearer {token2}"},
        )

    assert response.status_code == 404