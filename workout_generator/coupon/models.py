import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from workout_generator.datetime_tools import datetime_to_timestamp_ms


class _Coupon(models.Model):
    code = models.CharField(max_length=100, db_index=True)
    valid_thru = models.DateTimeField()
    description = models.CharField(max_length=255)
    stripe_plan_id = models.CharField(max_length=50, null=True)


class InvalidCoupon(object):

    def to_json(self):
        return {}

    @property
    def valid(self):
        return False


class Coupon(object):

    def __init__(self, _coupon):
        self._coupon = _coupon

    def to_json(self):
        return {
            "code": self._coupon.code,
            "description": self._coupon.description,
            "striple_plan_id": self.stripe_plan_id,
            "valid": self.valid,
            "valid_thru": datetime_to_timestamp_ms(self.valid_thru)
        }

    @property
    def valid(self):
        return self.valid_thru > datetime.datetime.utcnow()

    @property
    def valid_thru(self):
        return self._coupon.valid_thru

    @property
    def stripe_plan_id(self):
        return self._coupon.stripe_plan_id

    @classmethod
    def get_by_code(cls, code):
        try:
            _coupon = _Coupon.objects.get(code=code)
            return Coupon(_coupon)
        except ObjectDoesNotExist:
            return InvalidCoupon()

    @classmethod
    def create(cls, code, valid_thru_dt, description, stripe_plan_id):
        _Coupon.objects.create(
            code=code,
            valid_thru=valid_thru_dt,
            description=description,
            stripe_plan_id=stripe_plan_id
        )
