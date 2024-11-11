# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Set permissions (optional)
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser /app/data

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]