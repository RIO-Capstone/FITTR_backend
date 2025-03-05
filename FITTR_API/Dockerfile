# Dockerfile
FROM python:3.11.11-slim-bookworm AS django_app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Run the Django server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "FITTR_API.asgi:application"]

FROM python:3.11.11-slim-bookworm AS huey_worker

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Run the Huey worker
CMD ["python", "manage.py", "run_huey"]