#!/bin/sh
echo "Collect static files"
poetry run python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
until poetry run python manage.py migrate
do
  echo "Waiting for db to be ready..."
  sleep 2
done

# --> Duplicate logs to stdout for portainer console
echo "--> Starting prod logs"
tail -f /drf-ffmpeg/deploy/logs/gunicorn/access.log > /dev/stdout &
tail -f /drf-ffmpeg/deploy/logs/gunicorn/error.log > /dev/stderr &

exec "$@"
