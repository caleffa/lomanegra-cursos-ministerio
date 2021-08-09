#!/bin/bash

python /wait-for-postgres.py && \
python manage.py migrate && \
python manage.py compilescss && \
python manage.py collectstatic --noinput && \
if [ "$DEBUG" = "True" ]; then uwsgi /uwsgi.ini --python-autoreload=1; else uwsgi /uwsgi.ini; fi