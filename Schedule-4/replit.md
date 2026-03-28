# Telegram Mini App Project

## Overview

A Telegram Bot with a Mini App (WebApp) that displays user profile information in Khmer language.

## Stack

- **Language**: Python 3.11
- **Bot Framework**: python-telegram-bot >= 22.7
- **Web Framework**: Flask >= 3.0.0
- **Package Manager**: uv
- **Frontend**: Plain HTML/CSS/JS with Telegram WebApp JS API

## Structure

```text
/
├── bot.py              # Telegram bot (sends /start with WebApp button)
├── webapp.py           # Flask web server (serves the Mini App HTML)
├── static/
│   └── index.html      # Telegram Mini App frontend
├── pyproject.toml      # Python dependencies
└── uv.lock             # Dependency lockfile
```

## Workflows

- **Telegram Bot**: Runs `python3 bot.py` — handles bot commands
- **Mini App Web Server**: Runs `python3 webapp.py` on port 3000 — serves the Mini App HTML

## Environment Variables

- `TELEGRAM_BOT_TOKEN` (secret): The bot token from @BotFather
- `WEBAPP_URL` (shared): Public HTTPS URL of the Mini App web server

## Features

- `/start` command sends a greeting in Khmer with a WebApp button
- Mini App opens and displays:
  - Greeting: "សួស្តី [user's first name]"
  - Profile card with name, Telegram ID, username
  - Language code info
  - Avatar initials or photo
