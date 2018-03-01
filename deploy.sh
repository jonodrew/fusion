#!/bin/sh
source venv/bin/activate
flask db upgrade
exec gunicorn -b :$PORT --access-logfile - --error-logfile - fusion:app