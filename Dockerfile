FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv
RUN yes | uv sync
ENV PATH="/app/.venv/bin:$PATH"
RUN pip install --no-cache-dir gunicorn

COPY . /app

WORKDIR /app

CMD ["gunicorn", "hotel.wsgi:application", "--bind", "0.0.0.0:8000"]
