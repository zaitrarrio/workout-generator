# import datetime
import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from workout_generator.constants import Goal
from workout_generator.constants import Phase
from workout_generator.user.constants import StatusState


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


class _User__Equipment(models.Model):
    user_id = models.IntegerField()
    equipment_id = models.IntegerField()


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

    def _get_enabled_isoweekdays(self):
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
            'enabled_days': self._get_enabled_isoweekdays(),
            'minutes_per_day': self._user.minutes_per_day,
            'fitness_level': self._user.fitness_level,
            'experience': self._user.experience,
            'status': StatusState.from_index(self._user.status_state_id).canonical_name,
            'goal': Goal.get_by_id_as_json(self._user.goal_id),
            'phase': Phase.get_by_id(self._user.current_phase_id) if self._user.current_phase_id else None
        }

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
        return _User(_user)

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
