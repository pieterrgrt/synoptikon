FROM python:3.12-slim-bookworm

# WeasyPrint heeft Pango/HarfBuzz nodig voor de PDF-export. Verder niets.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libharfbuzz-subset0 \
        libffi8 shared-mime-info fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    SYNOPTIKON_DATA_DIR=/data

WORKDIR /app
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt
COPY synoptikon ./synoptikon
RUN pip install --no-cache-dir --no-deps -e .

RUN useradd --system --uid 10001 --create-home synoptikon && mkdir -p /data && chown synoptikon:synoptikon /data
USER synoptikon
VOLUME ["/data"]
EXPOSE 8000

# Eén worker volstaat voor één gebruiker en houdt het geheugen klein (~80 MB).
CMD ["uvicorn", "synoptikon.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers", "--forwarded-allow-ips", "*"]
