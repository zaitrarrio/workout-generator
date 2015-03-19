# pip install pycallgraph

from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
from workout_generator.user.models import User
from workout_generator.workout.generator import generate_new_workouts
user = User.get_by_username("scott.lobdell@gmail.com")
with PyCallGraph(output=GraphvizOutput()):
    generate_new_workouts(user)
