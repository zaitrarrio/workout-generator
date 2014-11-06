import os,sys

sys.path.append('/var/www/djangoproject')
sys.path.append('/var/www')

sys.path.append('/var/www/public_html')
os.environ['DJANGO_SETTINGS_MODULE'] = 'djangoproject.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
