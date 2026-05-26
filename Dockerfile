# APLIKACJA POGODOWA 
# Autor: Kyryl Nazarov
# Opis: Dockerfile do budowania kontenera aplikacji pogodowej z wykorzystaniem wieloetapowego budowania

# Przygotowanie zależności
FROM python:3.11-alpine AS builder

# Metadane OCI
LABEL org.opencontainers.image.authors="Kyryl Nazarov"
LABEL org.opencontainers.image.description="Weather application builder stage"
LABEL org.opencontainers.image.version="1.0.0"

# Ustawienie zmiennej środowiskowej
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Instalacja zależności systemowych wymaganych do budowania
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    linux-headers

# Utworzenie katalogów 
RUN mkdir -p /opt/venv
WORKDIR /app

# Instalacja Python'a w wirtualnym środowisku
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel && \
    pip install Flask==3.0.3 Werkzeug==3.0.3 requests==2.32.4 gunicorn==23.0.0

# Usunięcie zbędnych plików po instalacji
RUN find /opt/venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /opt/venv -type f -name "*.pyc" -delete && \
    find /opt/venv -type f -name "*.pyo" -delete

# Runtime
FROM python:3.11-alpine

# Informacja o autorze
LABEL org.opencontainers.image.authors="Kyryl Nazarov" \
    org.opencontainers.image.title="Weather Application" \
    org.opencontainers.image.description="Flask-based weather application with Open-Meteo API" \
    org.opencontainers.image.version="1.0.0" \
    org.opencontainers.image.source="https://github.com/nazkirill43-glitch/weather-app" \
    maintainer="Kyryl Nazarov"

# Zmienne środowiskowe dla aplikacji
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=5000 \
    FLASK_APP=app.py

# Instalacja tylko niezbędnych zależności 
RUN apk add --no-cache \
    ca-certificates \
    tzdata

# Utworzenie użytkownika bez uprawnień root
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# Ustawienie katalogu roboczego
WORKDIR /app

# Skopiowanie wirtualnego środowiska
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Skopiowanie kodu aplikacji
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser templates/ ./templates/
COPY --chown=appuser:appuser static/ ./static/

# Zmiana na użytkownika non-root
USER appuser

# Exponowanie portu TCP
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5000/health || exit 1

# BuildKit cache mount
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip

# Punkt wejścia
CMD sh -c "echo 'Autor: Kyryl Nazarov' && \
    echo 'Data startu: $(date +%Y-%m-%d\ %H:%M:%S)' && \
    echo 'Port TCP: 5000' && \
    echo 'URL: http://localhost:5000' && \
    gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 2 \
    --threads 2 \
    --worker-class gthread \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    app:app"
