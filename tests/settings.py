import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


TEMPLATE_DEBUG = True


class HighlightBrokenVariable:
    def __contains__(self, item):
        return True

    def __mod__(self, other):
        raise Exception(f'Tried to render non-existent variable {other}')


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': TEMPLATE_DEBUG,
            'string_if_invalid': HighlightBrokenVariable(),
        }
    },
]

SECRET_KEY = "foobar"
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'iommi',
    'shortner',
    'tests',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

MIDDLEWARE = [
    'iommi.middleware',
]

ROOT_URLCONF = 'shortner.urls'