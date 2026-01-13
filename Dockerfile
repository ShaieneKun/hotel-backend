FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv
RUN uv sync --non-interactive

COPY . /app

WORKDIR /app

CMD ["gunicorn", "hotel.wsgi:application", "--bind", "0.0.0.0:8000"]
