# tg-inv

Telegram bot for collecting inventory service cards using MongoDB.

## Features
- Admin can add service names with `/add`.
- Users receive a random incomplete card and fill missing fields.
- Input text is parsed into card fields via a simple LLM placeholder.
- Users confirm parsed fields before saving to the database.

## Running
1. Install requirements: `pip install -r requirements.txt`.
2. Set environment variables:
   - `TELEGRAM_TOKEN` – token of your Telegram bot.
   - `MONGO_URL` – MongoDB connection string.
   - `DB_NAME` – database name (default `tg_inv`).
3. Start the bot: `python -m bot.bot`.

## Testing
Run tests with:
```bash
pytest
```
