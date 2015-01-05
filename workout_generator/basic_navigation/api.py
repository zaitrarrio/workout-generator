import json

from django.http import Http404
from django.http import HttpResponse

from workout_generator.constants import Equipment
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


def equipment(request):
    return render_to_json(Equipment.as_json())


def user(request):
    if request.method == "POST":
        return _update_user(request)
    else:
        return _get_user(request)


def _update_user(request):
    user_id = 999 or request.session["user_id"]

    if 'goal_id' in request.POST:
        _update_goal(user_id, int(request.POST['goal_id']))

    return render_to_json({}, status=204)


def _get_user(request):
    return render_to_json({})


def _update_goal(user_id, goal_id):
    pass


@requires_post
def payment(request):
    return
    '''
    AMOUNT_TO_CHARGE = 5.00
    user_id = request.session['user_id']
    user = User.get_by_id(request.session['user_id'])
    stripe_token = request.POST['tokenId']
    stripe_email = request.POST['tokenEmail']
    success, error_message = charge_card(stripe_token, int(AMOUNT_TO_CHARGE * 100), user_id, stripe_email)
    if not success:
        return render_to_json({
            "error": error_message
        }, status=400)
    user.add_credits(AMOUNT_TO_CHARGE)
    return render_to_json(user.to_json())
    '''
