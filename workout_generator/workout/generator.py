import random

from collections import defaultdict

from workout_generator.constants import CardioMax
from workout_generator.constants import Exercise
from workout_generator.constants import MuscleGroup
from workout_generator.constants import MuscleFrequency
from workout_generator.constants import WorkoutComponent
from workout_generator.utils import get_new_trim_by_percent
from workout_generator.workout.cardio_creator import CardioCreator
from workout_generator.workout.exceptions import NoExercisesAvailableException
from workout_generator.workout.models import WorkoutCollection
from workout_generator.workout.models import DayFrameworkCollection
from workout_generator.workout.models import EmptyWorkout
from workout_generator.workout.models import Workout
from workout_generator.workout.super_set_manager import SuperSetManager
from workout_generator.workout.utils import get_reps_sets_from_volume_info
from workout_generator.workout.utils import evenly_distribute_exercises_by_muscle_group


def generate_new_workouts(user, move_to_next_week=True):
    old_framework = DayFrameworkCollection.get_for_user(user)

    if move_to_next_week:
        # added the option to backfill workouts in case of a bug
        user.move_to_next_week()

    day_framework_collection = _generate_day_frameworks(user)
    new_workouts = _generate_workouts(user, day_framework_collection)

    old_framework.delete()

    return WorkoutCollection(new_workouts, day_framework_collection)


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
    previous_workouts = WorkoutCollection.get_existing_workouts_for_user(user, cutoff_future_workouts=True)
    new_workouts = []
    for day_index in xrange(7):
        workout_components = day_framework_collection.get_workout_components_for_day_index(day_index)
        day_framework_id = day_framework_collection.get_id_for_day_index(day_index)
        cardio_level = day_framework_collection.get_cardio_for_day_index(day_index)
        workout = _generate_workout(day_framework_id, user, workout_components, cardio_level, list(reversed(previous_workouts)))
        previous_workouts.append(workout)
        new_workouts.append(workout)
    return new_workouts


def _discard_recuperating_muscles(user_exercise_filter, previous_workouts_by_distance):
    for period in reversed(range(MuscleFrequency.get_min_period(), MuscleFrequency.get_max_period())):
        muscle_to_days_worked = defaultdict(int)
        muscle_to_reps = defaultdict(list)
        for workout in previous_workouts_by_distance:
            for muscle_id in set(workout.get_primary_muscle_ids_used()):
                muscle_to_days_worked[muscle_id] += 1
                muscle_to_reps[muscle_id].extend(workout.get_rep_prescriptions_for_muscle(muscle_id))
        for muscle_id, times_worked_this_period in muscle_to_days_worked.items():
            rep_prescriptions = muscle_to_reps[muscle_id]
            if not MuscleFrequency.pass_fail(rep_prescriptions, times_worked_this_period, period):
                user_exercise_filter.discard_muscle_group_id(muscle_id)


def _generate_cardio(user, cardio_level):
    cardio_creator = CardioCreator(user, cardio_level)
    cardio_session = cardio_creator.create()
    return cardio_session


def _generate_workout(day_framework_id, user, workout_component_list, cardio_level, previous_workouts_by_distance):
    if not workout_component_list and cardio_level is None:
        return EmptyWorkout()

    cardio_session = None
    if cardio_level:
        cardio_session = _generate_cardio(user, cardio_level)

    user_exercise_filter = (Exercise().
                            for_fitness_level(user.fitness_level).
                            for_experience(user.experience).
                            for_phase(user.current_phase_id).
                            for_equipment_list(user.get_available_equipment_ids()))

    _discard_recuperating_muscles(user_exercise_filter, previous_workouts_by_distance)

    yesterday_muscle_ids = []
    if len(previous_workouts_by_distance) > 0:
        yesterday_muscle_ids = previous_workouts_by_distance[0].get_muscle_ids_used()

    today_exercise_filter = (user_exercise_filter.
                             copy().
                             exclude_muscle_groups(yesterday_muscle_ids))
    today_exercise_filter = _prioritize_unused_muscle_groups(today_exercise_filter, previous_workouts_by_distance)

    workout = Workout.create_new(day_framework_id, user.current_phase_id, cardio_session=cardio_session)
    workout_component_list = [w for w in workout_component_list if w != WorkoutComponent.FLEXIBILITY]

    for workout_component_id in workout_component_list:
        _add_exercises_for_component(workout_component_id, today_exercise_filter, user, workout)

    _add_flexibility_to_workout(workout, user_exercise_filter.copy())

    _add_more_time(workout)
    _trim_to_time(workout, user)

    return workout


