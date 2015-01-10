from django.utils import unittest
from workout_generator.workout.generator import _mandate_cardio_or_resistance
from workout_generator.workout.generator import _generate_day_frameworks
from workout_generator.workout.models import _DayFramework__WorkoutComponent
from workout_generator.workout.models import _DayFramework
from workout_generator.user.models import User


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
        user = User.get_or_create_by_username("weekframework")
        user.update_goal_id(1)
        user.move_to_next_week()
        initial_workout_component_count = _DayFramework__WorkoutComponent.objects.count()
        _generate_day_frameworks(user)
        final_workout_component_count = _DayFramework__WorkoutComponent.objects.count()
        self.assertEqual(final_workout_component_count - initial_workout_component_count, 14)
        isoweekdays = _DayFramework.objects.filter(user_id=user.id).values_list('js_isoweekday', flat=True)
        self.assertEqual(set(isoweekdays), set(range(7)))
