import datetime

from workout_generator.coupon.models import Coupon

Coupon.create("GRANDFATHER500",
              datetime.datetime(year=2015, month=2, day=31, hour=0, minute=0),
              "Hey, alright!  Your membership is free, just finished the signup!",
              None)
Coupon.create("HACKERNEWS2015",
              datetime.datetime(year=2015, month=2, day=7, hour=0, minute=0),
              "Hey, alright!  Your membership is free, just finished the signup!",
              None)
