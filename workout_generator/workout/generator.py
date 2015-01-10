import random
from collections import defaultdict

from workout_generator.constants import CardioMax
from workout_generator.constants import WorkoutComponent
from workout_generator.workout.models import WorkoutCollection
from workout_generator.workout.models import DayFrameworkCollection


def generate_new_workouts(user):
    old_framework = DayFrameworkCollection.get_for_user(user)

    user.move_to_next_week()
    day_framework_collection = _generate_day_frameworks(user)
    _generate_workouts(user, day_framework_collection)

    old_framework.delete()

    return WorkoutCollection(None, None)


def _generate_day_frameworks(user):
    isoweekday_to_components = _fill_isoweekdays_with_workout_components(user)
    isoweekday_to_cardio_intensity = _fill_isoweekdays_with_cardio_intensity(user, isoweekday_to_components)
    _mandate_cardio_or_resistance(isoweekday_to_components, isoweekday_to_cardio_intensity)
    return DayFrameworkCollection.create(user, isoweekday_to_components, isoweekday_to_cardio_intensity)


def _mandate_cardio_or_resistance(isoweekday_to_components, isoweekday_to_cardio_intensity):
    days_with_cardio_and_resistance = []
    days_with_no_cardio_no_resistance = []
    for isoweekday in (set(isoweekday_to_components.keys()) | set(isoweekday_to_cardio_intensity.keys())):
        if (isoweekday not in isoweekday_to_cardio_intensity and
                WorkoutComponent.RESISTANCE not in isoweekday_to_components[isoweekday]):
            days_with_no_cardio_no_resistance.append(isoweekday)
        elif (isoweekday in isoweekday_to_cardio_intensity and
                WorkoutComponent.RESISTANCE in isoweekday_to_components[isoweekday]):
            days_with_cardio_and_resistance.append(isoweekday)

    random.shuffle(days_with_cardio_and_resistance)
    for isoweekday in days_with_no_cardio_no_resistance:
        if len(days_with_cardio_and_resistance) == 0:
            isoweekday_to_components[isoweekday].append(WorkoutComponent.RESISTANCE)
            continue
        isoweekday_to_pull_from = days_with_cardio_and_resistance[0]
        days_with_cardio_and_resistance.remove(isoweekday_to_pull_from)
        isoweekday_to_cardio_intensity[isoweekday] = isoweekday_to_cardio_intensity[isoweekday_to_pull_from]
        del isoweekday_to_cardio_intensity[isoweekday_to_pull_from]


def _fill_isoweekdays_with_cardio_intensity(user, isoweekday_to_components):
    cardio_days = _get_num_cardio_days(user)
    isoweekdays_ordered_by_volume = sorted(isoweekday_to_components.keys(), key=lambda k: len(isoweekday_to_components[k]))
    # TODO it would be good right here to now re-order the volume so that it's
    # evenly spread using that spread out by intensity func
    isoweekdays_with_cardio = isoweekdays_ordered_by_volume[:cardio_days]
    max_lo, max_med, max_hi = CardioMax.get_values_from_fitness_level_cardio_type(user.fitness_level, user.goal.cardio_type.id)
    cardio_intensities = [random.randint(1, 3) for _ in isoweekdays_with_cardio]

    _bump_down_cardio_list_by_max(cardio_intensities, max_hi, 3)
    _bump_down_cardio_list_by_max(cardio_intensities, max_med, 2)
    _bump_down_cardio_list_by_max(cardio_intensities, max_lo, 1)
    cardio_intensities = [item for item in cardio_intensities if item > 0]
    cardio_intensities = _scramble_list_by_alternating_intensities(cardio_intensities)

    isoweekday_to_cardio_intensity = {}
    for index, isoweekday in enumerate(sorted(isoweekdays_with_cardio)):
        isoweekday_to_cardio_intensity[isoweekday] = cardio_intensities[index]
    return isoweekday_to_cardio_intensity


