import json

from django.http import Http404
from django.http import HttpResponse

from workout_generator.basic_navigation.constants import ResponseCodes
from workout_generator.constants import Equipment
from workout_generator.constants import Goal
from workout_generator.mailgun.tasks import send_verify_email
from workout_generator.stripe.utils import create_subscription
from workout_generator.user.models import User
from workout_generator.workout.exceptions import NeedsNewWorkoutsException
from workout_generator.user.exceptions import NoGoalSetException
from workout_generator.workout.models import WorkoutCollection
from workout_generator.workout.generator import generate_new_workouts


def render_to_json(response_obj, context={}, content_type="application/json", status=200):
    json_str = json.dumps(response_obj, indent=4)
    return HttpResponse(json_str, content_type=content_type, status=status)


def requires_post(fn):
    def inner(request, *args, **kwargs):
        if request.method != "POST":
            return Http404

        post_data = request.POST or json.loads(request.body)
        if 'username' not in post_data:
            return render_to_json({
                "message": "POST requests require a Parse 'username'",
            }, status=400)

        username = post_data['username']
        user = User.get_or_create_by_username(username)
        kwargs["user"] = user
        return fn(request, *args, **kwargs)
    return inner


@requires_post
def signup(request, user=None):
    post_data = request.POST or json.loads(request.body)
    email = post_data['email']
    placeholder(email)
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
        'age': _update_age,
        'gender': _update_gender,
        'equipment_ids': _update_equipment_ids,
        'enabled_days': _update_available_days,
        'minutes_per_day': _update_minutes_per_day,
        'fitness_level': _update_fitness_level,
        'experience': _update_experience
    }

    post_data = request.POST or json.loads(request.body)
    for field, function in field_to_function.items():

        if function is None:
            continue

        if field in post_data:
            function(user, post_data[field])

    return render_to_json({}, status=204)


def _get_user(request):
    username = request.GET["username"]
    user = User.get_by_username(username)
    if not user:
        return render_to_json({}, status=400)
    return render_to_json(user.to_json())


def _update_goal(user, goal_id):
    user.update_goal_id(goal_id)


def _update_equipment_ids(user, equipment_id_list):
    user.update_equipment_ids(equipment_id_list)


def _update_available_days(user, js_isoweekday_list):
    user.update_available_days(js_isoweekday_list)


def _update_minutes_per_day(user, minutes_per_day):
    minutes_per_day = int(minutes_per_day)
    user.update_minutes_per_day(minutes_per_day)


def _update_fitness_level(user, fitness_level_id):
    fitness_level_id = int(fitness_level_id)
    user.update_fitness_level(fitness_level_id)


def _update_experience(user, experience_id):
    experience_id = int(experience_id)
    user.update_experience(experience_id)


def _update_gender(user, canonical_gender_name):
    user.update_gender(canonical_gender_name)


def _update_age(user, age):
    age = int(age)
    user.update_age(age)


@requires_post
def payment(request, user=None):
    post_data = request.POST or json.loads(request.body)
    stripe_token = post_data['tokenId']
    stripe_email = post_data['tokenEmail']
    success, customer_id_or_message = create_subscription(stripe_token, stripe_email)
    if not success:
        return render_to_json({
            "error": customer_id_or_message
        }, status=400)

    user.update_stripe_customer_id(customer_id_or_message)

    return render_to_json({}, status=204)


def workout(request):
    '''
    return a week's worth of data for the user
    '''
    username = request.GET["username"]
    # TODO add some better authentication here
    user = User.get_by_username(username)
    if not user:
        return render_to_json({}, status=400)
    try:
        workout_collection = WorkoutCollection.for_user(user)
    except NeedsNewWorkoutsException:
        try:
            workout_collection = generate_new_workouts(user)
        except NoGoalSetException:
            return render_to_json({
                "redirect": "!goal/return"
            }, status=ResponseCodes.REDIRECT_REQUIRED)
    return render_to_json(workout_collection.to_json())
