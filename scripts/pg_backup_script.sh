#!/bin/bash
# PostgreSQL Backup Script to AWS S3

set -e  # Exit on error

# ====== CONFIGURATION ======
DATE=$(date +%F_%H-%M-%S)
BACKUP_DIR=/tmp/pg_backup
S3_BUCKET="s3://mech-book-backup/postgres"
DB_CONTAINER="postgres"
DB_USER=$POSTGRES_USER

mkdir -p $BACKUP_DIR

docker exec -t $DB_CONTAINER pg_dumpall -U $DB_USER > $BACKUP_DIR/mechbook_db_$DATE.sql

7z a -mx=9 $BACKUP_DIR/mechbook_db_$DATE.sql.7z $BACKUP_DIR/mechbook_db_$DATE.sql

aws s3 cp $BACKUP_DIR/MECHBOOK_DB_$DATE.sql.7z $S3_BUCKET/mech-book-backup/