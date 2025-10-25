#!/bin/bash

# === LOAD .env ===
set -a
source /home/administrator/MechBook/backend/scripts/.env
set +a

export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

mkdir -p "$BACKUP_DIR"

# === VARIABLES ===
DATE=$(date +'%Y-%m-%d_%H-%M')
BACKUP_NAME="pg_backup_$DATE.dump"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# === BACKUP ===
echo "[$DATE] Creating backup..."
docker exec "$DOCKER_DB_CONTAINER_NAME" pg_dump -U "$DB_USER" -Fc "$DB_NAME" > "$BACKUP_PATH"

# === UPLOAD TO S3 ===
echo "[$DATE] Uploading to S3..."
/snap/bin/aws s3 cp "$BACKUP_PATH" "$S3_BUCKET"

# === DELETE OLD LOCAL BACKUPS (7 days) ===
echo "[$DATE] Deleting old backups..."
find "$BACKUP_DIR" -type f -name "*.dump" -mtime +7 -exec rm {} \;

echo "[$DATE] Backup completed successfully."