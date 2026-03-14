import os
from pathlib import Path
from dotenv import load_dotenv

# ── Base ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-key-cambiar-en-produccion")
DEBUG       = os.environ.get("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# ── Apps instaladas ───────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "apps.employees",
    "apps.vacations",
    "apps.payroll",
]

# ── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF     = "gym_payroll.urls"
WSGI_APPLICATION = "gym_payroll.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]
    },
}]

# ── Base de datos — PostgreSQL ────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.postgresql",
        "NAME":     os.environ.get("DB_NAME",     "gym_payroll_db"),
        "USER":     os.environ.get("DB_USER",     "gym_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "gym_password"),
        "HOST":     os.environ.get("DB_HOST",     "127.0.0.1"),
        "PORT":     os.environ.get("DB_PORT",     "5432"),
    }
}

# ── Internacionalización ──────────────────────────────────────────────────────
LANGUAGE_CODE = "es-mx"
TIME_ZONE     = "America/Mexico_City"
USE_I18N      = True
USE_TZ        = True

STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Django REST Framework ─────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES":   ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES":     ["rest_framework.parsers.JSONParser"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_PAGINATION_CLASS":   "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]
CORS_ALLOW_ALL_ORIGINS = DEBUG