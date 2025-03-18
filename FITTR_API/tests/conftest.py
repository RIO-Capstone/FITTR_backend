import pytest
from rest_framework.test import APIClient
from FITTR_API.models import User, Product

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def product_fixture(db):
    return Product.objects.create(version=1)

@pytest.fixture
def user_fixture(db, product_fixture):
    return User.objects.create(
        first_name="John",
        last_name="Doe",
        email="testme@gmail.com",
        password="test123",
        weight=70,
        height=180,
        phone_number="1234567890",
        gender="male",
        date_of_birth="1990-01-01",
        product_id=product_fixture
    )
    
    