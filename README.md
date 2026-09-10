<div align="center">

# <img src=".github/assets/images/logo.png" width="38" height="38" align="center" style="vertical-align: middle; margin-right: 8px; border-radius: 6px;" alt="Barter Path Logo"> Barter Path

[![Python](https://img.shields.io/badge/Python-1F2937?style=for-the-badge&logo=python&logoColor=FFFFFF)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/aiogram-1F2937?style=for-the-badge&logo=telegram&logoColor=FFFFFF)](https://aiogram.dev/)
[![I18n](https://img.shields.io/badge/aiogram--i18n-1F2937?style=for-the-badge&logo=googletranslate&logoColor=FFFFFF)](https://github.com/aiogram/i18n)
[![SqlAlchemy](https://img.shields.io/badge/SQLAlchemy-1F2937?style=for-the-badge&logo=sqlalchemy&logoColor=FFFFFF)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/Postgres-1F2937?style=for-the-badge&logo=postgresql&logoColor=FFFFFF)](https://www.postgresql.org/)
[![Alembic](https://img.shields.io/badge/Alembic-1F2937?style=for-the-badge)](https://github.com/sqlalchemy/alembic)

An automated Stalzone barter tracker providing real-time resource calculations, discount management, and progression monitoring via official database.

</div>

## Features

- 🤖 **Interactive Bot Control** — Easy navigation via inline keyboards.
- 🎒 **Stalzone Barter Tracker** — Add crafting goals (e.g., A-545) and track your progress.
- 📊 **Dynamic Loot Logging** — Log successfully extracted resources to instantly recalculate what is left.
- 🌍 **Multi-Language Support** — Full English and Russian localization via Fluent.

## Project Structure

```text
├── logs/                             # App logs
├── migrations/                       # DB migrations (Alembic)
├── src/                              # Source code
│   ├── bot/                          # Telegram bot core (aiogram)
│   ├── db/                           # Database module
│   ├── locales/                      # Localization (en/ru)
│   ├── services/                     # External APIs & background updating
│   ├── config.py                     # Config loader
│   └── __main__.py                   # Main entry point
├── .env.example                      # Env template
├── poetry.lock                       # Frozen dependencies log
└── pyproject.toml                    # Dependencies
```

## 🐳 Quick Start with Docker

### 1. Clone the repository

```bash
git clone https://github.com/TheC0rX/barter-path.git
cd barter-path
```

### 2. Environment setup

Copy `.env.example` to `.env` and fill in the required values.

```bash
cp .env.example .env
```

### 3. Run application

```bash
docker compose up --build
```
