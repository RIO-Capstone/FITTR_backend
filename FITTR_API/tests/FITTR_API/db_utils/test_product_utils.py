import pytest

@pytest.mark.django_db
def test_register_product(client):
    payload = dict(
        version=1
    )
    
    response = client.post("/product/register", payload, format='json')
    data = response.json()
    
    assert response.status_code == 201
    assert "product_id" in data
    
@pytest.mark.django_db
def test_register_product_fail(client):
    payload = dict(
        versio2n="1.0"
    )
    
    response = client.post("/product/register", payload, format='json')
    data = response.json()
    
    assert response.status_code == 400
    assert "error" in data
    
@pytest.mark.django_db
def test_get_poduct(client, product_fixture):
    response = client.get("/product/1")
    data = response.json()
    
    assert response.status_code == 200
    assert "service_uuid" in data
    assert "left_resistance_uuid" in data
    assert "right_resistance_uuid" in data
    assert "stop_uuid" in data
    
@pytest.mark.django_db
def test_get_product_fail(client):
    response = client.get("/product/100")
    data = response.json()
    
    assert response.status_code == 401
    assert "error" in data
    
@pytest.mark.django_db
def test_get_all_products(client, product_fixture):
    response = client.get("/products")
    data = response.json()
    
    assert response.status_code == 200
    assert "products" in data
    assert len(data["products"]) > 0
    
@pytest.mark.django_db
def test_register_product_invalid_json(client):
    """Test that sending invalid JSON triggers JSONDecodeError."""
    response = client.post("/product/register", data="invalid_json_string", content_type="application/json")

    assert response.status_code == 400
    assert response.json() == {"error": "Invalid JSON format."}