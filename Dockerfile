FROM python:3.11-slim

# Install uv for faster package installs
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN uv pip install --system --no-cache -r requirements.txt

COPY . /app



CMD ["gunicorn", "GymGeniusAI.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--max-requests", "1000", "--max-requests-jitter", "50"]

EXPOSE 8000
