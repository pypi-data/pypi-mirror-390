# SemFire CLI container
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install dependencies
# By default, install from requirements.txt to match local dev.
# Set INSTALL_REQS=false to build a minimal image.
ARG INSTALL_REQS=true
COPY requirements.txt ./requirements.txt

RUN if [ "$INSTALL_REQS" = "true" ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    else \
      pip install --no-cache-dir requests rich python-dotenv; \
    fi

# Copy project (filtered by .dockerignore) to ensure new modules are included
COPY . .

# Default behavior: print CLI help. Override CMD to run other commands.
CMD ["python", "-m", "src.cli", "--help"]
