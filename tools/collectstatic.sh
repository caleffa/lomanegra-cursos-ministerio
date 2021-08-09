#!/bin/bash
docker-compose run --rm app python manage.py collectstatic --noinput | grep -v "Found another file with the destination path"
