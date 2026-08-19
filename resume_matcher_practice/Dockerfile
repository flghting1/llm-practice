FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY match_schema.py .
COPY matcher.py .
COPY resume_api.py .

EXPOSE 8005

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8005/health', timeout=3)"

CMD ["uvicorn", "resume_api:app", "--host", "0.0.0.0", "--port", "8005"]