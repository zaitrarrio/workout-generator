import datetime

# from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from workout_generator.workout.exceptions import NeedsNewWorkoutsException
# from workout_generator.constants import Exercise
# from workout_generator.constants import Phase
# from workout_generator.constants import Equipment
# from workout_generator.user.constants import StatusState
# from workout_generator.user.constants import GenderType


class _Workout__Exercise(models.Model):
    workout_id = models.IntegerField()
    exercise_id = models.IntegerField()
    reps = models.IntegerField()
    sets = models.IntegerField()
    tempo_id = models.IntegerField()
    rest = models.IntegerField()
    super_set_workout__exercise_id = models.IntegerField(null=True)


class _Workout(models.Model):
    user_id = models.IntegerField()
    cardio_string = models.CharField(max_length=2014, null=True)
    off_day = models.BooleanField(default=False)
    visited = models.BooleanField(default=False)
    day_framework_id = models.IntegerField()


class _DayFramework__WorkoutComponent(models.Model):
    day_framework_id = models.IntegerField()
    workout_component_id = models.IntegerField()


class _DayFramework(models.Model):
    js_isoweekday = models.IntegerField()
    user_id = models.IntegerField()
    cardio = models.BooleanField()
    timed = models.NullBooleanField(null=True)
    level = models.IntegerField()
    date = models.DateField()


class DayFramework(object):
    pass


class WorkoutCollection(object):

    def __init__(self, _workout_list, _day_framework_list):
        self._workout_list = _workout_list
        self._day_framework_list = _day_framework_list

    def to_json(self):
        return {}

    @classmethod
    def for_user(cls, user):
        existing_workouts = list(_Workout.objects.filter(user_id=user.id))
        if len(existing_workouts) == 0:
            raise NeedsNewWorkoutsException("No Workouts Exist")
        day_framework_ids = [w.day_framework_id for w in existing_workouts]
        existing_day_frameworks = list(_DayFramework.objects.filter(id__in=day_framework_ids, user_id=user.id))
        workout_dates = [d.date for d in existing_day_frameworks]
        if max(workout_dates) > datetime.datetime.utcnow().date():
            raise NeedsNewWorkoutsException("Workouts are outdated")
        return WorkoutCollection(existing_workouts, existing_day_frameworks)
