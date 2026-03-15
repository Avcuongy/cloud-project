# Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir
WORKDIR /app

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY . .

# Default environment
ENV FLASK_ENV=production \
    PORT=5000

# Expose Flask port
EXPOSE 5000

# Run with gunicorn in production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
