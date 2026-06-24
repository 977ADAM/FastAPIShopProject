#!/bin/bash
# Восстановление базы PostgreSQL из дампа, созданного backup.sh.
# Использование: ./scripts/restore.sh backups/fashop_YYYYMMDD_HHMMSS.sql.gz
set -euo pipefail

cd "$(dirname "$0")/.."

if [ $# -lt 1 ]; then
    echo "Использование: $0 <путь-к-дампу.sql.gz>"
    exit 1
fi

DUMP="$1"
if [ ! -f "$DUMP" ]; then
    echo "Файл не найден: $DUMP"
    exit 1
fi

if [ -f .env ]; then
    set -a; . ./.env; set +a
fi

POSTGRES_USER="${POSTGRES_USER:-fashop}"
POSTGRES_DB="${POSTGRES_DB:-fashop}"

echo "ВНИМАНИЕ: данные в $POSTGRES_DB будут перезаписаны из $DUMP"
read -p "Продолжить? (y/n): " -n 1 -r; echo
[[ $REPLY =~ ^[Yy]$ ]] || exit 0

gunzip -c "$DUMP" | docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
echo "Восстановление завершено."
