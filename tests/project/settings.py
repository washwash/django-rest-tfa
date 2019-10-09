from configurations import Configuration


class Test(Configuration):
    SECRET_KEY = '=3%ghvfz*u%n77z8i-q1ep#38*&c=1a*++ua(35t5blvd!oxn3'

    DEBUG = True
    STATIC_URL = '/static/'

    HOST = 'test.host'

    MIDDLEWARE = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',

        #  activate TFA middleware
        'django_user_agents.middleware.UserAgentMiddleware',
        'django_rest_tfa.middleware.TwoFactorAuthMiddleware',
    ]
    TFA_ENABLED_AUTH_TYPES = [
        'email',
    ]
    #  default times in seconds
    TFA_CLIENT_AGE = 1209600  # 2 weeks
    TFA_TOKEN_AGE = 3600  # 60 min
    TFA_CLIENT_IDENTIFIERS = [
        'django_rest_tfa.client_identifiers.browser_version',
        'django_rest_tfa.client_identifiers.os_version',
        'django_rest_tfa.client_identifiers.ip_address'
    ]

    ROOT_URLCONF = 'project.urls'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test_tfa_db',
            'ATOMIC_REQUESTS': True,
            'AUTOCOMMIT': False
        }
    }

    AUTH_USER_MODEL = 'test_app.User'

    INSTALLED_APPS = [
        'django',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        'django_otp',
        'django_otp.plugins.otp_email',
        'django_user_agents',
        'django_rest_tfa',
        'test_app'
    ]

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
        },
    ]

    REST_FRAMEWORK = {
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
        )
    }
