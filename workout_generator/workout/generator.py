import random

from collections import defaultdict

from workout_generator.constants import CardioMax
from workout_generator.constants import Exercise
from workout_generator.constants import MuscleGroup
from workout_generator.constants import MuscleFrequency
from workout_generator.constants import WorkoutComponent
from workout_generator.utils import get_new_trim_by_percent
from workout_generator.workout.cardio_creator import CardioCreator
from workout_generator.workout.exceptions import DeadEndException
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
    workout_collection = WorkoutCollection(new_workouts, day_framework_collection)
    _swap_empty_workouts(workout_collection)
    _swap_one_cardio_day(workout_collection)
    for workout in workout_collection.workout_list:
        _trim_to_time(workout, user)

    old_framework.delete()
    return workout_collection


def _generate_day_frameworks(user):
    isoweekday_to_components = _fill_isoweekdays_with_workout_components(user)
    isoweekday_to_cardio_intensity = _fill_isoweekdays_with_cardio_intensity(user, isoweekday_to_components)
    _mandate_cardio_or_resistance(isoweekday_to_components, isoweekday_to_cardio_intensity)
    _evenly_distribute_cardio_lifting_days(isoweekday_to_components, isoweekday_to_cardio_intensity)
    return DayFrameworkCollection.create(user, isoweekday_to_components, isoweekday_to_cardio_intensity)


def _evenly_distribute_cardio_lifting_days(isoweekday_to_components, isoweekday_to_cardio_intensity):
    enabled_isoweekdays = list(set(isoweekday_to_cardio_intensity.keys() + isoweekday_to_components.keys()))
    cardio_intensities = [0] * len(enabled_isoweekdays)

    index = 0
    cardio_intensity_to_isoweekday = defaultdict(list)
    for isoweekday, intensity in isoweekday_to_cardio_intensity.items():
        cardio_intensities[index] = intensity
        cardio_intensity_to_isoweekday[intensity].append(isoweekday)
        index += 1

    scrambled_cardio_intensities = _scramble_list_by_alternating_intensities(cardio_intensities)
    sorted_isoweekdays = sorted(enabled_isoweekdays)
    for index, cardio_intensity in enumerate(scrambled_cardio_intensities):
        if cardio_intensity:
            old_isoweekday = cardio_intensity_to_isoweekday[cardio_intensity].pop()
            new_isoweekday = sorted_isoweekdays[index]

            _swap_dict_values(isoweekday_to_components, old_isoweekday, new_isoweekday)
            _swap_dict_values(isoweekday_to_cardio_intensity, old_isoweekday, new_isoweekday)


def _swap_dict_values(dictionary, old_key, new_key):
    temp_value = dictionary[old_key]
    if new_key in dictionary:
        dictionary[old_key] = dictionary[new_key]
    else:
        del dictionary[old_key]
    dictionary[new_key] = temp_value


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


def _swap_empty_workouts(workout_collection):
    ''' This is a fairly extreme edge case '''
    cardio_and_lifting = []
    no_cardio_no_lifting = []
    for workout in workout_collection.workout_list:
        if not workout.can_manipulate():
            continue
        if workout.needs_populate():
            no_cardio_no_lifting.append(workout)
        if workout.has_cardio() and workout.has_lifting():
            cardio_and_lifting.append(workout)
    day_framework_collection = workout_collection.day_framework_collection
    while no_cardio_no_lifting and len(no_cardio_no_lifting) < len(cardio_and_lifting):
        empty_workout = no_cardio_no_lifting.pop(0)
        full_workout = cardio_and_lifting.pop(0)
        day_framework_collection.swap_cardio_for_workouts(empty_workout, full_workout)


def _swap_one_cardio_day(workout_collection):
    '''
    Helps to balance out the volume in the week.  Restricted to just
    one day because it otherwise destroys the previous logic of spreading out cardio through the week
    '''
    cardio_and_lifting = [workout for workout in workout_collection.workout_list
            if workout.can_manipulate() and workout.has_cardio() and workout.has_lifting()]
    lifting_only = [workout for workout in workout_collection.workout_list
            if workout.can_manipulate() and not workout.has_cardio() and workout.has_lifting()]
    if not lifting_only or not cardio_and_lifting:
        return
    smallest_lifting = sorted(lifting_only, key=lambda w: w.get_total_time())[0]
    largest_with_cardio = sorted(cardio_and_lifting, key=lambda w: w.get_total_time(), reverse=True)[0]
    if largest_with_cardio.get_total_time() > smallest_lifting.get_total_time():
        day_framework_collection = workout_collection.day_framework_collection
        day_framework_collection.swap_cardio_for_workouts(smallest_lifting, largest_with_cardio)


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


def _get_today_exercise_filter(user_exercise_filter, previous_workouts_by_distance, retry_count=0):
    today_exercise_filter = user_exercise_filter.copy()

    retry_mode = False
    if retry_count >= 1:
        retry_mode = True
    _discard_yesterday_muscles(today_exercise_filter, previous_workouts_by_distance, retry_mode=retry_mode)

    if retry_count <= 2:
        today_exercise_filter = _prioritize_unused_muscle_groups(user_exercise_filter, today_exercise_filter, previous_workouts_by_distance)

    if retry_count <= 3:
        _discard_recuperating_muscles(today_exercise_filter, previous_workouts_by_distance)

    _discard_previous_exercises(today_exercise_filter, previous_workouts_by_distance)
    return today_exercise_filter


def _discard_previous_exercises(exercise_filter, previous_workouts_by_distance, days=4):
    for previous_workout in previous_workouts_by_distance[:days]:
        exercise_ids = previous_workout.get_exercise_ids_used()
        for exercise_id in exercise_ids:
            exercise_filter.discard_exercise_id(exercise_id)


