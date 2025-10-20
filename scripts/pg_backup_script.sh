#!/bin/bash

# LOAD .env
export $(grep -v '^#' /home/administrator/MechBook/scripts/.env | xargs)

# CREATE BACKUP DIR IF NOT EXISTS
mkdir -p $BACKUP_DIR

DATE=$(date +'%Y-%m-%d') #every day night at 00:00
BACKUP_NAME="pg_backup_$DATE.sql.gz"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# 1) CREATE BACKUP
docker exec $CONTAINER_NAME pg_dumpall -U $DB_USER | gzip > $BACKUP_PATH

# 2) UPLOAD TO S3
aws s3 cp $BACKUP_PATH $S3_BUCKET

# 3) DELETE LOC BACKUPS OLDER THAN 7 DAYS
find $BACKUP_DIR -type f -name "*.gz" -mtime +7 -exec rm {} \;
