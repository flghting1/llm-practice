FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY create_database.py .
COPY sql_tool.py .
COPY sql_agent.py .
COPY sql_api.py .

RUN python create_database.py

EXPOSE 8003

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8003/health', timeout=3)"

CMD ["uvicorn", "sql_api:app", "--host", "0.0.0.0", "--port", "8003"]