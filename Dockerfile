# Network Security ML — base image for later use
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy project source
COPY . .

# Default command (change later as needed)
CMD ["python", "main.py"]
