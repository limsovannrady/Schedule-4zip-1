#!/bin/bash
set -e

# Initialize data files if not present
[ ! -f groups.json ]            && echo '{}'  > groups.json
[ ! -f user_groups.json ]       && echo '{}'  > user_groups.json
[ ! -f pending_schedules.json ] && echo '{}'  > pending_schedules.json
[ ! -f scheduled_messages.json ] && echo '[]' > scheduled_messages.json

echo "✅ Data files initialized"
echo "🤖 Starting Telegram Bot..."
python bot.py &
BOT_PID=$!

echo "🌐 Starting Web Server on port ${PORT:-10000}..."
exec gunicorn --bind=0.0.0.0:${PORT:-10000} \
              --workers=1 \
              --timeout=120 \
              --log-level=info \
              webapp:app
