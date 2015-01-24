import os
import re

from django.http import HttpResponsePermanentRedirect


def requires_ssl(fn):
    def inner(request, *args, **kwargs):
        if os.environ.get("I_AM_IN_DEV_ENV"):
            return fn(request, *args, **kwargs)

        if request.is_secure() or 'HTTP_X_SSL_PROTOCOL' in request.META:
            return fn(request, *args, **kwargs)
        secure_url = make_https(request.build_absolute_uri())
        return HttpResponsePermanentRedirect(secure_url)

    return inner


def make_https(url):
    return re.sub('^\s*https?:', 'https:', url)
