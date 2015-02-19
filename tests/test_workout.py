from collections import defaultdict

from django.utils import unittest

from workout_generator.constants import Exercise
from workout_generator.constants import Goal
from workout_generator.workout.generator import _mandate_cardio_or_resistance
from workout_generator.workout.generator import _generate_day_frameworks
from workout_generator.workout.generator import generate_new_workouts
from workout_generator.workout.models import _DayFramework__WorkoutComponent
from workout_generator.workout.models import _DayFramework
from workout_generator.user.models import User
from workout_generator.workout.utils import evenly_distribute_exercises_by_muscle_group


class WorkoutTestCase(unittest.TestCase):
    def setUp(self):
        super(WorkoutTestCase, self).setUp()

    def test_mandate_cardio_or_resistance(self):
        isoweekday_to_components = {
            1: [1, 2, 3, 5],
            2: [1, 2, 3, 5],
            3: [1, 2, 3, 5],
        }
        isoweekday_to_cardio_intensity = {
            1: 1,
            2: 2,
            3: 3,
        }
        args = (
            isoweekday_to_components,
            isoweekday_to_cardio_intensity,
        )
        expected_1 = isoweekday_to_components.copy()
        expected_2 = isoweekday_to_cardio_intensity.copy()
        _mandate_cardio_or_resistance(*args)
        self.assertDictEqual(expected_1, isoweekday_to_components)
        self.assertDictEqual(expected_2, isoweekday_to_cardio_intensity)

        isoweekday_no_resistance = {
            1: [1, 2, 3],
            2: [1, 2, 3, 5],
            3: [1, 2, 3, 5],
        }
        isoweekday_no_cardio = {
            2: 1,
            3: 1
        }
        args = (
            isoweekday_no_resistance,
            isoweekday_no_cardio
        )
        _mandate_cardio_or_resistance(*args)
        self.assertIn(1, isoweekday_no_cardio)

    def test_no_exception_generate_framework(self):
        _, user = User.get_or_create_by_username("weekframework")
        user.update_goal_id(1)
        user.move_to_next_week()
        initial_workout_component_count = _DayFramework__WorkoutComponent.objects.count()
        day_framework_collection = _generate_day_frameworks(user)
        final_workout_component_count = _DayFramework__WorkoutComponent.objects.count()
        self.assertEqual(final_workout_component_count - initial_workout_component_count, 14)
        isoweekdays = _DayFramework.objects.filter(user_id=user.id).values_list('js_isoweekday', flat=True)
        self.assertEqual(set(isoweekdays), set(range(7)))

        total_cardio = 0
        for day in xrange(7):
            total_cardio += day_framework_collection.get_cardio_for_day_index(day) or 0
        self.assertGreater(total_cardio, 0)

        total_components = []
        for day in xrange(7):
            workout_component_list = day_framework_collection.get_workout_components_for_day_index(day)
            total_components += workout_component_list
        self.assertEqual(len(total_components), 14)

    def test_generate_workouts(self):
        _, user = User.get_or_create_by_username("workoutdude")
        user.update_goal_id(1)
        user.move_to_next_week()
        workout_collection = generate_new_workouts(user)

    def test_all_goals_no_exceptions(self):
        # with open("output.json", "w+") as f:
        total = 0
        bad = 0
        for fitness_level in xrange(1, 6):
            for experience in xrange(1, 6):
                for goal_id in Goal.IDS:
                    _, user = User.get_or_create_by_username("workoutdude%s_%s_%s" % (fitness_level, experience, goal_id))
                    # user = User.get_or_create_by_username("workoutdude%s" % goal_id)
                    user.update_goal_id(goal_id)
                    # user.update_fitness_level(fitness_level)
                    # user.update_experience(experience)
                    for week_count in xrange(10):
                        user.move_to_next_week()
                        workout_collection = generate_new_workouts(user)
                        for workout in workout_collection.get_existing_workouts_for_user(user):
                            total += 1
                            empty_cardio = workout.cardio_session is None
                            empty_exercises = len(workout._get_workout_component_to_exercises()) == 0
                            if empty_cardio and empty_exercises:
                                # problem here: the database is populated with a
                                # framework, but exercises empty I guess
                                print "EMPTY DATA"
                                bad += 1
                                # raise ValueError("there's empty data")
            # import json
            # f.write(json.dumps(workout_collection.to_json(), indent=4))
        print "%s/%s" % (bad, total)

    def test_evenly_distribute_exercises_by_muscle_group(self):
        exercise_list = Exercise().query
        distributed_exercise_list = evenly_distribute_exercises_by_muscle_group(exercise_list)
        muscle_group_counts = defaultdict(int)
        for exercise in distributed_exercise_list:
            muscle_group_counts[exercise.muscle_group_id] += 1
        for count in muscle_group_counts.values():
            self.assertEqual(count, 100)
