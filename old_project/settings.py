# Django settings for mysite project.

DEBUG = False
#DEBUG = True
TEMPLATE_DEBUG = DEBUG

FACEBOOK_API_KEY='bc11070e702fa796baa1251f0b14670c'
FACEBOOK_SECRET_KEY='3f1dcb0261e666130d6e92ad17a6c705'
SESSION_SAVE_EVERY_REQUEST=True
SESSION_ENGINE='django.contrib.sessions.backends.cached_db'
#SESSION_ENGINE='django.contrib.sessions.backends.cached'
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'aesg'             # Or path to database file if using sqlite3.
DATABASE_USER = 'aesg'             # Not used with sqlite3.
DATABASE_PASSWORD = 'CombatLoad!@#123'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = 'America/Chicago'
TIME_ZONE='Pacific/Pago_Pago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = '/home/lobdellbrothers/domains/oraclefitness.com/public_html/'
#
MEDIA_ROOT = '/home/aesg/webapps/staticserve'
#MEDIA_ROOT = '/home/slobdell/webapps/oraclefitness/myproject/public_html/'
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://www.cyber-trainer.com'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '(j+4crc-=0eddp(7s7r8uvf0*4ub2w4mdvvw73qz_&v21b%mjr'
#SECRET_KEY='mystuffwasnotworkingearlierletstrywithnospecialcharacter'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'oraclefitness.FacebookConnectMiddleware.FacebookConnectMiddleware',
#    'facebook.djangofb.FacebookMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
#    'django.middleware.cache.UpdateCacheMiddleware',
#    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'myproject.urls'

TEMPLATE_DIRS = (
    "/home/aesg/webapps/cybertrainer/myproject/templates"
#    "/home/lobdellbrothers/domains/oraclefitness.com/djangoproject/templates"
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
#EMAIL_HOST_USER='kutoken'
EMAIL_USE_TLS = True
EMAIL_HOST='smtp.gmail.com'
EMAIL_HOST_USER = 'scott@workoutgenerator.net'

EMAIL_HOST_PASSWORD='seaweed1'
EMAIL_PORT=587
DEFAULT_FROM_EMAIL='scott@workoutgenerator.net'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'myproject.oraclefitness',
    
#    'south',
#    'registration',
#    'base',
#    'kutoken_extensions',
)

SOUTH_AUTO_FREEZE_APP=True
#CACHE_BACKEND='memcached://unix:/home/aesg/memcached.sock'
LOGIN_URL='/login/'
