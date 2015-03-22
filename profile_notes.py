# pip install pycallgraph
import django
django.setup()

from workout_generator.user.models import User
from workout_generator.workout.generator import generate_new_workouts
user = User.get_by_username("scott.lobdell@gmail.com")
generate_new_workouts(user)
