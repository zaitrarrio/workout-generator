import datetime
from collections import defaultdict

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
    super_set_workout_exercise_id = models.IntegerField(null=True)


class _Workout(models.Model):
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
    # dont think cardio field is even necessary
    cardio = models.BooleanField(default=False)
    level = models.IntegerField(null=True)
    date = models.DateField()


class DayFrameworkCollection(object):

    def __init__(self, user, day_frameworks=None, m2m_workout_components=None):
        self.user = user
        day_frameworks = day_frameworks or self._get_day_frameworks()
        self._sorted_day_frameworks = sorted(day_frameworks, key=lambda d: d.date)
        self._m2m_workout_components = m2m_workout_components or self._get_m2m_workout_components()
        self.day_framework_id_to_workout_component_list = self._create_day_framework_id_to_workout_component_list()

    def _create_day_framework_id_to_workout_component_list(self):
        day_framework_id_to_workout_component_list = defaultdict(list)
        for m2m_row in self._m2m_workout_components:
            day_framework_id = m2m_row.day_framework_id
            workout_component_id = m2m_row.workout_component_id
            day_framework_id_to_workout_component_list[day_framework_id].append(workout_component_id)
        return dict(day_framework_id_to_workout_component_list)

    def get_cardio_for_day_index(self, day_index):
        if day_index >= 7:
            raise Exception("day index must be in 0..6")
        day_framework = self._sorted_day_frameworks[day_index]
        cardio_level = day_framework.level
        return cardio_level

    def get_workout_components_for_day_index(self, day_index):
        if day_index >= 7:
            raise Exception("day index must be in 0..6")
        day_framework = self._sorted_day_frameworks[day_index]
        workout_component_list = self.day_framework_id_to_workout_component_list.get(day_framework.id, [])
        return workout_component_list

    def _get_day_frameworks(self):
        return list(_DayFramework.objects.filter(user_id=self.user.id))

    def _get_m2m_workout_components(self):
        day_framework_ids = [d.id for d in self._sorted_day_frameworks]
        m2m_rows = list(_DayFramework__WorkoutComponent.objects.filter(day_framework_id__in=day_framework_ids))
        return m2m_rows

    def delete(self):
        day_framework_ids = [d.id for d in self._sorted_day_frameworks]
        workouts_qs = _Workout.objects.filter(day_framework_id__in=day_framework_ids)
        workout_ids = [w.id for w in workouts_qs]

        _Workout__Exercise.objects.filter(workout_id__in=workout_ids)
        workouts_qs.delete()

        workout_component_m2m_ids = [m2m.id for m2m in self._m2m_workout_components]
        _DayFramework__WorkoutComponent.objects.filter(id__in=workout_component_m2m_ids).delete()
        _DayFramework.objects.filter(id__in=day_framework_ids).delete()

    @classmethod
    def get_for_user(cls, user):
        return DayFrameworkCollection(user)

    @classmethod
    def _get_start_isoweekdays(cls):
        # TODO add a test method for this
        js_isoweekdays = range(7)
        start_isoweekday = datetime.datetime.utcnow().date().isoweekday()
        if start_isoweekday == 7:
            start_isoweekday = 0
        while js_isoweekdays[0] != start_isoweekday:
            js_isoweekdays.append(js_isoweekdays.pop(0))
        return js_isoweekdays

    @classmethod
    def _create_day_framework_rows(cls, user, isoweekday_to_cardio_intensity):
        js_isoweekdays = cls._get_start_isoweekdays()
        start_date = datetime.datetime.utcnow().date()

        isoweekday_to_day_framework = {}
        for offset, js_isoweekday in enumerate(js_isoweekdays):
            kwargs = dict(
                js_isoweekday=js_isoweekday,
                user_id=user.id,
                cardio=True if js_isoweekday in isoweekday_to_cardio_intensity else False,
                level=isoweekday_to_cardio_intensity.get(js_isoweekday),
                date=start_date + datetime.timedelta(days=offset)
            )
            isoweekday_to_day_framework[js_isoweekday] = _DayFramework.objects.create(**kwargs)
        return isoweekday_to_day_framework

    @classmethod
    def _create_m2m_workout_component_ids(cls, isoweekday_to_day_framework, isoweekday_to_components):
        m2ms = []
        for isoweekday, component_list in isoweekday_to_components.items():
            for workout_component_id in component_list:
                kwargs = dict(
                    day_framework_id=isoweekday_to_day_framework[isoweekday].id,
                    workout_component_id=workout_component_id
                )
                m2ms.append(_DayFramework__WorkoutComponent.objects.create(**kwargs))
        return m2ms

    @classmethod
    def create(cls, user, isoweekday_to_components, isoweekday_to_cardio_intensity):
        isoweekday_to_day_framework = cls._create_day_framework_rows(user, isoweekday_to_cardio_intensity)
        existing_m2ms = cls._create_m2m_workout_component_ids(isoweekday_to_day_framework, isoweekday_to_components)

        existing_day_frameworks = isoweekday_to_day_framework.values()
        return DayFrameworkCollection(user, day_frameworks=existing_day_frameworks, m2m_workout_components=existing_m2ms)


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
