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
- **Server**: Gunicorn
- **Deployment**: Docker (Render Web Service)

## រចនាសម្ព័ន្ធ Project

```
├── bot.py                      # Telegram Bot - ផ្ញើ/ទទួលសារ
├── webapp.py                   # Flask Web Server - Admin API
├── main.py                     # Entry point
├── start.sh                    # Script ដំណើរការ bot + webapp
├── Dockerfile                  # Docker configuration
├── render.yaml                 # Render deployment configuration
├── requirements.txt            # Python dependencies
├── static/
│   └── index.html              # Mini App Admin Dashboard
├── groups.json.example         # Template
├── user_groups.json.example    # Template
├── pending_schedules.json.example
├── scheduled_messages.json.example
└── settings.json.example
```

---

## 🚀 Deploy ជាមួយ Render (Docker)

### ជំហានទី 1: Push Code ទៅ GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### ជំហានទី 2: បង្កើត Web Service នៅ Render

1. ចូល [https://render.com](https://render.com) → **New** → **Web Service**
2. ភ្ជាប់ GitHub repository
3. ជ្រើស **Language: Docker**
4. Render នឹង detect `Dockerfile` ដោយស្វ័យប្រវត្តិ

### ជំហានទី 3: កំណត់ Environment Variables

នៅក្នុង Render Dashboard → **Environment** → បន្ថែម:

| Variable | តម្លៃ |
|----------|--------|
| `TELEGRAM_BOT_TOKEN` | Token ពី @BotFather |
| `WEBAPP_URL` | `https://YOUR-APP.onrender.com` |
| `ADMIN_ID` | Telegram User ID របស់ Admin |

### ជំហានទី 4: Deploy

ចុច **Deploy Web Service** — Render នឹង build Docker image ហើយ deploy ដោយស្វ័យប្រវត្តិ

---

## 💻 Run ក្នុង Local

### ១. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### ២. Initialize Data Files

```bash
cp groups.json.example groups.json
cp user_groups.json.example user_groups.json
cp pending_schedules.json.example pending_schedules.json
cp scheduled_messages.json.example scheduled_messages.json
```

### ៣. Set Environment Variables

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export WEBAPP_URL="https://your-app.onrender.com"
export ADMIN_ID="your_telegram_user_id"
```

### ៤. Install Dependencies

```bash
pip install -r requirements.txt
```

### ៥. Start

```bash
bash start.sh
```

---

## API Endpoints

| Method | Endpoint | ការប្រើប្រាស់ |
|--------|----------|----------------|
| GET | `/` | Admin Dashboard |
| GET | `/api/groups` | ទទួល Groups ទាំងអស់ |
| POST | `/api/schedule` | បង្កើត Schedule ថ្មី |
| GET | `/api/scheduled` | ទទួល Schedules ទាំងអស់ |
| DELETE | `/api/scheduled/<id>` | លុប Schedule |
| GET | `/api/all-groups` | ទទួល Groups ទាំងអស់ (Admin) |

## Environment Variables

| Variable | ការប្រើប្រាស់ | Required |
|----------|----------------|----------|
| `TELEGRAM_BOT_TOKEN` | Token Bot ពី @BotFather | ✅ |
| `WEBAPP_URL` | URL Mini App Web Server | ✅ |
| `ADMIN_ID` | Telegram User ID of Admin | ✅ |
