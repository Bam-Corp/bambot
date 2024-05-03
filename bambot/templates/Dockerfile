# bambot/templates/Dockerfile
FROM python:3.11-alpine

WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy over project files
COPY . .

# Run the application
CMD ["python", "server.py"]

# Expose server port
EXPOSE 1337