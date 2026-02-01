FROM python:3.10-slim

# Avoid Python buffering & bytecode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Expose service port
EXPOSE 8003

# Run service
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]
