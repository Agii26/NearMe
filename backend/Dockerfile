FROM python:3.12-slim

# GeoDjango needs GDAL/GEOS/PROJ system libraries — they don't come from pip.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "nearme_backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
