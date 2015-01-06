import json

from django.http import Http404
from django.http import HttpResponse

from workout_generator.constants import Equipment
from workout_generator.constants import Goal
from workout_generator.mailgun.tasks import send_verify_email
from workout_generator.stripe.utils import create_subscription
from workout_generator.user.models import User


def render_to_json(response_obj, context={}, content_type="application/json", status=200):
    json_str = json.dumps(response_obj, indent=4)
    return HttpResponse(json_str, content_type=content_type, status=status)


def requires_post(fn):
    def inner(request, *args, **kwargs):
        if request.method != "POST":
            return Http404

        if 'username' not in request.POST:
            return render_to_json({
                "message": "POST requests require a Parse 'username'",
            }, status=400)

        username = request.POST['username']
        user = User.get_or_create_by_username(username)
        kwargs.update["user"] = user
        return fn(request, *args, **kwargs)
    return inner


@requires_post
def signup(request, user=None):
    email = request.POST['email']
    password = request.POST['password']
    placeholder(email, password)
    send_verify_email(email)
    return render_to_json({}, status=204)


def placeholder(*args, **kwargs):
    pass


def goals(request):
    return render_to_json(Goal.as_json())


def equipment(request):
    return render_to_json(Equipment.as_json())


def user(request):
    if request.method == "POST":
        return _update_user(request)
    else:
        return _get_user(request)


@requires_post
def _update_user(request, user=None):
    field_to_function = {
        'goal_id': _update_goal,
        'equipment_ids': _update_equipment_ids,
        'available_days': _update_available_days,
        'minutes_per_day': _update_minutes_per_day,
        'fitness_level': _update_fitness_level,
        'experience': _update_experience
    }

    for field, function in field_to_function.items():

        if function is None:
            continue

        if field in request.POST:
            function(user, request.POST[field])

    return render_to_json({}, status=204)


def _get_user(request):
    return render_to_json({})


def _update_goal(user, goal_id):
    user.update_goal_id(goal_id)


def _update_equipment_ids(user, equipment_id_list):
    user.update_equipment_ids(equipment_id_list)


def _update_available_days(user, js_isoweekday_list):
    user.update_available_days(js_isoweekday_list)


def _update_minutes_per_day(user, minutes_per_day):
    user.update_minutes_per_day(minutes_per_day)


def _update_fitness_level(user, fitness_level_id):
    user.update_fitess_level(fitness_level_id)


def _update_experience(user, experience_id):
    user.update_experience(experience_id)


@requires_post
def payment(request, user=None):
    stripe_token = request.POST['tokenId']
    stripe_email = request.POST['tokenEmail']
    success, customer_id_or_message = create_subscription(stripe_token, stripe_email)
    if not success:
        return render_to_json({
            "error": customer_id_or_message
        }, status=400)

    user.update_stripe_customer_id(customer_id_or_message)

    return render_to_json({}, status=204)
