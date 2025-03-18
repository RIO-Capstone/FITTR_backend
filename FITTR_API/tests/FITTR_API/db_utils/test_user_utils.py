import pytest

@pytest.mark.django_db
def test_login_user(client, user_fixture):
    payload = dict(
        email="testme@gmail.com",
        password="test123"
    )
    
    response = client.post("/user/login", payload, format='json')
    data = response.json()
    
    assert response.status_code == 200
    assert "user" in data
    assert "user_id" in data["user"]
    assert "first_name" in data["user"]
    assert "last_name" in data["user"]
    assert "email" in data["user"]
    assert "weight" in data["user"]
    assert "height" in data["user"]
    assert "product_id" in data["user"]
    
@pytest.mark.django_db
def test_login_user_fail(client):
    payload = dict(
        email="abcd@123",
        password="test123"
    )
    
    response = client.post("/user/login", payload, format='json')
    data = response.json()
    assert response.status_code == 401
    assert "error" in data
    
@pytest.mark.django_db
def test_register_user(client, product_fixture):
    payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "janedoe@example.com",
        "password": "password123",
        "weight": 65,
        "height": 165,
        "phone_number": "9876543210",
        "gender": "female",
        "date_of_birth": "25-12-1995",  # Format: DD-MM-YYYY
        "product_id": product_fixture.id,
        "fitness_goal": "muscle_gain"
    }

    response = client.post("/user/register", payload, format="json")
    data = response.json()

    assert response.status_code == 201
    assert "message" in data
    assert data["message"] == "Registration successfull."
    assert "user_id" in data


@pytest.mark.django_db
def test_register_user_fail(client):
    payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "test"
    }
    response = client.post("/user/register", payload, format="json")
    data = response.json()
    assert response.status_code == 400
    assert data["error"].endswith("is required.")
    
@pytest.mark.django_db
def test_get_all_users(client, user_fixture):
    response = client.get("/users", format="json")
    data = response.json()

    assert response.status_code == 200
    assert "users" in data
    assert len(data["users"]) == 1  # Should return 1 user, since we created one in `user_fixture`
    assert "id" in data["users"][0]
    assert "full_name" in data["users"][0]

@pytest.mark.django_db
def test_get_user(client, user_fixture):
    response = client.get(f"/user/{user_fixture.id}", format="json")
    data = response.json()

    assert response.status_code == 200
    assert "user" in data
    assert data["user"]["user_id"] == user_fixture.id
    assert data["user"]["first_name"] == "John"
    assert data["user"]["last_name"] == "Doe"
    
@pytest.mark.django_db
def test_get_users_by_product(client, user_fixture, product_fixture):
    response = client.get(f"/user/product/{product_fixture.id}", format="json")
    data = response.json()

    assert response.status_code == 200
    assert "users" in data
    assert len(data["users"]) == 1  # Should return 1 user for the given product
    assert data["users"][0]["id"] == user_fixture.id
    assert data["users"][0]["full_name"] == "John Doe"


@pytest.mark.django_db
def test_get_users_by_product_no_users(client):
    # Trying with a non-existent Product ID
    non_existent_product_id = 9999
    response = client.get(f"/user/product/{non_existent_product_id}", format="json")
    data = response.json()

    assert response.status_code == 404
    assert "error" in data
    assert data["error"] == f"No users found for product ID {non_existent_product_id}"


    