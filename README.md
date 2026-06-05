<div align="center">

# Barter PATH
[![Python](https://img.shields.io/badge/Python-1F2937?style=for-the-badge&logo=python&logoColor=FFFFFF)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/aiogram-1F2937?style=for-the-badge&logo=telegram&logoColor=FFFFFF)](https://aiogram.dev/)
[![Aiogram-i18n](https://img.shields.io/badge/aiogram--i18n-1F2937?style=for-the-badge&logo=googletranslate&logoColor=FFFFFF)](https://github.com/aiogram/i18n)
[![SqlAlchemy](https://img.shields.io/badge/SQLAlchemy-1F2937?style=for-the-badge&logo=sqlalchemy&logoColor=FFFFFF)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/Postgres-1F2937?style=for-the-badge&logo=postgresql&logoColor=FFFFFF)](https://www.postgresql.org/)
[![Alembic](https://img.shields.io/badge/Alembic-1F2937?style=for-the-badge)](https://github.com/sqlalchemy/alembic)

An automated Stalcraft barter tracker providing real-time resource calculations, discount management, and progression monitoring via official database.

</div>

## Features
- 🤖 Telegram bot interface
- 🛠️ Task management system
- 📊 Real-time barter calculations
- 🌍 Multi-language support (i18n)

## Project Structure
```text
├── migrations/                # Alembic Migrations
├── src/
│   ├── bot/
│   │   ├── handlers/          # Bot handlers
│   │   ├── keyboard/          # Keyboads & callback factories
│   │   │   ├── callback_data.py
│   │   │   ├── inline.py
│   │   ├── middlewares/       # DB & i18n middlewares
│   │   │   ├── db.py
│   │   │   ├── i18n.py
│   │   ├── utils/             # States, UI helpers
│   │   │   ├── states.py
│   │   │   ├── ui.py
│   │   ├── main.py            # Bot entry point
│   ├── db/
│   │   ├── base.py
│   │   ├── models.py
│   │   ├── repo.py
│   ├── locales/               # Translations
│   │   ├── ru/
│   │   ├── en/
│   ├── services/
│   │   ├── stalcraft_api.py
│   │   ├── updater.py
│   ├── __main__.py            # Application launcher
│   ├── config.py              # Environment config loader
```

## Getting Started
### 1. Clone repository
```bash
git clone https://github.com/TheC0rX/barter-path.git
cd barter-path
```

### 2. Install dependencies
```bash
poetry install
```

### 3. Environment setup
Copy `.env.example` to `.env` and fill in the required values.
```env
BOT_TOKEN=BOT_TOKEN
GITHUB_TOKEN=PAT_TOKEN
DB_URL=postgresql+asyncpg://DB_USER:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME
```

### 4. Run database migrations
```bash
poetry run alembic upgrade head
```

### 5. Run application
```bash
poetry run python -m src
```