def _discard_yesterday_muscles(exercise_filter, previous_workouts_by_distance, retry_mode=False):
    if not previous_workouts_by_distance:
        return
    if retry_mode:
        yesterday_muscle_ids = previous_workouts_by_distance[0].get_primary_muscle_ids_used()
    else:
        yesterday_muscle_ids = previous_workouts_by_distance[0].get_muscle_ids_used()
    exercise_filter.exclude_muscle_groups(yesterday_muscle_ids)


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

    workout = Workout.create_new(day_framework_id, user.current_phase_id, cardio_session=cardio_session)
    workout_component_list = [w for w in workout_component_list if w != WorkoutComponent.FLEXIBILITY]

    today_exercise_filter = _get_today_exercise_filter(user_exercise_filter, previous_workouts_by_distance)
    max_retries = 5
    for workout_component_id in workout_component_list:
        temp_filter = today_exercise_filter
        for dead_end_count in xrange(max_retries):
            try:
                _add_exercises_for_component(workout_component_id, temp_filter, user, workout)
                break
            except DeadEndException:
                temp_filter = _get_today_exercise_filter(user_exercise_filter, previous_workouts_by_distance, retry_count=dead_end_count)
        # re-gain state with temp_filter
        today_exercise_filter = Exercise.join_and(today_exercise_filter, temp_filter)

    target_time = user.minutes_per_day
    cardio_time = (0 if not cardio_session else cardio_session.get_total_time())
    for workout_component_id in (10 * workout_component_list):
        total_time = cardio_time + workout.get_total_time()
        if total_time >= target_time - 5:
            break
        try:
            _add_exercises_for_component(workout_component_id, today_exercise_filter, user, workout, force_one=True)
        except DeadEndException:
            continue

    _add_flexibility_to_workout(workout, user_exercise_filter.copy())
    return workout


def _prioritize_unused_muscle_groups(user_exercise_filter, today_exercise_filter, previous_workouts_by_distance):
    component_filters = []
    for workout_component_id in WorkoutComponent.WORKOUT_ORDER:
        muscle_tuple_to_should_use = _get_muscle_tuple_to_should_use(user_exercise_filter, workout_component_id)
        _discard_or_reset_muscle_tuples(muscle_tuple_to_should_use, previous_workouts_by_distance, workout_component_id)
        remaining_muscle_group_ids = _get_remaining_muscle_groups(muscle_tuple_to_should_use)
        non_repeating_component_filter = (today_exercise_filter.copy().
                                          for_workout_component(workout_component_id).
                                          restrict_to_muscle_group_ids(remaining_muscle_group_ids))
        component_filters.append(non_repeating_component_filter)
    non_repeating_exercise_filter = Exercise.join(*component_filters)
    return non_repeating_exercise_filter


def _get_muscle_tuple_to_should_use(user_exercise_filter, workout_component_id):
    usable_muscle_group_ids = user_exercise_filter.copy().for_workout_component(workout_component_id).get_muscle_group_ids()

    list_of_sets = MuscleGroup.get_required_rings()
    for index in xrange(len(list_of_sets)):
        list_of_sets[index] = {item for item in list_of_sets[index] if item in usable_muscle_group_ids}

    list_of_tuples = [tuple(muscle_set) for muscle_set in list_of_sets if muscle_set]
    muscle_tuple_to_should_use = {t: True for t in list_of_tuples}
    return muscle_tuple_to_should_use


def _get_muscle_id_to_tuple(muscle_tuple_to_should_use):
    muscle_id_to_tuple = {}
    for muscle_tuple in muscle_tuple_to_should_use.keys():
        for muscle_id in muscle_tuple:
            muscle_id_to_tuple[muscle_id] = muscle_tuple
    return muscle_id_to_tuple


def _get_remaining_muscle_groups(muscle_tuple_to_should_use):
    remaining_muscle_group_ids = []
    for muscle_tuple, should_use in muscle_tuple_to_should_use.items():
        if should_use:
            remaining_muscle_group_ids.extend(list(muscle_tuple))
    return remaining_muscle_group_ids


def _discard_or_reset_muscle_tuples(muscle_tuple_to_should_use, previous_workouts_by_distance, workout_component_id):
    muscle_id_to_tuple = _get_muscle_id_to_tuple(muscle_tuple_to_should_use)
    for workout in reversed(previous_workouts_by_distance):
        for muscle_id in workout.get_primary_muscle_ids_used(workout_component_id=workout_component_id):
            muscle_tuple = muscle_id_to_tuple.get(muscle_id)
            if muscle_tuple:
                muscle_tuple_to_should_use[muscle_tuple] = False
                if not any(muscle_tuple_to_should_use.values()):
                    for muscle_tuple in muscle_tuple_to_should_use.keys():
                        muscle_tuple_to_should_use[muscle_tuple] = True


def _trim_to_time(workout, user):
    if not workout.can_manipulate():
        return
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


def _add_exercises_for_component(workout_component_id, exercise_filter, user, workout, force_one=False):
    component_filter = exercise_filter.copy().for_workout_component(workout_component_id)
    if len(component_filter.query) == 0:
        raise DeadEndException("No Exercises Available")

    super_set_manager = SuperSetManager(workout_component_id, user, component_filter)
    component_filter = super_set_manager.get_updated_exercise_filter()
    volume_info = super_set_manager.get_volume_info_first_exercise()
    num_exercises = random.randint(volume_info.min_exercises, volume_info.max_exercises)

    if force_one:
        current_count = len(workout.get_exercise_ids_used(workout_component_id=workout_component_id))
        if current_count >= volume_info.max_exercises:
            return
        num_exercises = 1

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
    exercise_filter.intersect(component_filter)


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
