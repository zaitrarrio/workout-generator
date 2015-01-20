# import datetime
import random
import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from workout_generator.constants import CardioVolume
from workout_generator.constants import ExercisesPerMuscleGroup
from workout_generator.constants import Exhaustion
from workout_generator.constants import Goal
from workout_generator.constants import Phase
from workout_generator.constants import PhaseLengthByGoal
from workout_generator.constants import Equipment
from workout_generator.constants import WorkoutComponentFrequency
from workout_generator.user.constants import StatusState
from workout_generator.user.constants import GenderType
from workout_generator.user.exceptions import NoGoalSetException


class _User(models.Model):
    username = models.CharField(max_length=255, null=False)
    email = models.CharField(max_length=255, null=True)
    confirmation_code = models.CharField(max_length=255, null=True)
    status_state_id = models.IntegerField(default=StatusState.UNCONFIRMED.index, null=False)

    stripe_customer_id = models.CharField(max_length=255, null=True)
    goal_id = models.IntegerField(null=True)
    current_phase_id = models.IntegerField(null=True)

    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True)
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    # sunday is 0 in JS

    minutes_per_day = models.IntegerField(default=60)
    fitness_level = models.IntegerField(default=2)
    experience = models.IntegerField(default=2)
    age = models.IntegerField(default=30)
    gender_id = models.IntegerField(default=GenderType.MALE.index, null=False)

    current_week_in_phase = models.IntegerField(default=0)
    total_weeks_in_phase = models.IntegerField(default=0)


class _User__Equipment(models.Model):
    user_id = models.IntegerField()
    equipment_id = models.IntegerField()


class _User__VisitedPhase(models.Model):
    user_id = models.IntegerField()
    phase_id = models.IntegerField()

    @classmethod
    def get_or_create(cls, user_id, phase_id):
        try:
            _User__VisitedPhase.objects.get(user_id=user_id, phase_id=phase_id)
        except ObjectDoesNotExist:
            _User__VisitedPhase.objects.create(user_id=user_id, phase_id=phase_id)


