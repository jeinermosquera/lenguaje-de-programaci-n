# wsgi.py — punto de entrada para servidores WSGI de producción (gunicorn, waitress, etc.)
# Uso local: python app.py  |  Uso producción: waitress-serve --listen=0.0.0.0:8000 wsgi:application
import os

os.environ.setdefault("FLASK_DEBUG", "false")

from app import app as application

if __name__ == "__main__":
    application.run()
