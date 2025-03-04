## Running the server
Command to run django server: daphne -b 0.0.0.0 -p 8000 FITTR_API.asgi:application
User must be in the same directory as the manage.py file.

## Applying Migrations
1. First run: python manage.py makemigrations FITTR_API
2. Then run: python manage.py migrate
## Querying Sqlite3 Database on CMD
1. Traverse to the FITTR_API directory (where the database file is)
2. Command to initialize session: sqlite3  db.sqlite3
3. Command to get a list of all the tables in the database: .tables
4. SQL Query <SELECT * FROM FITTR_API_user;>
<h5>Example edit query</h5>
<UPDATE FITTR_API_product
SET exercise_initialize_uuid = 'new_uuid_value'
WHERE id = <product_id>;>

## Updating requirements.txt for the environment
pip list --format=freeze > requirements.txt

## Updating requirements.txt for Django project
1) Ensure that you're in the FITTR_API directory
2) Run: pipreqs --force ./ (this should overrite any existing requirements.txt file and only produce Django project specific dependencies)

## Docker commands
### Building with docker
1) Ensure that you're in Dockerfile directory
2) Run: docker build --tag backend_service:v1 .
### Running the container
1) Run: docker run -d -p 8000:8000 --name FITTR_Backend backend_service:v1 