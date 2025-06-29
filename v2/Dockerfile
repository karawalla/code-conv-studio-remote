FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy application files
COPY app.py .
COPY services services/
COPY templates templates/
COPY static static/
COPY init_targets.py .

# Create data directories
RUN mkdir -p data/sources

# Copy targets metadata if it exists
COPY data/targets_metadata.json data/targets_metadata.json

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]