# Use full Python image to avoid missing dependencies
FROM python:3.11

# Set working directory inside container
WORKDIR /app

# Copy entire project directory into the container
COPY . .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt




CMD uvicorn src.api.main:app --host 0.0.0.0 --port $PORT

