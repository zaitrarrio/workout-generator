import random

from workout_generator.constants import CardioZone
from workout_generator.constants import HardcodedRule

from .cardio_session import CardioSession
from .cardio_interval import CardioInterval


class CardioCreator(object):

    def __init__(self, user, level):
        # get cardio zone by fitness level and cardio type
        # check HardCodedRule by CardioType and Phase

        # see getCardioZone in original file
        self.user = user
        self.level = level

    def _get_cardio_zones(self):
        cardio_type = self.user.get_cardio_type_id()
        force_cardio_zone_id = HardcodedRule.get_by_cardio_type_phase(cardio_type, self.user.current_phase_id)
        if force_cardio_zone_id:
            cardio_zone = CardioZone.get_by_id(force_cardio_zone_id)
            return [cardio_zone]
        return self._get_zones_by_query(self)

    def _get_zones_by_query(self, zone):
        cardio_type = self.user.get_cardio_type_id()
        args = (
            self.level,
            zone,
            cardio_type,
            self.user.fitness_level
        )
        possible_zones = CardioZone.query(*args)
        try:
            return random.choice(possible_zones)
        except IndexError:
            return None

    def _construct_zone_pattern(self, cardio_zones):
        patterns = [
            (1,),
            (1, 2),
            (1, 2, 3),
            (1, 2, 3, 2),
            (2, 3),
            (1, 3),
        ]
        valid_patterns = []
        usable_zone_numbers = {cz.zone for cz in cardio_zones}

        for pattern in patterns:
            include_pattern = True
            for pattern_zone in pattern:
                if pattern_zone not in usable_zone_numbers:
                    include_pattern = False
            if include_pattern:
                valid_patterns.append(pattern)

        return random.choice(valid_patterns)

    def _pick_three_cardio_zones(self):
        cardio_zones = [self._get_zones_by_query(zone_number) for zone_number in xrange(1, 3 + 1)]
        cardio_zones = [cz for cz in cardio_zones if cz is not None]
        return cardio_zones

    def _get_total_cardio_time(self, cardio_zones):
        max_overall_possibles = [cz.max_overall for cz in cardio_zones]
        return float(min(max_overall_possibles))

    def _filter_out_unnecessary_cardio_zones(self, cardio_zones, zone_pattern):
        return [cz for cz in cardio_zones if cz.zone in zone_pattern + (1, )]

    def _update_cardio_rules_by_adjacent_zones(self, cardio_zones):
        cardio_zones_by_rule_order = list(reversed(sorted(cardio_zones, key=lambda cz: cz.zone)))
        previous_zone = None
        for cardio_zone in cardio_zones_by_rule_order:
            if previous_zone:
                cardio_zone.interval = previous_zone.previous
            previous_zone = cardio_zone

    def _create_cardio_from_rules(self, total_time_for_cardio, cardio_zones, zone_pattern):
        zone_to_cardio_zone = {cz.zone: cz for cz in cardio_zones}
        time_spent_so_far = 0.0
        zone_index_cursor = 0
        cardio_session = CardioSession()

        self._update_cardio_rules_by_adjacent_zones(cardio_zones)

        if zone_pattern[0] != 1:
            cardio_zone = zone_to_cardio_zone[1]
            cardio_interval = CardioInterval.from_cardio_zone(cardio_zone)
            cardio_session.add_interval(cardio_interval)

        while time_spent_so_far < total_time_for_cardio - zone_to_cardio_zone[1].interval:
            zone = zone_pattern[zone_index_cursor]
            cardio_zone = zone_to_cardio_zone[zone]
            cardio_interval = CardioInterval.from_cardio_zone(cardio_zone)
            cardio_session.add_interval(cardio_interval)
            time_spent_so_far += cardio_zone.interval
            zone_index_cursor += 1
            zone_index_cursor = zone_index_cursor % len(zone_pattern)

        if cardio_session.is_empty() or cardio_zone.zone != 1:
            cardio_zone = zone_to_cardio_zone[1]
            cardio_interval = CardioInterval.from_cardio_zone(cardio_zone)
            cardio_session.add_interval(cardio_interval)
        return cardio_session

    def create(self):
        cardio_zones = self._pick_three_cardio_zones()
        zone_pattern = self._construct_zone_pattern(cardio_zones)
        cardio_zones = self._filter_out_unnecessary_cardio_zones(cardio_zones, zone_pattern)
        total_time_for_cardio = self._get_total_cardio_time(cardio_zones)
        cardio_session = self._create_cardio_from_rules(total_time_for_cardio, cardio_zones, zone_pattern)
        # TODO then figure out the hardcoded rule nonsense
        return cardio_session
