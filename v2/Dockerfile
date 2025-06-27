FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install flask flask-cors

# Copy application files
COPY app.py .
COPY services services/
COPY templates templates/
COPY static static/

# Create data directories
RUN mkdir -p data/sources

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]