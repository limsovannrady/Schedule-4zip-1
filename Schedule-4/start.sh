#!/bin/bash
python bot.py &
gunicorn --bind=0.0.0.0:$PORT --reuse-port --workers=2 webapp:app
