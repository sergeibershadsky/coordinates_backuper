import os

from notifiers.logging import NotificationHandler

TELEGRAM_NOTIFY_TOKEN = os.environ.get("TELEGRAM_NOTIFY_TOKEN")
TELEGRAM_NOTIFY_CHAT_ID = int(os.environ.get("TELEGRAM_NOTIFY_CHAT_ID"))

params = {
    'token': TELEGRAM_NOTIFY_TOKEN,
    'chat_id': TELEGRAM_NOTIFY_CHAT_ID
}
notify_handler = NotificationHandler("telegram", defaults=params)
