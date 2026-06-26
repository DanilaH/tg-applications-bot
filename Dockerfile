FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml requirements.txt ./
COPY src/ ./src/

RUN pip install --no-cache-dir -r requirements.txt -e .

CMD ["python", "-m", "bot.main"]