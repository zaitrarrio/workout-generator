import random

from workout_generator.constants import CardioZone
from workout_generator.constants import HardcodedRule


class CardioCreator(object):

    def __init__(self, user, level):
        # get cardio zone by fitness level and cardio type
        # check HardCodedRule by CardioType and Phase

        # see getCardioZone in original file
        self.user = user
        self.level = level

    def _get_cardio_zone(self):
        cardio_type = self.user.get_cardio_type_id()
        force_cardio_zone_id = HardcodedRule.get_by_cardio_type_phase(cardio_type, self.user.current_phase_id)
        if force_cardio_zone_id:
            cardio_zone = CardioZone.get_by_id(force_cardio_zone_id)
        else:
            zone = random.randint(1, 3)
            args = (
                self.level,
                zone,
                cardio_type,
                self.user.fitness_level
            )
            possible_zones = CardioZone.query(*args)
            cardio_zone = random.choice(possible_zones)
        return cardio_zone
