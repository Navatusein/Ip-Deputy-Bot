FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN addgroup -S bot && adduser -S -G bot -H -h /app bot

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pybabel compile -d locales -D default \
    && mkdir -p logs \
    && chown bot:bot logs

USER bot

EXPOSE 7540

CMD ["python", "main.py"]
