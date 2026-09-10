import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    MAX_UPLOAD_SIZE_MB=(int, 20),
    GROQ_LLM_MODEL=(str, "llama-3.3-70b-versatile"),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-dev-only")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", default="*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "apps.core",
    "apps.accounts",
    "apps.organizations",
    "apps.telephony",
    "apps.agents",
    "apps.campaigns",
    "apps.leads",
    "apps.calls",
    "apps.jobs",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

AUTH_USER_MODEL = "accounts.User"

DATABASES = {"default": env.db("DATABASE_URL", default="sqlite:///" + str(BASE_DIR / "db.sqlite3"))}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.core.auth.OrganizationTokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "apps.core.permissions.IsOrganizationMember",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "EXCEPTION_HANDLER": "apps.core.exceptions.exception_handler",
}

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS", default="http://localhost:5173").split(",")

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CREDENTIAL_ENCRYPTION_KEY = env("CREDENTIAL_ENCRYPTION_KEY", default="")
INTERNAL_SIGNING_KEY = env("INTERNAL_SIGNING_KEY", default=SECRET_KEY)

S3_ENDPOINT_URL = env("S3_ENDPOINT_URL", default="")
if S3_ENDPOINT_URL and not S3_ENDPOINT_URL.startswith(("http://", "https://")):
    S3_ENDPOINT_URL = f"https://{S3_ENDPOINT_URL}"
S3_REGION = env("S3_REGION", default="")
S3_ACCESS_KEY_ID = env("S3_ACCESS_KEY_ID", default="")
S3_SECRET_ACCESS_KEY = env("S3_SECRET_ACCESS_KEY", default="")
S3_BUCKET_NAME = env("S3_BUCKET_NAME", default="")

QSTASH_TOKEN = env("QSTASH_TOKEN", default="")
QSTASH_CURRENT_SIGNING_KEY = env("QSTASH_CURRENT_SIGNING_KEY", default="")
QSTASH_NEXT_SIGNING_KEY = env("QSTASH_NEXT_SIGNING_KEY", default="")
QSTASH_INLINE = env.bool("QSTASH_INLINE", default=DEBUG)
PUBLIC_BASE_URL = env("PUBLIC_BASE_URL", default="http://localhost:8000")

GROQ_API_KEY = env("GROQ_API_KEY", default="")
GROQ_LLM_MODEL = env("GROQ_LLM_MODEL")
GROQ_REASONING_EFFORT = env("GROQ_REASONING_EFFORT", default="low")

LIVEKIT_SIP_URI = env("LIVEKIT_SIP_URI", default="")

MAX_UPLOAD_SIZE_MB = env("MAX_UPLOAD_SIZE_MB")