def _scramble_list_by_alternating_intensities(generic_list):
    previous_value = None
    new_list = []
    random.shuffle(generic_list)
    while True:
        cannot_add_new_items = True
        for item in generic_list:
            if item != previous_value:
                new_list.append(item)
                previous_value = item
                cannot_add_new_items = False
                break
        if not cannot_add_new_items:
            generic_list.remove(item)
        else:
            new_list += generic_list
            break
    return new_list


def _bump_down_cardio_list_by_max(cardio_intensity_list, max_occurences, intensity_to_check):
    occurences = 0
    for index in xrange(len(cardio_intensity_list)):
        if cardio_intensity_list[index] == intensity_to_check:
            occurences += 1

    items_to_bump_down = max(0, occurences - max_occurences)
    for _ in xrange(items_to_bump_down):
        for index in xrange(len(cardio_intensity_list)):
            if cardio_intensity_list[index] == intensity_to_check:
                cardio_intensity_list[index] -= 1
                break


def _get_num_cardio_days(user):
    min_cardio, max_cardio = user.get_min_max_cardio()
    cardio_days = random.randint(min_cardio, max_cardio)
    cardio_type = user.goal.cardio_type
    if cardio_days < cardio_type.min_times_per_week:
        cardio_days = cardio_type.min_times_per_week
    return cardio_days


def _fill_isoweekdays_with_workout_components(user):
    '''
    Returns a week with workout component randomly distributed
    '''
    enabled_isoweekdays = user.get_enabled_isoweekdays()
    isoweekday_to_components = {isoweekday: [] for isoweekday in enabled_isoweekdays}
    num_enabled_days = len(enabled_isoweekdays)

    for workout_component_info in user.get_workout_component_frequencies():
        workout_components_as_list = _get_workout_component_list_for_week(workout_component_info, num_enabled_days)
        for index, workout_component_id in enumerate(workout_components_as_list):
            isoweekday = enabled_isoweekdays[index]
            if workout_component_id is not None:
                isoweekday_to_components[isoweekday].append(workout_component_id)
    isoweekday_to_components = _evenly_distribute_volume_across_week(isoweekday_to_components)
    return isoweekday_to_components


def _evenly_distribute_volume_across_week(isoweekday_to_components):
    enabled_isoweekdays = isoweekday_to_components.keys()
    volume_list = [len(isoweekday_to_components[k]) for k in enabled_isoweekdays]

    volume_list = _scramble_list_by_alternating_intensities(volume_list)

    volume_to_indexes = defaultdict(list)
    for index, volume in enumerate(volume_list):
        volume_to_indexes[volume].append(index)

    new_distributed_components = [None] * len(volume_list)

    initial_component_list = [isoweekday_to_components[k] for k in enabled_isoweekdays]
    for component_list in initial_component_list:
        volume = len(component_list)
        index = volume_to_indexes[volume][0]
        volume_to_indexes[volume].remove(index)
        new_distributed_components[index] = component_list

    ordered_isoweekdays = sorted(enabled_isoweekdays)
    distributed_isoweekday_to_components = {}
    for index, isoweekday in enumerate(ordered_isoweekdays):
        corresponding_components = new_distributed_components[index]
        distributed_isoweekday_to_components[isoweekday] = corresponding_components
    return distributed_isoweekday_to_components


def _get_workout_component_list_for_week(workout_component_info, num_enabled_days):
    workout_component_id = workout_component_info.workout_component_id
    times_per_week = random.randint(workout_component_info.minimum, workout_component_info.maximum)
    workout_components_as_list = [workout_component_id for _ in xrange(times_per_week)]
    workout_components_as_list = workout_components_as_list[:num_enabled_days]
    empty_days_for_workout_component = num_enabled_days - len(workout_components_as_list)
    for _ in xrange(empty_days_for_workout_component):
        workout_components_as_list.append(None)
    random.shuffle(workout_components_as_list)
    return workout_components_as_list


def _generate_workouts(user, day_framework_collection):
    # equipment_ids = user.get_available_equipment_ids()
    workout_component_id = 1
    user.get_volume_for_workout_component(workout_component_id)
    # SBL LEFT OFF HERE
    pass


def _delete_old_data(user):
    pass
