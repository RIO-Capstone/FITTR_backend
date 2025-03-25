import sqlite_utils
import erdantic as erd

db = sqlite_utils.Database("db.sqlite3")

class ExerciseSession:
    id: int
    exercise_type: str
    reps: int
    created_at: str
    errors: int
    product_id_id: int
    user_id_id: int
    duration: float

class Product:
    id: int
    version: str
    created_at: str
    service_uuid: str
    stop_characteristic_uuid: str
    left_resistance_characteristic_uuid: str
    exercise_initialize_uuid: str
    right_resistance_characteristic_uuid: str

class User:
    id: int
    first_name: str
    last_name: str
    email: str
    password: str
    weight: int
    height: int
    phone_number: str
    gender: str
    date_of_birth: str
    product_id_id: int
    created_at: str
    fitness_goal: str

erd.draw(ExerciseSession)
