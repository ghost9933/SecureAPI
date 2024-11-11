# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables to prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (optional)
# RUN apt-get update && apt-get install -y build-essential

# Copy the requirements file first for better caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the Docker image
COPY . .

# Create the data directory for SQLite database
RUN mkdir -p /app/data

# Create the logs directory
RUN mkdir -p /app/logs

# (Optional) Create a non-root user and set permissions
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser /app/data /app/logs

# Switch to the non-root user for security
USER appuser

# Expose port 8000 to the host
EXPOSE 8000

# Define the default command to run the application using Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
