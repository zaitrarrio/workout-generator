from django.utils import unittest
from workout_generator.user.exceptions import NoGoalSetException
from workout_generator.user.models import User
from workout_generator.user.models import _User


class UserTestCase(unittest.TestCase):

    def setUp(self):
        super(UserTestCase, self).setUp()

    def test_get_or_create_by_username(self):
        User.get_or_create_by_username("testuser@test.com")
        self.assertTrue(_User.objects.all().exists())

    def test_get_by_username(self):
        username = "testuser@test.com"
        User.get_or_create_by_username(username)
        user = User.get_by_username(username)
        self.assertEqual(_User.objects.count(), 1)
        self.assertEqual(user.to_json()["username"], username)

        default_equipment_ids = set([1, 2, 5, 10, 20, 21])
        self.assertItemsEqual(set(user.to_json()["equipment_ids"]), default_equipment_ids)

    def test_update_available_days(self):
        username = "testuser@test.com"
        user = User.get_or_create_by_username(username)
        user.update_available_days([0])
        self.assertEqual(user.to_json()["enabled_days"], [0])

    def test_move_to_next_week(self):
        username = "testuser@test.com"
        user = User.get_or_create_by_username(username)
        with self.assertRaises(NoGoalSetException):
            user.move_to_next_week()
        user.update_goal_id(1)
        user.move_to_next_week()
        self.assertEqual(user.current_phase_id, 1)
        self.assertGreater(user.to_json()["total_weeks_in_phase"], 1)
        self.assertEqual(user.current_week_in_phase, 1)
        user.move_to_next_week()
        self.assertEqual(user.current_week_in_phase, 2)
        initial_phase_id = user.current_phase_id

        max_runs = 50
        counter = 0
        while user.current_phase_id == initial_phase_id:
            counter += 1
            user.move_to_next_week()
            if counter > max_runs:
                raise Exception("infinite loop reach")

    def test_get_min_max_cardio(self):
        user = User.get_or_create_by_username("test")
        user.update_goal_id(3)
        with self.assertRaises(NoGoalSetException):
            user.get_min_max_cardio()
        user.move_to_next_week()
        min_cardio, max_cardio = user.get_min_max_cardio()
        self.assertGreater(max_cardio, min_cardio)

    def test_get_workout_component_frequencies(self):
        user = User.get_or_create_by_username("unique")
        user.update_goal_id(1)
        with self.assertRaises(NoGoalSetException):
            user.get_workout_component_frequencies()
        user.move_to_next_week()
        self.assertEqual(len(user.get_workout_component_frequencies()), 5)
        for frequency_info in user.get_workout_component_frequencies():
            self.assertTrue(frequency_info.minimum <= frequency_info.maximum)

    def test_get_volume_for_workout_component(self):
        user = User.get_or_create_by_username("unique2")
        user.update_goal_id(1)
        with self.assertRaises(NoGoalSetException):
            user.get_volume_for_workout_component(1)
        user.move_to_next_week()
        volume_info = user.get_volume_for_workout_component(1)
        attrs = (
            'max_exercises',
            'max_reps',
            'max_sets',
            'max_timed_cardio',
            'min_exercises',
            'min_reps',
            'min_sets',
            'min_timed_cardio'
        )
        for attr in attrs:
            self.assertTrue(hasattr(volume_info, attr))

    def test_update_equipment_ids(self):
        user = User.get_or_create_by_username("equipment_user")
        initial_equipment = user.get_available_equipment_ids()
        self.assertGreater(len(initial_equipment), 0)
        new_equipment = [1, 2, 3]
        user.update_equipment_ids(new_equipment)
        self.assertItemsEqual(user.get_available_equipment_ids(), new_equipment)
