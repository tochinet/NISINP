"""
Django settings for governanceplatform project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os

try:
    from governanceplatform import config  # type: ignore
except ImportError:  # pragma: no cover
    from governanceplatform import config_dev as config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

try:
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = config.SECRET_KEY
    HASH_KEY = config.HASH_KEY

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = config.DEBUG
    LOGGING = config.LOGGING
    LOG_DIRECTORY = config.LOG_DIRECTORY

    # Database
    # https://docs.djangoproject.com/en/3.2/ref/settings/#databases
    DATABASES = config.DATABASES

    ALLOWED_HOSTS = config.ALLOWED_HOSTS
    PUBLIC_URL = config.PUBLIC_URL
    REGULATOR_CONTACT = config.REGULATOR_CONTACT
    SITE_NAME = config.SITE_NAME

    EMAIL_HOST = config.EMAIL_HOST
    EMAIL_PORT = config.EMAIL_PORT
except AttributeError as e:
    print("Please check you configuration file for the missing configuration variable:")
    print(f"  {e}")
    exit(1)

try:
    CORS_ALLOWED_ORIGINS = config.CORS_ALLOWED_ORIGINS
    CORS_ALLOWED_ORIGIN_REGEXES = config.CORS_ALLOWED_ORIGIN_REGEXES
    CORS_ALLOW_METHODS = config.CORS_ALLOW_METHODS
except AttributeError:
    CORS_ALLOWED_ORIGINS = []
    CORS_ALLOWED_ORIGIN_REGEXES = []
    CORS_ALLOW_METHODS = []

try:
    if LOG_DIRECTORY:
        # if not logging in stdout
        os.makedirs(LOG_DIRECTORY, exist_ok=True)
except Exception as e:
    print("Impossible to create the log directory:")
    print(f"  {e}")
    exit(1)


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "governanceplatform",
    "regulator",
    "operateur",
    "drf_spectacular",
    "drf_spectacular_sidecar",  # required for Django collectstatic discovery
    "corsheaders",
    "django_bootstrap5",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "two_factor",
    "import_export",
    "parler",
]

context_processors = [
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
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
    "django.middleware.locale.LocaleMiddleware",
    "governanceplatform.middleware.proxyPortalMiddleware",
    "django_otp.middleware.OTPMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    context_processors.append("django.template.context_processors.debug")
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[:-1] + "1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]
    DEBUG_TOOLBAR_CONFIG = {
        "INTERCEPT_REDIRECTS": False,
        "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
        "RESULTS_CACHE_SIZE": 3,
        "SHOW_COLLAPSED": True,
        "SQL_WARNING_THRESHOLD": 100,
    }


ROOT_URLCONF = "governanceplatform.urls"

LOGIN_REDIRECT_URL = "/"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "templates",
            "theme/templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                "governanceplatform.context_processors.extra_content_for_all_templates",
            ],
        },
    },
]

WSGI_APPLICATION = "governanceplatform.wsgi.application"


DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# User Model

AUTH_USER_MODEL = "governanceplatform.User"

LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/account/login"

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
SITE_ID = 1

LANGUAGES = [
    ("en", "English"),
    ("fr", "Français"),
    ("nl", "Dutch"),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
    os.path.join(BASE_DIR, "theme/locale"),
]

# Email

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = os.path.join(BASE_DIR, "sent_emails")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "static")

STATIC_DIR = os.path.join(BASE_DIR, "static")

STATICFILES_DIRS = [
    STATIC_DIR,
    "theme/static",
]

# Used to get an access to the header on JS side.
CORS_EXPOSE_HEADERS = [
    "content-disposition",
]

# Default settings
BOOTSTRAP5 = {
    # The complete URL to the Bootstrap CSS file.
    # Note that a URL can be either a string
    # ("https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css"),
    # or a dict with keys `url`, `integrity` and `crossorigin` like the default value below.
    "css_url": {
        "url": "/static/npm_components/bootstrap/dist/css/bootstrap.min.css",
        "crossorigin": "anonymous",
    },
    # The complete URL to the Bootstrap bundle JavaScript file.
    "javascript_url": {
        "url": "/static/npm_components/bootstrap/dist/js/bootstrap.min.js",
        "crossorigin": "anonymous",
    },
    # The URL to the jQuery JavaScript file (full)
    "jquery_url": {
        "url": "/static/npm_components/jquery/dist/jquery.min.js",
        "crossorigin": "anonymous",
    },
    # The complete URL to the Bootstrap CSS theme file (None means no theme).
    "theme_url": None,
    # Put JavaScript in the HEAD section of the HTML document
    # (only relevant if you use bootstrap5.html).
    "javascript_in_head": False,
    # Wrapper class for non-inline fields.
    # The default value "mb-3" is the spacing as used by Bootstrap 5 example code.
    "wrapper_class": "mb-3",
    # Wrapper class for inline fields.
    # The default value is empty, as Bootstrap5 example code doesn't use a wrapper class.
    "inline_wrapper_class": "",
    # Label class to use in horizontal forms.
    "horizontal_label_class": "col-sm-2",
    # Field class to use in horizontal forms.
    "horizontal_field_class": "col-sm-10",
    # Field class used for horizontal fields withut a label.
    "horizontal_field_offset_class": "offset-sm-2",
    # Set placeholder attributes to label if no placeholder is provided.
    "set_placeholder": True,
    # Class to indicate required field (better to set this in your Django form).
    "required_css_class": "",
    # Class to indicate field has one or more errors (better to set this in your Django form).
    "error_css_class": "",
    # Class to indicate success, meaning the field has valid input
    # (better to set this in your Django form).
    "success_css_class": "",
    # Enable or disable Bootstrap 5 server side validation classes
    # (separate from the indicator classes above).
    "server_side_validation": True,
    # Renderers (only set these if you have studied the source and understand the inner workings).
    "formset_renderers": {
        "default": "django_bootstrap5.renderers.FormsetRenderer",
    },
    "form_renderers": {
        "default": "django_bootstrap5.renderers.FormRenderer",
    },
    "field_renderers": {
        "default": "django_bootstrap5.renderers.FieldRenderer",
    },
}

# Multinlingual DB parameter
PARLER_DEFAULT_LANGUAGE_CODE = "en"
PARLER_LANGUAGES = {
    1: (
        {
            "code": "en",
        },  # English
        {
            "code": "fr",
        },  # French
        {
            "code": "nl",
        },  # Dutch
    ),
    "default": {
        "fallbacks": ["en"],
        "hide_untranslated": False,
    },
}


# Import-export settings

IMPORT_EXPORT_IMPORT_PERMISSION_CODE = "import"
IMPORT_EXPORT_EXPORT_PERMISSION_CODE = "export"
IMPORT_EXPORT_ESCAPE_HTML_ON_EXPORT = True
IMPORT_EXPORT_ESCAPE_FORMULAE_ON_EXPORT = True
