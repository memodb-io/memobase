#!/bin/bash
set -e

if [ "$1" = "api" ]; then
    exec python -m fastapi run api.py
elif [ "$1" = "worker" ]; then
    # exec python -m celery -A api.celery_app worker --loglevel=info
    echo "Celery worker is not implemented yet"
    exit 1
else
    echo "Usage: $0 {api|worker}"
    exit 1
fi 
