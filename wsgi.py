"""
WSGI entry point for production servers (Gunicorn, uWSGI, etc.)

Usage:
  gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
  gunicorn --workers 4 --worker-class sync --bind 0.0.0.0:5000 wsgi:app
"""
import os
import logging
from app import app

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    # This should only run via Gunicorn in production
    app.run()
