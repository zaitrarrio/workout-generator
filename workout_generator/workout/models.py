import datetime
import json
import pytz
from collections import defaultdict

from django.db import models

from workout_generator.constants import Exercise
from workout_generator.constants import MuscleGroup
from workout_generator.constants import Phase
from workout_generator.constants import WorkoutComponent
from workout_generator.datetime_tools import datetime_to_timestamp_ms
from workout_generator.workout.exceptions import NeedsNewWorkoutsException

from .abstract_trimmable import AbstractTrimmable
from .cardio_session import CardioSession

SECONDS_FOR_TIMED_EXERCISE = 30.0
TIME_FUDGE_FACTOR = 1.08


class _Workout__Exercise(models.Model):
    workout_id = models.IntegerField(db_index=True)
    exercise_id = models.IntegerField()
    reps = models.IntegerField()
    sets = models.IntegerField()
    first_super_set_workout_exercise_id = models.IntegerField(null=True)

    def __init__(self, *args, **kwargs):
        super(_Workout__Exercise, self).__init__(*args, **kwargs)
        self.second_exercise = None


class _Workout(models.Model):
    off_day = models.BooleanField(default=False)
    visited = models.BooleanField(default=False)
    day_framework_id = models.IntegerField(db_index=True)
    phase_id = models.IntegerField()
    cardio_session_json = models.TextField()


class _DayFramework__WorkoutComponent(models.Model):
    day_framework_id = models.IntegerField(db_index=True)
    workout_component_id = models.IntegerField()


class _DayFramework(models.Model):
    js_isoweekday = models.IntegerField()
    user_id = models.IntegerField(db_index=True)
    level = models.IntegerField(null=True)
    datetime = models.DateTimeField()


