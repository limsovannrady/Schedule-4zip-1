# 📅 Telegram Message Scheduler Bot

ប្រព័ន្ធ Bot Telegram សម្រាប់កំណត់ពេលផ្ញើសារទៅ Groups Telegram ជាស្វ័យប្រវត្តិ។

## លក្ខណៈពិសេស

- កំណត់ពេលផ្ញើសារ (Text, Photo, Video, Document, Audio) ទៅ Groups Telegram
- ទំព័រ Admin Dashboard តាមរយៈ Telegram Mini App
- បង្ហាញ Groups ដែល Bot ចូលរួម
- លុប schedules ដែលមិនចាំបាច់
- ប្រើ Timezone Cambodia (UTC+7)
- UI ភាសាខ្មែរ

## Tech Stack

- **Language**: Python 3.11
- **Bot Framework**: python-telegram-bot >= 22.7
- **Web Framework**: Flask >= 3.0.0
- **Frontend**: HTML / CSS / JavaScript (Telegram WebApp API)
- **Package Manager**: uv

## រចនាសម្ព័ន្ធ Project

```
Schedule-4/
├── bot.py                    # Telegram Bot - ផ្ញើ/ទទួលសារ
├── webapp.py                 # Flask Web Server - Admin API
├── main.py                   # Entry point សម្រាប់ Flask
├── start.sh                  # Script ដើម្បីដំណើរការ bot + webapp
├── static/
│   └── index.html            # Mini App Admin Dashboard
├── pyproject.toml            # Python dependencies
├── groups.json.example       # Template file
├── user_groups.json.example  # Template file
├── pending_schedules.json.example
├── scheduled_messages.json.example
└── settings.json.example
```

## របៀបដំណើរការ

### ១. Clone Repository

```bash
git clone <your-repo-url>
cd Schedule-4
```

### ២. ដំឡើង Dependencies

```bash
pip install -r requirements.txt
# ឬប្រើ uv
uv sync
```

### ៣. រៀបចំ Data Files

```bash
cp groups.json.example groups.json
cp user_groups.json.example user_groups.json
cp pending_schedules.json.example pending_schedules.json
cp scheduled_messages.json.example scheduled_messages.json
cp settings.json.example settings.json
```

### ៤. កំណត់ Environment Variables

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export WEBAPP_URL="https://your-webapp-url.com"
```

### ៥. កែ settings.json

```json
{
  "admin_user_id": YOUR_TELEGRAM_USER_ID
}
```

### ៦. ដំណើរការ

```bash
bash start.sh
```

ឬដំណើរការដាច់ដោយឡែក:

```bash
# Terminal 1 - Bot
python3 bot.py

# Terminal 2 - Web Server
python3 webapp.py
```

## Environment Variables

| Variable | ការប្រើប្រាស់ |
|----------|----------------|
| `TELEGRAM_BOT_TOKEN` | Token Bot ពី @BotFather |
| `WEBAPP_URL` | URL សាធារណៈរបស់ Web Server |

## API Endpoints

| Method | Endpoint | ការប្រើប្រាស់ |
|--------|----------|----------------|
| GET | `/api/groups` | ទទួល Groups ទាំងអស់ |
| POST | `/api/schedule` | បង្កើត Schedule ថ្មី |
| GET | `/api/scheduled` | ទទួល Schedules ទាំងអស់ |
| DELETE | `/api/scheduled/<id>` | លុប Schedule |
