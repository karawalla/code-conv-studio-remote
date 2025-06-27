FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install flask flask-cors

# Copy application files
COPY app.py .
COPY templates templates/
COPY static static/

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]