def _prioritize_unused_muscle_groups(today_exercise_filter, previous_workouts_by_distance):
    list_of_sets = MuscleGroup.get_required_rings()
    list_of_tuples = [tuple(muscle_set) for muscle_set in list_of_sets]
    muscle_tuple_to_should_use = {t: True for t in list_of_tuples}
    muscle_id_to_tuple = {}
    for muscle_tuple in muscle_tuple_to_should_use.keys():
        for muscle_id in muscle_tuple:
            muscle_id_to_tuple[muscle_id] = muscle_tuple

    for workout in reversed(previous_workouts_by_distance):
        for muscle_id in workout.get_primary_muscle_ids_used():
            muscle_tuple = muscle_id_to_tuple.get(muscle_id)
            if muscle_tuple:
                muscle_tuple_to_should_use[muscle_tuple] = False
                if not any(muscle_tuple_to_should_use.values()):
                    for muscle_tuple in muscle_tuple_to_should_use.keys():
                        muscle_tuple_to_should_use[muscle_tuple] = True
    remaining_muscle_group_ids = []
    for muscle_tuple, should_use in muscle_tuple_to_should_use.items():
        if should_use:
            remaining_muscle_group_ids.extend(list(muscle_tuple))
    non_repeating_exercise_filter = today_exercise_filter.copy().restrict_to_muscle_group_ids(remaining_muscle_group_ids)
    return non_repeating_exercise_filter


def _add_more_time(workout):
    pass


def _trim_to_time(workout, user):
    items_to_trim = [workout]
    cardio_session = workout.cardio_session
    if cardio_session:
        items_to_trim.append(cardio_session)
    total_time = sum([trimmable.get_total_time() for trimmable in items_to_trim])
    target_time = user.minutes_per_day
    if target_time >= total_time:
        return

    trim_by_percent = 1.0 - (float(target_time) / total_time)
    trim_by_percent = get_new_trim_by_percent(total_time, items_to_trim, trim_by_percent)

    for trimmable in items_to_trim:
        trimmable.trim_by_percent(trim_by_percent)

    workout.refresh_and_save()


def _add_flexibility_to_workout(workout, exercise_filter):
    exercise_filter = exercise_filter.for_workout_component(WorkoutComponent.FLEXIBILITY)
    for muscle_group_id in workout.get_muscle_ids_used():
        possible_exercises = exercise_filter.copy().for_muscle_group(muscle_group_id).query
        possible_exercises = [e for e in possible_exercises]
        try:
            flexibility_exercise = random.choice(possible_exercises)
        except IndexError:
            continue
        workout.add_exercise_set_collection(flexibility_exercise, 1, 30)
        exercise_filter.discard_exercise_id(flexibility_exercise.id)
        exercise_filter.discard_mutually_exclusive(flexibility_exercise.id)


def _add_exercises_for_component(workout_component_id, exercise_filter, user, workout):
    component_filter = exercise_filter.copy().for_workout_component(workout_component_id)

    super_set_manager = SuperSetManager(workout_component_id, user, component_filter)
    component_filter = super_set_manager.get_updated_exercise_filter()
    volume_info = super_set_manager.get_volume_info_first_exercise()
    num_exercises = random.randint(volume_info.min_exercises, volume_info.max_exercises)

    previous_exercise = None
    count_for_current_muscle_group = 0
    exercises_this_component = []

    for _ in xrange(num_exercises):
        if float(count_for_current_muscle_group) / num_exercises >= user.get_exhaustion_percent():
            previous_exercise = None
            count_for_current_muscle_group = 0

        sets, reps = get_reps_sets_from_volume_info(volume_info)
        try:
            exercise = _select_exercise(component_filter.copy(), previous_exercise=previous_exercise)
        except NoExercisesAvailableException:
            previous_exercise = None
            count_for_current_muscle_group = 0
            try:
                exercise = _select_exercise(component_filter.copy(), retry_mode=True)
            except NoExercisesAvailableException:
                continue

        workout.add_exercise_set_collection(exercise, sets, reps)

        component_filter.discard_exercise_id(exercise.id)
        component_filter.discard_mutually_exclusive(exercise.id)
        super_set_manager.add_superset_exercise_to_workout(workout, exercise, component_filter)

        if workout_component_id == WorkoutComponent.RESISTANCE:
            previous_exercise = exercise
            count_for_current_muscle_group += 1

        exercises_this_component.append(exercise)
        if _max_exercises_reached_for_muscle_group_id(user, exercises_this_component, exercise.muscle_group_id):
            component_filter.discard_muscle_group_id(exercise.muscle_group_id)


def _max_exercises_reached_for_muscle_group_id(user, exercises, muscle_group_id):
    minimum, maximum = user.get_min_max_exercises_for_muscle_group_per_day(muscle_group_id)
    relevant_exercises = [e for e in exercises if e.muscle_group_id == muscle_group_id]
    if len(relevant_exercises) > maximum:
        return True
    return False


def _select_exercise(exercise_filter, previous_exercise=None, retry_mode=False):
    if previous_exercise is not None:
        for related_muscle_group_set in MuscleGroup.get_rings():
            if previous_exercise.muscle_group_id in related_muscle_group_set:
                exercise_filter.restrict_to_muscle_group_ids(related_muscle_group_set)
                break
    elif not retry_mode:
        exercise_filter = exercise_filter.compound_only()
    else:
        rollback_filter = exercise_filter.copy()
        exercise_filter = exercise_filter.compound_only()
        if exercise_filter.count() == 0:
            exercise_filter = rollback_filter

    exercise_list = [exercise for exercise in exercise_filter.query]
    exercise_list = evenly_distribute_exercises_by_muscle_group(exercise_list)
    try:
        exercise = random.choice(exercise_list)
    except IndexError:
        raise NoExercisesAvailableException("No exercises left")
    return exercise
