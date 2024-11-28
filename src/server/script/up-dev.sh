set -e
rm -rf ./db/dev_data
rm -rf ./db/dev_redis
DATABASE_LOCATION="./db/dev_data" REDIS_LOCATION="./db/dev_redis" docker compose up memobase-server-db memobase-server-redis
rm -rf ./db/dev_data
rm -rf ./db/dev_redis