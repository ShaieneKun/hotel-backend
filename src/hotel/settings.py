"""
Django settings for hotel project (moved to src/).
"""
import os
from celery.schedules import crontab
from pathlib import Path
from datetime import timedelta

# repo root is two parents up from src/hotel/settings.py
BASE_DIR = Path(__file__).resolve().parents[2]

SECRET_KEY = "django-insecure-devkey"
DEBUG = True
ALLOWED_HOSTS = ["0.0.0.0", "*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_celery_beat",
    "django_celery_results",
    "reservations",
    'drf_spectacular',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hotel.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "hotel.wsgi.application"

# Database configuration
# Use environment variables if set (for Docker/devcontainer)
# Otherwise use SQLite for local development
DB_HOST = os.environ.get("DB_HOST")

if DB_HOST:
    # Docker or devcontainer - use PostgreSQL
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "hotel"),
            "USER": os.environ.get("DB_USER", "hotel"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "hotel_password"),
            "HOST": DB_HOST,
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
else:
    # Local development without Docker - use SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator", },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"

# REST Framework & JWT
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# Celery configuration
# Use environment variables if set (for Docker/devcontainer)
# Otherwise use localhost for local development
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")

CELERY_BROKER_URL = f"redis://{REDIS_HOST}:6379/0"
CELERY_RESULT_BACKEND = "django-db"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"


# Email (Mailpit)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "mailpit")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 1025))
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = "noreply@hotel.local"

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]


CELERY_BEAT_SCHEDULE = {
    "cleanup-expired-reservations": {
        "task": "reservations.tasks.cleanup_expired_reservations",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight
        "options": {"expires": 3600}
    },
    "mark-rooms-available-after-cleaning": {
        "task": "reservations.tasks.mark_rooms_available_after_cleaning",
        "schedule": crontab(hour="*/3", minute=0),  # Every 3 hours
        "options": {"expires": 600}
    },
}
