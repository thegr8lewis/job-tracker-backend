# import os
# from pathlib import Path
# from dotenv import load_dotenv




# import environ
# import dj_database_url

# env = environ.Env()
# environ.Env.read_env()
# from dotenv import load_dotenv
# from corsheaders.defaults import default_headers

# load_dotenv()

# BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY = os.getenv('SECRET_KEY')

# # For local development you might want DEBUG = True
# DEBUG = True

# ALLOWED_HOSTS = [
#     'localhost',
#     '127.0.0.1',
#     'job-tracker-backend-ztii.onrender.com',
#     '.onrender.com',  # Allow all Render subdomains
# ]



# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'rest_framework',
#     'corsheaders',
#     'applications',
#     'stats',
#     'files',
# ]

# MIDDLEWARE = [
#      'corsheaders.middleware.CorsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     # 'corsheaders.middleware.CorsMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'config.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = 'config.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('DB_USER'),
#         'PASSWORD': os.getenv('DB_PASSWORD'),
#         'HOST': os.getenv('DB_HOST'),
#         'PORT': os.getenv('DB_PORT'),
#     }
# }

# # DATABASES = {
# #     'default': dj_database_url.config(
# #         default=os.environ.get("DATABASE_URL")
# #     )
# # }

# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]

# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'
# USE_I18N = True
# USE_TZ = True

# STATIC_URL = 'static/'
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # ---- REST framework: remove default authentication classes ----
# # This makes the API not enforce authentication by default.
# # IMPORTANT: keep an eye on security for production.
# REST_FRAMEWORK = {
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.AllowAny',
#     ],
#     # No default authentication classes — requests won't be authenticated by DRF
#     'DEFAULT_AUTHENTICATION_CLASSES': [],
# }

# CORS_ALLOW_HEADERS = list(default_headers) + [
#     'content-type',
#     'authorization',
# ]

# # Configure CORS
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "http://localhost:3001",
#     "https://jobtracker-frontendd.onrender.com",
#     "https://job-tracker-frontendd.onrender.com",  # Note the dash vs no dash
# ]

# # For development only - allows cookies
# CORS_ALLOW_CREDENTIALS = True

# # Required for CSRF with session auth (if later used)
# CSRF_TRUSTED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "https://jobtracker-frontendd.onrender.com",
#     "https://job-tracker-frontendd.onrender.com",
# ]


import os
from pathlib import Path
from dotenv import load_dotenv
import environ
import dj_database_url
from corsheaders.defaults import default_headers
from celery.schedules import crontab

env = environ.Env()
environ.Env.read_env()
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

# For local development you might want DEBUG = True
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'job-tracker-backend-ztii.onrender.com',
    '.onrender.com',  
]

# CRITICAL: corsheaders must be at the top of INSTALLED_APPS
INSTALLED_APPS = [
    'corsheaders',  # MUST BE FIRST
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'applications',
    'stats',
    'files',
]

# CRITICAL: CorsMiddleware must be at the top of MIDDLEWARE
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # MUST BE FIRST
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('DB_USER'),
#         'PASSWORD': os.getenv('DB_PASSWORD'),
#         'HOST': os.getenv('DB_HOST'),
#         'PORT': os.getenv('DB_PORT'),
#     }
# }

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get("DATABASE_URL")
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---- REST framework: remove default authentication classes ----
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
}

# ==================== CORS CONFIGURATION - CRITICAL FIX ====================
# Option 1: Allow ALL origins (recommended for development)
CORS_ALLOW_ALL_ORIGINS = True  # THIS IS THE KEY FIX

# Option 2: OR use specific origins (comment out the above line if using this)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "https://jobtracker-frontendd.onrender.com",
    "https://job-tracker-frontendd.onrender.com",
]

# Additional CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'access-control-allow-origin',
]

CORS_EXPOSE_HEADERS = [
    'content-type',
    'authorization',
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-user-uid",
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Required for CSRF with session auth
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://jobtracker-frontendd.onrender.com",
    "https://job-tracker-frontendd.onrender.com",
]

# Optional: If you still have issues, add these
CORS_PREFLIGHT_MAX_AGE = 86400
CORS_ALLOW_PRIVATE_NETWORK = True

# ==================== SECURITY SETTINGS ====================
# For production, you should set these:
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'


# Use local Redis or your Redis Cloud URL
# CELERY_BROKER_URL = "redis://localhost:6379/0"
# CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

# Celery beat (example schedule)
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    "fetch-jobs-daily-7am": {
        "task": "applications.tasks.fetch_jobs_daily",
        "schedule": crontab(minute=0, hour=7),  # every day at 07:00
    },
}

JOOBLE_API_KEY = os.environ.get("JOOBLE_API_KEY")
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY")
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
WORKABLE_TOKEN = os.environ.get("WORKABLE_TOKEN")

# Debug API key status
print(f"[DEBUG] JOOBLE_API_KEY: {'SET' if JOOBLE_API_KEY else 'NOT SET'}")
print(f"[DEBUG] ADZUNA_APP_ID: {'SET' if ADZUNA_APP_ID else 'NOT SET'}")
print(f"[DEBUG] ADZUNA_APP_KEY: {'SET' if ADZUNA_APP_KEY else 'NOT SET'}")