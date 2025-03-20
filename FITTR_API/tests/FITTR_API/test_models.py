import pytest
from datetime import date
from FITTR_API.models import User, Product

@pytest.fixture
def product_fixture(db):
    """Creates a sample product for testing."""
    return Product.objects.create(version="1.0")

@pytest.fixture
def user_fixture(db, product_fixture):
    """Creates a sample user for testing."""
    return User.objects.create(
        first_name="John",
        last_name="Doe",
        email="johndoe@example.com",
        password="securepass",
        weight=70,  # kg
        height=175,  # cm
        phone_number="1234567890",
        gender="male",
        date_of_birth=date(2000, 3, 15),
        product_id=product_fixture,
        fitness_goal="Strength Seeker"
    )

def test_get_age(user_fixture):
    """Test that the age calculation is correct."""
    today = date.today()
    expected_age = today.year - user_fixture.date_of_birth.year
    if today < user_fixture.date_of_birth.replace(year=today.year):
        expected_age -= 1
    assert user_fixture.get_age() == expected_age

@pytest.mark.parametrize("weight, height, expected_bmi", [
    (50, 160, 19.53),
    (70, 175, 22.86),
    (90, 180, 27.78),
    (110, 170, 38.06),
])
def test_get_bmi(db, product_fixture, weight, height, expected_bmi):
    """Test BMI calculation for different weights and heights."""
    user = User.objects.create(
        first_name="Test",
        last_name="User",
        email="testuser@example.com",
        password="testpass",
        weight=weight,
        height=height,
        phone_number="9999999999",
        gender="male",
        date_of_birth=date(1995, 5, 5),
        product_id=product_fixture
    )
    assert round(user.get_bmi(), 2) == expected_bmi

@pytest.mark.parametrize("gender, weight, height, age, expected_bmr", [
    ("male", 70, 175, 24, 1729.73),
    ("female", 60, 165, 30, 1383.68),
    ("other", 80, 180, 40, 0),  # Invalid gender case
])
def test_get_bmr(db, product_fixture, gender, weight, height, age, expected_bmr):
    """Test BMR calculation for different genders and body compositions."""
    birth_year = date.today().year - age
    user = User.objects.create(
        first_name="Test",
        last_name="User",
        email="testbmr@example.com",
        password="testpass",
        weight=weight,
        height=height,
        phone_number="8888888888",
        gender=gender,
        date_of_birth=date(birth_year, 1, 1),
        product_id=product_fixture
    )
    assert round(user.get_bmr(), 2) == expected_bmr

@pytest.mark.parametrize("weight, height, expected_description", [
    (50, 160, "Normal weight (BMI: 19.53)"),
    (70, 175, "Normal weight (BMI: 22.86)"),
    (90, 180, "Obese (BMI: 27.78)"),
    (110, 170, "Obese (BMI: 38.06)"),
])
def test_get_bmi_description(db, product_fixture, weight, height, expected_description):
    """Test BMI category descriptions."""
    user = User.objects.create(
        first_name="Test",
        last_name="User",
        email="testbmidesc@example.com",
        password="testpass",
        weight=weight,
        height=height,
        phone_number="7777777777",
        gender="male",
        date_of_birth=date(1990, 6, 15),
        product_id=product_fixture
    )
    assert user.get_bmi_description() == expected_description

@pytest.mark.parametrize("gender, weight, height, age, expected_description", [
    ("male", 70, 175, 24, "Optimal BMR (BMR: 1729.73)"),
    ("female", 60, 165, 30, "Optimal BMR (BMR: 1383.68)"),
    ("other", 80, 180, 40, "Undefined bmr. Do not use bmr value as context"),
])
def test_get_bmr_description(db, product_fixture, gender, weight, height, age, expected_description):
    """Test BMR category descriptions."""
    birth_year = date.today().year - age
    user = User.objects.create(
        first_name="Test",
        last_name="User",
        email="testbmrdesc@example.com",
        password="testpass",
        weight=weight,
        height=height,
        phone_number="6666666666",
        gender=gender,
        date_of_birth=date(birth_year, 1, 1),
        product_id=product_fixture
    )
    assert user.get_bmr_description() == expected_description
