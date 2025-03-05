# FITTR API Backend

This document provides instructions for setting up, running, and managing the FITTR API backend using Docker and Django.

---

## 🚀 Running the Server
Ensure you are in the same directory as the `compose.yaml` file before running the server.

**Run the server with:**
```sh
docker compose up -d --build
```

---

## 📌 Applying Migrations
Before running migrations, make sure you are inside the project directory.

1. Generate migrations for the `FITTR_API` app:
   ```sh
   python manage.py makemigrations FITTR_API
   ```
2. Apply migrations to the database:
   ```sh
   python manage.py migrate
   ```

---

## 🛠 Querying the SQLite Database in CMD
To interact with the SQLite database directly:

1. Navigate to the `FITTR_API` directory (where `db.sqlite3` is located).
2. Start an SQLite session:
   ```sh
   sqlite3 db.sqlite3
   ```
3. List all tables in the database:
   ```sh
   .tables
   ```
4. Example SQL Query:
   ```sql
   SELECT * FROM FITTR_API_user;
   ```
5. Example Edit Query:
   ```sql
   UPDATE FITTR_API_product
   SET exercise_initialize_uuid = 'new_uuid_value'
   WHERE id = <product_id>;
   ```

---

## 📄 Updating `requirements.txt`
To update the environment dependencies:
```sh
pip list --format=freeze > requirements.txt
```

### Updating `requirements.txt` for the Django Project
1. Ensure you are in the `FITTR_API` directory.
2. Run the following command to update only project-specific dependencies:
   ```sh
   pipreqs --force ./
   ```

---

## 🐳 Installing Docker
Follow the installation instructions for your system:
[Docker Windows Install](https://docs.docker.com/desktop/setup/install/windows-install/)

---

## 🏗️ Docker Commands
### Getting the Redis:latest Image
Redis image website: [Docker Redis](https://hub.docker.com/_/redis)
```sh
docker pull redis
```


### Building with Docker
1. Navigate to the directory containing the `Dockerfile`.
2. Build the Docker image:
   ```sh
   docker build --tag backend_service:v1 .
   ```

### Running the Container
Run the container and expose it on port `8000`:
```sh
docker run -d -p 8000:8000 --name FITTR_Backend backend_service:v1
```

### Building & Launching Docker Compose
To build and start all services using `docker-compose`:
```sh
docker compose up -d --build
```

---

### 🎯 You're all set! 🎯