class User(object):
    isoweekday_to_prop = {
        0: 'sunday',
        1: 'monday',
        2: 'tuesday',
        3: 'wednesday',
        4: 'thursday',
        5: 'friday',
        6: 'saturday'
    }

    def __init__(self, _user):
        self._user = _user

    def _start_first_phase(self):
        self._user.current_phase_id = Goal.get_by_id(self.goal_id).start_phase_id
        self._user.current_week_in_phase = 1
        min_length, max_length = PhaseLengthByGoal.get_min_max_phase_length_for_goal_phase(self.goal_id, self._user.current_phase_id)
        self._user.total_weeks_in_phase = random.randint(min_length, max_length)
        self._user.save()

    def _start_next_phase(self):
        _User__VisitedPhase.get_or_create(self._user.id, self._user.current_phase_id)

        possible_user_phase_infos = PhaseLengthByGoal.get_phases_for_goal_id(self.goal_id)
        possible_user_phase_infos = [phase_info for phase_info in possible_user_phase_infos if phase_info.phase.id != self._user.current_phase_id]

        user_phase_infos_not_visited = [phase_info for phase_info in possible_user_phase_infos if not self.has_visited_phase(phase_info.phase.id)]
        use_max_length = False
        if len(user_phase_infos_not_visited) > 0:
            use_max_length = True
            possible_user_phase_infos = user_phase_infos_not_visited

        new_phase_info = random.choice(possible_user_phase_infos)
        self._user.current_phase_id = new_phase_info.phase.id
        self._user.current_week_in_phase = 1
        if use_max_length:
            self._user.total_weeks_in_phase = new_phase_info.max_length
        else:
            self._user.total_weeks_in_phase = random.randint(new_phase_info.min_length, new_phase_info.max_length)
        self._user.save()

    def get_workout_component_frequencies(self):
        if self.current_phase_id is None:
            raise NoGoalSetException("User hasn't started a phase yet")
        args = (
            self.current_week_in_phase,
            self.current_phase_id,
            self.fitness_level,
        )
        return WorkoutComponentFrequency.get_by_week_phase_fitness_level(*args)

    def get_min_max_cardio(self):
        # per week
        if self.current_phase_id is None:
            raise NoGoalSetException("User hasn't started a phase yet")
        args = (
            self.current_phase_id,
            self.fitness_level,
            self.current_week_in_phase,
        )
        return CardioVolume.get_min_max_cardio(*args)

    def get_volume_for_workout_component(self, workout_component_id, force_different_phase=None):
        if self.current_phase_id is None:
            raise NoGoalSetException("User hasn't started a phase yet")
        phase_id = force_different_phase or self.current_phase_id
        fitness_level = self.fitness_level
        week = self.current_week_in_phase
        return CardioVolume.get_all_volume_info(phase_id, fitness_level, week, workout_component_id)

    def get_cardio_type_id(self):
        return Goal.get_by_id(self.goal_id).cardio_type_id

    def has_visited_phase(self, phase_id):
        return _User__VisitedPhase.objects.filter(user_id=self._user.id, phase_id=phase_id).exists()

    def move_to_next_week(self):
        if self.goal_id is None:
            raise NoGoalSetException("User hasn't selected a goal")
        if self._user.current_phase_id is None:
            self._start_first_phase()
            return

        self._user.current_week_in_phase += 1
        if self._user.current_week_in_phase <= self._user.total_weeks_in_phase:
            self._user.save()
            return
        self._start_next_phase()

    @property
    def id(self):
        return self._user.id

    @property
    def minutes_per_day(self):
        return self._user.minutes_per_day

    def get_enabled_isoweekdays(self):
        enabled_days = []
        prop_to_isoweekday = {v: k for k, v in self.isoweekday_to_prop.items()}
        for attr_name, isoweekday in prop_to_isoweekday.items():
            if getattr(self._user, attr_name):
                enabled_days.append(isoweekday)
        return enabled_days

    def to_json(self):
        return {
            'username': self._user.username,
            'email': self._user.email,
            'enabled_days': self.get_enabled_isoweekdays(),
            'minutes_per_day': self._user.minutes_per_day,
            'fitness_level': self._user.fitness_level,
            'experience': self._user.experience,
            'status': StatusState.from_index(self._user.status_state_id).canonical_name,
            'goal': Goal.get_by_id_as_json(self._user.goal_id),
            'gender': GenderType.from_index(self._user.gender_id).canonical_name,
            'age': self._user.age,
            'equipment_ids': self.get_available_equipment_ids(),
            'current_week_in_phase': self._user.current_week_in_phase,
            'total_weeks_in_phase': self._user.total_weeks_in_phase,
            'phase': Phase.get_by_id(self._user.current_phase_id) if self._user.current_phase_id else None
        }

    @property
    def goal_id(self):
        return self._user.goal_id

    @property
    def goal(self):
        return Goal.get_by_id(self.goal_id)

    @property
    def current_phase_id(self):
        return self._user.current_phase_id

    @property
    def fitness_level(self):
        return self._user.fitness_level

    @property
    def experience(self):
        return self._user.experience

    @property
    def current_week_in_phase(self):
        return self._user.current_week_in_phase

    def get_available_equipment_ids(self):
        existing_user_equipment = list(_User__Equipment.objects.filter(user_id=self._user.id).
                values_list('equipment_id', flat=True))
        return existing_user_equipment

    def get_exhaustion_percent(self):
        days_per_week = len(self.get_enabled_isoweekdays())
        return Exhaustion.get_percent(days_per_week, self.current_phase_id)

    def get_min_max_exercises_for_muscle_group_per_day(self, muscle_group_id):
        return ExercisesPerMuscleGroup.get_min_max(muscle_group_id, self.current_phase_id, self.fitness_level)

    def update_gender(self, canonical_name):
        gender_type = GenderType.from_canonical(canonical_name)
        self._user.gender_id = gender_type.index
        self._user.save()

    def update_age(self, age):
        self._user.age = age
        self._user.save()

    def update_email(self, email):
        self._user.email = email
        self._user.save()

    def update_stripe_customer_id(self, stripe_customer_id):
        self._user.stripe_customer_id = stripe_customer_id
        self._user.save()

    def update_goal_id(self, goal_id):
        self._user.goal_id = goal_id
        self._user.save()

    def update_equipment_ids(self, equipment_id_list):
        existing_user_equipment = list(_User__Equipment.objects.filter(user_id=self._user.id).
                values_list('equipment_id', flat=True))

        equipment_needing_creation = set(equipment_id_list) - set(existing_user_equipment)
        equipment_needing_deletion = set(existing_user_equipment) - set(equipment_id_list)

        _User__Equipment.objects.filter(user_id=self._user.id, equipment_id__in=equipment_needing_deletion).delete()

        for equipment_id in equipment_needing_creation:
            _User__Equipment.objects.create(user_id=self._user.id, equipment_id=equipment_id)

        self._user.save()

    def update_available_days(self, js_isoweekday_list):

        for weekday_attr in self.isoweekday_to_prop.values():
            setattr(self._user, weekday_attr, False)

        for isoweekday in js_isoweekday_list:
            weekday_attr = self.isoweekday_to_prop[isoweekday]
            setattr(self._user, weekday_attr, True)

        self._user.save()

    def update_minutes_per_day(self, minutes_per_day):
        self._user.minutes_per_day = minutes_per_day
        self._user.save()

    def update_fitness_level(self, fitness_level_id):
        self._user.fitness_level = fitness_level_id
        self._user.save()

    def update_experience(self, experience_id):
        self._user.experience = experience_id
        self._user.save()

    @classmethod
    def create_from_username(cls, username):
        _user = _User.objects.create(
            username=username,
            confirmation_code=str(uuid.uuid4())
        )
        user = User(_user)
        user.update_equipment_ids(Equipment.DEFAULT_IDS)
        return user

    @classmethod
    def get_or_create_by_username(cls, username):
        try:
            _user = _User.objects.get(username=username)
        except ObjectDoesNotExist:
            return cls.create_from_username(username)
        return User(_user)

    @classmethod
    def get_by_username(cls, username):
        try:
            _user = _User.objects.get(username=username)
        except ObjectDoesNotExist:
            return None
        return User(_user)
