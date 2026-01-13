# hotel-backend

Simple Django backend for a Hotel Reservations system.

Project layout: application code lives under `/src` so the Python package is `hotel`.

Install with `uv` (this repo contains `uv.lock`):

```bash
# install uv (if not installed)
pip install uv

# sync dependencies from pyproject.toml/uv.lock into a virtualenv
uv sync

# run migrations and start dev server
uv run -- .venv/bin/python manage.py migrate
uv run -- .venv/bin/python manage.py runserver
```

Run with Docker Compose:

```bash
docker-compose build
docker-compose run --rm web python manage.py migrate
docker-compose up -d
```

API endpoints:
- `POST /api/auth/register/` — register
- `POST /api/auth/token/` — obtain JWT (token will include extra user claims)
- `GET /api/rooms/` — list rooms
- `POST /api/reservations/` — create reservation (authenticated)

Celery tasks:
- `reservations.tasks.send_reservation_confirmation` — sends confirmation emails asynchronously
- `reservations.tasks.release_expired_reservations` — run daily via Celery Beat

