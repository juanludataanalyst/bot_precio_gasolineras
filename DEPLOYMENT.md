# Deployment Guide

## Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment:
```bash
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN
```

4. Run the bot:
```bash
python -m src.bot.main
```

## Railway Deployment

1. Create a new project on Railway
2. Connect this repository
3. Add environment variable: `TELEGRAM_BOT_TOKEN`
4. Deploy

## Render Deployment

1. Create a new Web Service on Render
2. Connect this repository
3. Add environment variable: `TELEGRAM_BOT_TOKEN`
4. Set start command: `python -m src.bot.main`
5. Deploy

## Docker Deployment

1. Build image:
```bash
docker build -t bot-precio-gasolineras .
```

2. Run container:
```bash
docker run -d --name gasolineras-bot --env-file .env bot-precio-gasolineras
```

Or use docker-compose:
```bash
docker-compose up -d
```
