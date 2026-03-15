"""
Django settings for config project.
"""
from pathlib import Path
import environ

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Load .env file ===
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(BASE_DIR / '.env')

# === Security ===
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = []

# === Installed Apps ===
INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
'rest_framework.authtoken',
    'channels',
    # Local apps
    'users',
    'documents',
    'nlp_engine',
    'notifications',    
'storages',


]

# === Middleware ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# === Templates ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# === Channel Layers (for in-app notifications) ===
ASGI_APPLICATION = 'config.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# === Database ===
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     env('DB_NAME'),
        'USER':     env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST':     env('DB_HOST'),
        'PORT':     env('DB_PORT'),
    }
}

# === Password validation ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === Internationalization ===
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# === Static files ===
STATIC_URL = 'static/'

# === Default primary key field type ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === Email Settings ===
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f"DLMS System <{env('EMAIL_HOST_USER')}>"

# === Twilio Settings ===
TWILIO_SID = env('TWILIO_SID')
TWILIO_TOKEN = env('TWILIO_TOKEN')
TWILIO_PHONE = env('TWILIO_PHONE')

# === DLMS Notification Settings ===
APP_BASE_URL = env('APP_BASE_URL')
INACTIVITY_THRESHOLD_DAYS = env.int('INACTIVITY_THRESHOLD_DAYS')
GRACE_PERIOD_DAYS = env.int('GRACE_PERIOD_DAYS')
VERIFICATION_EXPIRY_HOURS = env.int('VERIFICATION_EXPIRY_HOURS')


# === AWS S3 Storage ===
import storages

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID       = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY   = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME      = env('AWS_S3_REGION_NAME')

AWS_S3_CUSTOM_DOMAIN = (
    f"{env('AWS_STORAGE_BUCKET_NAME')}"
    f".s3.{env('AWS_S3_REGION_NAME')}.amazonaws.com"
)

AWS_LOCATION         = 'assets'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL      = None

# ── LAYER 1: AES-256 Server-Side Encryption ───────────────────
# Every file uploaded to S3 is automatically encrypted at rest
# using AES-256. This is free and requires no extra code.
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl':    'max-age=86400',
    'ServerSideEncryption': 'AES256',   # ← This is the key line
}

# Files are only accessible via signed URLs (expire after 1 hour)
AWS_QUERYSTRING_AUTH    = True
AWS_QUERYSTRING_EXPIRE  = 3600   # 1 hour in seconds



# === REST Framework Settings ===
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# === Field-Level Encryption ===
# Used to encrypt sensitive fields in the database
# (national ID, phone numbers, access codes)
FIELD_ENCRYPTION_KEY = env('FIELD_ENCRYPTION_KEY')


# === LAYER 3: HTTPS / Transit Encryption ===
# Forces all cookies to be sent over HTTPS only
# Active in production (when DEBUG=False)
if not DEBUG:
    SECURE_SSL_REDIRECT          = True
    SESSION_COOKIE_SECURE        = True
    CSRF_COOKIE_SECURE           = True
    SECURE_HSTS_SECONDS          = 31536000   # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD          = True
