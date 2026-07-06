FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Render provides $PORT at runtime; default to 5000 for local Docker runs.
EXPOSE 5000

# Bind to $PORT so Render can route traffic (falls back to 5000 locally).
CMD gunicorn -w ${WEB_CONCURRENCY:-1} -b 0.0.0.0:${PORT:-5000} --timeout 120 --access-logfile - --error-logfile - wsgi:app