class DayFrameworkCollection(object):

    def __init__(self, user, day_frameworks=None, m2m_workout_components=None):
        self.user_id = user.id
        day_frameworks = day_frameworks or self._get_day_frameworks()
        self.day_framework_id_to_obj = {d.id: d for d in day_frameworks}
        self._sorted_day_frameworks = sorted(day_frameworks, key=lambda d: d.datetime)

        self._cached_m2m_workout_components = m2m_workout_components
        self.say_framework_id_to_workout_component_list = None

    def _create_day_framework_id_to_workout_component_list(self):
        day_framework_id_to_workout_component_list = defaultdict(list)
        for m2m_row in self._get_m2m_workout_components():
            day_framework_id = m2m_row.day_framework_id
            workout_component_id = m2m_row.workout_component_id
            day_framework_id_to_workout_component_list[day_framework_id].append(workout_component_id)
        return dict(day_framework_id_to_workout_component_list)

    def get_ids(self):
        return self.day_framework_id_to_obj.keys()

    def get_json_for_day_framework_id(self, day_framework_id):
        if day_framework_id is None:
            return {}
        _day_framework = self.day_framework_id_to_obj[day_framework_id]
        return {
            "js_isoweekday": _day_framework.js_isoweekday,
            "cardio_level": _day_framework.level,
            "utc_date_timestamp": datetime_to_timestamp_ms(_day_framework.datetime)
        }

    def get_id_for_day_index(self, day_index):
        if day_index >= 7:
            raise Exception("day index must be in 0..6")
        day_framework = self._sorted_day_frameworks[day_index]
        return day_framework.id

    def get_cardio_for_day_index(self, day_index):
        if day_index >= 7:
            raise Exception("day index must be in 0..6")
        day_framework = self._sorted_day_frameworks[day_index]
        cardio_level = day_framework.level
        return cardio_level

    def get_workout_components_for_day_index(self, day_index):
        if day_index >= 7:
            raise Exception("day index must be in 0..6")
        if self.say_framework_id_to_workout_component_list is None:
            self.day_framework_id_to_workout_component_list = self._create_day_framework_id_to_workout_component_list()
        day_framework = self._sorted_day_frameworks[day_index]
        workout_component_list = self.day_framework_id_to_workout_component_list.get(day_framework.id, [])
        return workout_component_list

    def _get_day_frameworks(self):
        return list(_DayFramework.objects.filter(user_id=self.user_id))

    def _get_m2m_workout_components(self):
        if self._cached_m2m_workout_components is not None:
            return self._cached_m2m_workout_components
        day_framework_ids = [d.id for d in self._sorted_day_frameworks]
        m2m_rows = list(_DayFramework__WorkoutComponent.objects.filter(day_framework_id__in=day_framework_ids))
        self._cached_m2m_workout_components = m2m_rows
        return m2m_rows

    def delete(self):
        day_framework_ids = [d.id for d in self._sorted_day_frameworks]
        workouts_qs = _Workout.objects.filter(day_framework_id__in=day_framework_ids)
        workout_ids = [w.id for w in workouts_qs]

        _Workout__Exercise.objects.filter(workout_id__in=workout_ids).delete()
        workouts_qs.delete()

        workout_component_m2m_ids = [m2m.id for m2m in self._get_m2m_workout_components()]
        _DayFramework__WorkoutComponent.objects.filter(id__in=workout_component_m2m_ids).delete()
        _DayFramework.objects.filter(id__in=day_framework_ids).delete()

    @classmethod
    def get_for_user(cls, user):
        return DayFrameworkCollection(user)

    @classmethod
    def _get_start_isoweekdays(cls):
        # TODO add a test method for this
        js_isoweekdays = range(7)
        start_isoweekday = datetime.datetime.utcnow().isoweekday()
        if start_isoweekday == 7:
            start_isoweekday = 0
        while js_isoweekdays[0] != start_isoweekday:
            js_isoweekdays.append(js_isoweekdays.pop(0))
        return js_isoweekdays

    @classmethod
    def _create_day_framework_rows(cls, user, isoweekday_to_cardio_intensity):
        js_isoweekdays = cls._get_start_isoweekdays()
        start_datetime = datetime.datetime.utcnow()

        isoweekday_to_day_framework = {}
        for offset, js_isoweekday in enumerate(js_isoweekdays):
            kwargs = dict(
                js_isoweekday=js_isoweekday,
                user_id=user.id,
                level=isoweekday_to_cardio_intensity.get(js_isoweekday),
                datetime=start_datetime + datetime.timedelta(days=offset)
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

    def swap_cardio_for_workouts(self, workout1, workout2):
        # FIXME this is kind of lazy
        df1 = self.day_framework_id_to_obj[workout1.day_framework_id]
        df2 = self.day_framework_id_to_obj[workout2.day_framework_id]

        temp_level = df1.level
        df1.level = df2.level
        df2.level = temp_level
        df1.save()
        df2.save()

        temp_cardio_session_json = workout1._workout.cardio_session_json
        workout1._workout.cardio_session_json = workout2._workout.cardio_session_json
        workout2._workout.cardio_session_json = temp_cardio_session_json

        workout1._workout.save()
        workout2._workout.save()


class WorkoutCollection(object):

    def __init__(self, workout_list, day_framework_collection):
        self.workout_list = workout_list
        self.day_framework_collection = day_framework_collection

    def to_json(self):
        day_framework_id_to_json = {w.day_framework_id: w.to_json() for w in self.workout_list}
        for day_framework_id in day_framework_id_to_json.keys():
            day_framework_json = self.day_framework_collection.get_json_for_day_framework_id(day_framework_id)
            day_framework_id_to_json[day_framework_id].update(day_framework_json)
        return day_framework_id_to_json.values()

    @classmethod
    def workouts_exist_for_user(cls, user):
        return _DayFramework.objects.filter(user_id=user.id).exists()

    @classmethod
    def _check_needs_new_workouts(cls, existing_day_frameworks, tz):
        if len(existing_day_frameworks) == 0:
            raise NeedsNewWorkoutsException("No Workouts Exist")
        workout_dates = [d.datetime for d in existing_day_frameworks]

        max_workout_date = max(workout_dates)
        max_workout_date = max_workout_date.replace(tzinfo=pytz.timezone("UTC")).astimezone(tz)

        local_now = datetime.datetime.now(tz)
        date_older_than_one_day = max_workout_date < local_now - datetime.timedelta(days=1)
        day_difference = max_workout_date < local_now and max_workout_date.isoweekday() != local_now.isoweekday()
        if date_older_than_one_day or day_difference:
            raise NeedsNewWorkoutsException("Workouts are outdated")

    @classmethod
    def for_user(cls, user, tz):
        existing_day_frameworks = list(_DayFramework.objects.filter(user_id=user.id))
        cls._check_needs_new_workouts(existing_day_frameworks, tz)
        day_framework_collection = DayFrameworkCollection(user, day_frameworks=existing_day_frameworks)
        return cls.from_day_framework_collection(day_framework_collection)

    @classmethod
    def from_day_framework_collection(cls, day_framework_collection):
        day_framework_ids = day_framework_collection.get_ids()
        existing_workouts = list(_Workout.objects.filter(day_framework_id__in=day_framework_ids))
        workout_id_to_exercises = cls._get_exercises_for_workout_list(existing_workouts)

        proxied_workout_objects = []
        for _workout in existing_workouts:
            proxied_workout_objects.append(Workout.from_query_objects(_workout, workout_id_to_exercises.get(_workout.id, [])))

        return WorkoutCollection(proxied_workout_objects, day_framework_collection)

    @classmethod
    def _get_exercises_for_workout_list(cls, _workout_list):
        workout_ids = [w.id for w in _workout_list]
        corresponding_exercises = _Workout__Exercise.objects.filter(workout_id__in=workout_ids)
        workout_id_to_exercises = defaultdict(list)
        for exercise in corresponding_exercises:
            workout_id_to_exercises[exercise.workout_id].append(exercise)
        return workout_id_to_exercises

    @classmethod
    def get_existing_workouts_for_user(cls, user, cutoff_future_workouts=False):
        day_framework_qs = (_DayFramework.
                            objects.
                            filter(user_id=user.id).
                            order_by("datetime").
                            values_list("id", flat=True))
        if cutoff_future_workouts:
            day_framework_qs = day_framework_qs.filter(datetime__lte=datetime.datetime.utcnow())
        day_framework_ids = list(day_framework_qs)

        corresponding_workouts = list(_Workout.objects.filter(day_framework_id__in=day_framework_ids))

        workout_id_to_exercises = cls._get_exercises_for_workout_list(corresponding_workouts)

        workout_objects = []
        for workout in corresponding_workouts:
            workout_objects.append(Workout.from_query_objects(workout, workout_id_to_exercises.get(workout.id, [])))
        workout_objects = cls._sort_workout_objects_by_day_framework(workout_objects, day_framework_ids)
        return workout_objects

    @classmethod
    def _sort_workout_objects_by_day_framework(cls, workout_list, day_framework_id_list):
        id_to_obj_dict = {w.day_framework_id: w for w in workout_list}
        sorted_objs = []
        for id in day_framework_id_list:
            obj = id_to_obj_dict.get(id)
            if obj:
                sorted_objs.append(obj)
        return sorted_objs


class Workout(AbstractTrimmable):

    def __init__(self,
                 _workout=None,
                 _workout__exercise_list=None,
                 day_framework_id=None,
                 phase_id=None,
                 cardio_session=None):
        self.cardio_session = cardio_session
        self._workout = _workout or self._create_new(day_framework_id, phase_id)
        self._workout__exercise_list = _workout__exercise_list or []
        self.phase_id = phase_id or _workout.phase_id

    @property
    def phase(self):
        return Phase.get_by_id(self.phase_id)

    def to_json(self):
        json_dict = {
            "off_day": False,
            "visited": False,
            "workout_components": [],
            "phase": self.phase.to_json(),
            "cardio": self.cardio_session.to_json() if self.cardio_session else None,
        }
        workout_component_to_exercises = self._get_workout_component_to_exercises()
        for workout_component_id in WorkoutComponent.WORKOUT_ORDER:
            exercise_list = workout_component_to_exercises.get(workout_component_id)
            if exercise_list:
                workout_component = WorkoutComponent.get_by_id(workout_component_id)
                exercise_json_list = [self._workout__exercise_to_json(_w_e) for _w_e in exercise_list]
                exercise_json_list = [e for e in exercise_json_list if e is not None]
                json_dict["workout_components"].append({
                    "workout_component": workout_component.to_json(),
                    "rest": workout_component.get_rest(self.phase),
                    "exercises": exercise_json_list
                })
        return json_dict

    def _get_workout_component_to_exercises(self):
        workout_component_to_exercises = defaultdict(list)
        first_exercise_superset = [_we for _we in self._workout__exercise_list if _we.first_super_set_workout_exercise_id is None]
        second_exercise_superset = [_we for _we in self._workout__exercise_list if _we.first_super_set_workout_exercise_id is not None]
        for _workout__exercise in first_exercise_superset:
            exercise = Exercise.get_by_id(_workout__exercise.exercise_id)
            workout_component_to_exercises[exercise.workout_component_id].append(_workout__exercise)
        for _workout__exercise in second_exercise_superset:
            exercise = Exercise.get_by_id(_workout__exercise.exercise_id)
            for _workout__exercise_initial in workout_component_to_exercises[exercise.workout_component_id]:
                if _workout__exercise_initial.id == _workout__exercise.first_super_set_workout_exercise_id:
                    _workout__exercise_initial.second_exercise = _workout__exercise
                    break

        return workout_component_to_exercises

    def _workout__exercise_to_json(self, _workout__exercise):
        if _workout__exercise is None:
            return None

        if _workout__exercise.first_super_set_workout_exercise_id is None and _workout__exercise.sets == 0:
            # sets can be reduced to 0 via time trimming
            return None

        return {
            "exercise": Exercise.get_by_id(_workout__exercise.exercise_id).to_json(),
            "reps": _workout__exercise.reps,
            "sets": _workout__exercise.sets,
            "superset": self._workout__exercise_to_json(_workout__exercise.second_exercise)
        }

    @classmethod
    def from_query_objects(cls, _workout, _workout__exercise_list):
        cardio_session_str = _workout.cardio_session_json
        cardio_session = CardioSession.from_json(json.loads(cardio_session_str)) if cardio_session_str else None
        return Workout(_workout=_workout, _workout__exercise_list=_workout__exercise_list, cardio_session=cardio_session)

    @classmethod
    def create_new(cls, day_framework_id, phase_id, cardio_session=None):
        return Workout(day_framework_id=day_framework_id, phase_id=phase_id, cardio_session=cardio_session)

    def _create_new(self, day_framework_id, phase_id):
        return _Workout.objects.create(
            off_day=False,
            visited=False,
            day_framework_id=day_framework_id,
            phase_id=phase_id,
            cardio_session_json=json.dumps(self.cardio_session.to_json()) if self.cardio_session else "",
        )

    @property
    def day_framework_id(self):
        return self._workout.day_framework_id

    def get_muscle_ids_used(self):
        muscle_ids = self.get_primary_muscle_ids_used()
        for _workout__exercise in self._workout__exercise_list:
            exercise = Exercise.get_by_id(_workout__exercise.exercise_id)
            muscle_ids.extend(exercise.muscle_group_ids)
        muscle_ids = list(set(muscle_ids))
        return muscle_ids

    def get_exercise_ids_used(self, workout_component_id=None):
        exercise_ids = []
        for _we in self._workout__exercise_list:
            if workout_component_id:
                exercise = Exercise.get_by_id(_we.exercise_id)
                if exercise.workout_component_id != workout_component_id:
                    continue
            exercise_ids.append(_we.exercise_id)
        return exercise_ids

    def get_primary_muscle_ids_used(self, workout_component_id=None):
        muscle_ids = []
        for _workout__exercise in self._workout__exercise_list:
            exercise = Exercise.get_by_id(_workout__exercise.exercise_id)
            if workout_component_id is None or exercise.workout_component_id == workout_component_id:
                muscle_ids.append(exercise.muscle_group_id)
        muscle_ids = list(set(muscle_ids))
        return muscle_ids

    def add_exercise_set_collection(self, exercise, sets, reps, first_super_set_workout_exercise_id=None):
        kwargs = dict(
            workout_id=self._workout.id,
            exercise_id=exercise.id,
            reps=reps,
            sets=sets,
            first_super_set_workout_exercise_id=first_super_set_workout_exercise_id
        )
        workout_exercise = _Workout__Exercise.objects.create(**kwargs)
        self._workout__exercise_list.append(workout_exercise)

    def add_superset_to_exercise(self, first_exercise, second_exercise, reps):
        first_workout_exercise_id = None
        sets = 0
        for _workout__exercise in self._workout__exercise_list:
            if _workout__exercise.exercise_id == first_exercise.id:
                first_workout_exercise_id = _workout__exercise.id
                sets = _workout__exercise.sets
        self.add_exercise_set_collection(second_exercise, sets, reps, first_super_set_workout_exercise_id=first_workout_exercise_id)

    def get_rep_prescriptions_for_muscle(self, muscle_id):
        rep_list = []
        for _workout__exercise in self._workout__exercise_list:
            exercise = Exercise.get_by_id(_workout__exercise.exercise_id)
            if exercise.muscle_group_id == muscle_id:
                rep_list.append(_workout__exercise.reps)
        return rep_list

    def get_minimum_time_required(self):
        return 10.0

    def get_total_time(self):
        total_time = 0.0
        workout_component_to_exercises = self._get_workout_component_to_exercises()
        for workout_component_id, exercise_list in workout_component_to_exercises.items():
            if workout_component_id == WorkoutComponent.FLEXIBILITY:
                continue
            workout_component = WorkoutComponent.get_by_id(workout_component_id)
            for _workout__exercise in exercise_list:
                seconds_rest = workout_component.get_rest(self.phase)
                minutes_rest = float(seconds_rest) / 60
                minutes_rest *= _workout__exercise.sets
                total_time += minutes_rest

                for _we in [_workout__exercise, _workout__exercise.second_exercise]:
                    if _we is None:
                        continue
                    exercise = Exercise.get_by_id(_we.exercise_id)
                    if exercise.timed:
                        total_time += _we.sets * SECONDS_FOR_TIMED_EXERCISE / 60.0
                    else:
                        total_reps = _we.reps * _we.sets
                        rep_minutes = total_reps * self.phase.tempo.seconds_per_rep / 60.0
                        total_time += rep_minutes
        total_time *= TIME_FUDGE_FACTOR
        return total_time

    def _trim_by_exact_percent(self, percent):
        initial_time = self.get_total_time()
        target_time = initial_time * (1.0 - percent)
        self._trim_sets(target_time)
        self._trim_lonely_muscle_groups(target_time)
        self._trim_isolated_exercises(target_time)
        self._trim_most_worked_muscles(target_time)

    def _trim_sets(self, target_time):
        if self.get_total_time() < target_time:
            return

        min_sets = 2
        max_sets_to_delete = 2
        non_supersets = [_we for _we in self._workout__exercise_list if _we.first_super_set_workout_exercise_id is None]
        for _ in xrange(max_sets_to_delete):
            for _we in non_supersets:
                if _we.sets > min_sets:
                    _we.sets -= 1
                    if _we.second_exercise:
                        _we.second_exercise.sets -= 1
                if self.get_total_time() < target_time:
                    break
            else:
                continue
            break

    def _trim_lonely_muscle_groups(self, target_time):
        if self.get_total_time() < target_time:
            return
        non_supersets = [_we for _we in self._workout__exercise_list if _we.first_super_set_workout_exercise_id is None]
        muscle_id_to_ring = {}
        ring_to_count = {}
        for muscle_id_set in MuscleGroup.get_rings():
            muscle_id_tuple = tuple(muscle_id_set)
            for muscle_id in muscle_id_tuple:
                muscle_id_to_ring[muscle_id] = muscle_id_tuple
            ring_to_count[muscle_id_tuple] = 0

        for _we in non_supersets:
            exercise = Exercise.get_by_id(_we.exercise_id)
            muscle_id_tuple = muscle_id_to_ring[exercise.muscle_group_id]
            ring_to_count[muscle_id_tuple] += 1
        for muscle_ring, count in ring_to_count.items():
            if count == 1:
                for _we in non_supersets:
                    _we.sets = 0
                    if self.get_total_time() < target_time:
                        break
                else:
                    continue
                break

    def _trim_isolated_exercises(self, target_time):
        if self.get_total_time() < target_time:
            return
        non_supersets = [_we for _we in self._workout__exercise_list if _we.first_super_set_workout_exercise_id is None]
        for _we in non_supersets:
            exercise = Exercise.get_by_id(_we.exercise_id)
            if not _we.second_exercise and exercise.compound:
                _we.sets = 0
                if self.get_total_time() < target_time:
                    break

    def _trim_most_worked_muscles(self, target_time):
        if self.get_total_time() < target_time:
            return
        non_supersets = [_we for _we in self._workout__exercise_list if _we.first_super_set_workout_exercise_id is None]

        while self.get_total_time() > target_time:
            # SBL MOVE THIS LOGIC TO ITS OWN FUNCTION
            muscle_id_to_ring = {}
            ring_to_count = {}
            for muscle_id_set in MuscleGroup.get_rings():
                muscle_id_tuple = tuple(muscle_id_set)
                for muscle_id in muscle_id_tuple:
                    muscle_id_to_ring[muscle_id] = muscle_id_tuple
                ring_to_count[muscle_id_tuple] = 0

            for _we in non_supersets:
                exercise = Exercise.get_by_id(_we.exercise_id)
                muscle_id_tuple = muscle_id_to_ring[exercise.muscle_group_id]
                if _we.sets:
                    ring_to_count[muscle_id_tuple] += 1
            muscle_ring__count = sorted(ring_to_count.items(), key=lambda t: t[1], reverse=True)

            for _we in non_supersets:
                exercise = Exercise.get_by_id(_we.exercise_id)
                if _we.sets and exercise.muscle_group_id in muscle_ring__count[0][0]:
                    _we.sets = 0
                    if _we.second_exercise:
                        _we.second_exercise.sets = 0
                    break

    def refresh_and_save(self):
        if self.cardio_session:
            self._workout.cardio_sesson_json = json.dumps(self.cardio_session.to_json())
        for _we in self._workout__exercise_list:
            _we.save()

    def needs_populate(self):
        return (not self.has_cardio() and not self.has_lifting())

    def has_cardio(self):
        return self.cardio_session is not None

    def has_lifting(self):
        return len(self._get_workout_component_to_exercises()) > 0

    def can_manipulate(self):
        return True


class EmptyWorkout(object):

    def __init__(self, day_framework_id=None):
        self.day_framework_id = day_framework_id

    def to_json(self):
        return {}

    def get_muscle_ids_used(self):
        return tuple()

    def get_exercise_ids_used(self):
        return tuple()

    def get_primary_muscle_ids_used(self, **extras):
        return tuple()

    def get_rep_prescriptions_for_muscle(self, muscle_id):
        return []

    def add_exercise_set_collection(self, *args, **kwargs):
        raise Exception("This case should not be reached")

    def needs_populate(self):
        return False

    def can_manipulate(self):
        # FIXME probably a better way to do this
        return False
