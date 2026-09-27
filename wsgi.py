"""WSGI entry point used by gunicorn in production: `gunicorn wsgi:app`."""

from app import create_app

app = create_app()
