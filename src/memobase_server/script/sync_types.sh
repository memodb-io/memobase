set -e

python ./api/build_init_sql.py > ./db/init.sql
# echo the current time to a file
echo "# Synced from memobase_server.models.blob on $(date)" > ../memobase/core/blob.py
cat ./api/memobase_server/models/blob.py >> ../memobase/core/blob.py