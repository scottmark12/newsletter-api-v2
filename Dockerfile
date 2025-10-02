# Use Python 3.11 explicitly - this MUST be 3.11, not 3.13
FROM python:3.11.9-slim

# Verify Python version
RUN python --version

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Verify Python version again before install
RUN python --version && pip --version

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Final Python version check
RUN python --version

# Expose port
EXPOSE 10000

# Start command
CMD ["python", "-m", "uvicorn", "app.main:web_app", "--host", "0.0.0.0", "--port", "10000"]