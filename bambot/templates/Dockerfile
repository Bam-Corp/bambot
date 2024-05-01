# bam/templates/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install only the necessary dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy only the required files
COPY . .

# Run the application
CMD ["python", "main.py"]