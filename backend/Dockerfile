# Use Python 3.11 slim as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy requirements file first for caching
COPY requirements.txt /app/

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application code to a folder named 'backend'
# This allows 'uvicorn backend.app.main:app' to find the 'backend' package
COPY . /app/backend

# Expose port 8000
EXPOSE 8000

# Start FastAPI using uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
