import json

from django.http import Http404
from django.http import HttpResponse

from workout_generator.constants import Goal
from workout_generator.mailgun.tasks import send_verify_email


def render_to_json(response_obj, context={}, content_type="application/json", status=200):
    json_str = json.dumps(response_obj, indent=4)
    return HttpResponse(json_str, content_type=content_type, status=status)


def requires_post(fn):
    def inner(request, *args, **kwargs):
        if request.method != "POST":
            return Http404
        return fn(request, *args, **kwargs)
    return inner


@requires_post
def signup(request):
    email = request.POST['email']
    password = request.POST['password']
    placeholder(email, password)
    send_verify_email(email)
    return render_to_json({}, status=204)


def placeholder(*args, **kwargs):
    pass


def goals(request):
    return render_to_json(Goal.as_json())
