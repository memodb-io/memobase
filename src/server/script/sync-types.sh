set -e

# python ./api/build_init_sql.py > ./db/init.sql

# Get the value of __version__ from memobase_server.__init__
version=$(grep -oE '__version__ *= *"[^"]+"' ./api/memobase_server/__init__.py | awk -F'"' '{print $2}')
echo "Version: $version"
echo "# Synced from backend ${version}" > ../client/memobase/core/blob.py
cat ./api/memobase_server/models/blob.py >> ../client/memobase/core/blob.py