#!/bin/bash
# Резервная копия базы PostgreSQL из контейнера db в ./backups/.
# Использование: ./scripts/backup.sh
set -euo pipefail

cd "$(dirname "$0")/.."

# Загружаем переменные из .env (POSTGRES_USER / POSTGRES_DB)
if [ -f .env ]; then
    set -a; . ./.env; set +a
fi

POSTGRES_USER="${POSTGRES_USER:-fashop}"
POSTGRES_DB="${POSTGRES_DB:-fashop}"

mkdir -p backups
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTFILE="backups/${POSTGRES_DB}_${TIMESTAMP}.sql.gz"

echo "Создаю дамп $POSTGRES_DB -> $OUTFILE"
docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$OUTFILE"
echo "Готово: $OUTFILE"

# Чистим дампы старше 14 дней
find backups -name "*.sql.gz" -mtime +14 -delete 2>/dev/null || true
