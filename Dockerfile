# Stage 1: Build the Application
FROM python:3.11-slim AS build

WORKDIR /usr/src/app

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv

# Activate virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements file
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application source code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Stage 2: Create the Final Production Image
FROM python:3.11-slim

WORKDIR /usr/src/app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the build stage
COPY --from=build /opt/venv /opt/venv

# Copy the application code and static files
COPY --from=build /usr/src/app .

# Set the virtual environment as the active Python environment
ENV PATH="/opt/venv/bin:$PATH"

# --- MUDANÇA PRINCIPAL: Usar ROOT para permitir escrita no Volume ---
USER root

# Expose the port your app runs on (Ajustado para 8000)
ENV PORT=8000
EXPOSE 8000

# Run database migrations and start the application
# O comando abaixo tenta rodar a migração e depois sobe o servidor
CMD sh -c "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 --workers 2 --threads 2 --timeout 120 Projeto.wsgi:application"