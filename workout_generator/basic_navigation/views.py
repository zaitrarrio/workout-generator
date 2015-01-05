import json
import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response

from workout_generator.stripe.constants import get_publishable_key


def render_to_json(data, status=200):
    return HttpResponse(json.dumps(data), content_type="application/json", status=status)


def home(request):
    render_data = {
        "dev": True if os.environ.get("I_AM_IN_DEV_ENV") else False,
        "publishable_key": get_publishable_key(),
        "facebook_app_id": settings.FACEBOOK_APP_ID,
        "parse_app_id": settings.PARSE_APP_ID,
        "parse_key": settings.PARSE_KEY
    }
    return render_to_response("basic_navigation/base.html", render_data)


def sitemap(request):
    with open("workout_generator/templates/sitemap.xml", "rb") as f:
        xml_content = f.read()
    return HttpResponse(xml_content, content_type="text/xml")
