#! /bin/bash
# Before running the script, pass the backup file name

# Load environment variables
set -ae
source /home/administrator/MechBook/backend/scripts/.env
set +a

DUMP_FILE="$1"


echo "Downloading backup file from S3: $DUMP_FILE"
aws s3 cp "$S3_BUCKET/$DUMP_FILE" .


echo "Copying backup into PostgreSQL container: $DOCKER_DB_CONTAINER_NAME"
docker cp "$DUMP_FILE" "$DOCKER_DB_CONTAINER_NAME":/tmp/restore.dump

echo "Restoring PostgreSQL database: $DOCKER_DB_CONTAINER_NAME"
docker exec -i "$DOCKER_DB_CONTAINER_NAME" pg_restore -U "$DB_USER" --clean -d "$DB_NAME" /tmp/restore.dump
echo "Database restore completed successfully."

echo "Reindexing Elasticsearch: $DOCKER_BACKEND_CONTAINER_NAME"
docker exec -i "$DOCKER_BACKEND_CONTAINER_NAME" python3 scripts/reindex.py
echo "Elasticsearch reindex completed."

echo "Finished successfully."