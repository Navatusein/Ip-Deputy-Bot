# Ip-Deputy-Bot

Telegram bot for the Ip-Deputy project (aiogram 3, webhook mode).

## Configuration

Settings are read from environment variables (and a `.env` file), with `config/config.json` as a fallback.
Environment variables take precedence. See `.env.example` and `config/config.template.json`.

| Variable | Default | Description |
|---|---|---|
| `BOT_TOKEN` | — | Telegram bot token |
| `API_TOKEN` | — | Value of the `X-BOT-TOKEN` header |
| `API_URL` | — | Bot API base URL, including `/api/bot` |
| `API_TIMEOUT` | `10` | API request timeout, seconds |
| `FRONTEND_URL` | — | Frontend URL used for Web App buttons |
| `WEBHOOK_URL` | — | Public URL of the bot |
| `WEBHOOK_PATH` | `/bot-webhook` | Webhook path |
| `WEBHOOK_SECRET` | — | Webhook secret token |
| `WEBSERVER` | `0.0.0.0` | Listen host |
| `PORT` | `7540` | Listen port |
| `TIME_ZONE` | `Europe/Kyiv` | Time zone for schedules |
| `LOG_LEVEL` | `INFO` | Log level |
| `LOG_FILE` | empty | Optional rotating log file, logs always go to stdout |
| `CONFIG_FILE` | `config/config.json` | Path to the JSON fallback config |

## Running

```shell
pip install -r requirements.txt
pybabel compile -d locales -D default
python main.py
```

Docker:

```shell
docker build -t ip-deputy-bot .
docker run --env-file .env -p 7540:7540 ip-deputy-bot
```

## Translations

Ukrainian is the source language. Translations live in `locales/<lang>/LC_MESSAGES/default.po` (`ru`, `en`).
Only `.po` files are committed, `.mo` files are compiled during the Docker build.

Update translations after changing texts:

```shell
pybabel extract -F babel.cfg -k __ -k LocalizedText -o locales/messages.pot --no-location --sort-output .
pybabel update -i locales/messages.pot -d locales -D default
pybabel compile -d locales -D default --statistics
```

Then fill in empty and `fuzzy` entries in the `.po` files.

Add a new language:

```shell
pybabel init -i locales/messages.pot -d locales -D default -l <lang>
```

and add it to `SUPPORTED_LOCALES` in `bot/i18n.py` and to `LANGUAGE_OPTIONS` in `bot/handlers/menu_keyboards/settings_menu.py`.
