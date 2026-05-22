# Stage 1: Build deps
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: Runtime
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

COPY --from=builder /install /usr/local

COPY alembic/ alembic/
COPY alembic.ini alembic.ini
COPY app/ app/
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh && chown -R app:app /app

USER app

ENTRYPOINT ["/entrypoint.sh"]
