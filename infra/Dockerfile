FROM python:3.12-slim

WORKDIR /app

# Install production dependencies only
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy application source
COPY app/ ./app/
COPY run.py ./

# Create runtime directories
RUN mkdir -p data logs

# Run as non-root
RUN useradd --no-create-home --shell /bin/false appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:api", "--host", "0.0.0.0", "--port", "8000"]
