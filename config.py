import os


class Config(object):
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "1924237703:AAEmCvxEQS8unVp4y_GOjkQC8n9eiBCE6Xk")

    APP_ID = int(os.environ.get("APP_ID", 7286764))

    API_HASH = os.environ.get("API_HASH", "a85651bde0b7c341ccffba9b2dad1979")

    UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL", "@movieserialsbymax")
