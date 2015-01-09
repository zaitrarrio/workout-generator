from django.utils import unittest
from workout_generator.workout.generator import _mandate_cardio_or_resistance

class WorkoutTestCase(unittest.TestCase):
    def setUp(self):
        super(WorkoutTestCase, self).setUp()

    def test_animals_can_speak(self):
        self.assertTrue(True)
