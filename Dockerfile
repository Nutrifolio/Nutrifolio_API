FROM python:3.11.5-slim-bullseye

WORKDIR /backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.api.main:app", "--proxy-headers", "--forwarded-allow-ips='*'", "--host", "0.0.0.0", "--port", "8000"]
