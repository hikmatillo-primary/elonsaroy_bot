#!/bin/sh
set -e

echo "Migratsiyalar ishga tushirilmoqda..."
alembic upgrade head

echo "Bot ishga tushirilmoqda..."
exec python -m app.bot
