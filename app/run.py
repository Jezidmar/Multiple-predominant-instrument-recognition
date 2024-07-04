from flask import Flask
from app_config import PRODUCTION
from flask_app import app

if __name__ == "__main__":
    kw = {"host": "0.0.0.0"} if PRODUCTION else {"debug": True}
    app.run(**kw)
