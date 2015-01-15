import random
from collections import defaultdict


def get_reps_sets_from_volume_info(volume_info):
    reps = random.randint(volume_info.min_reps, volume_info.max_reps)
    reps = _make_reps_human_acceptable(reps)
    sets = random.randint(volume_info.min_sets, volume_info.max_sets)
    return sets, reps


def evenly_distribute_exercises_by_muscle_group(exercise_list):
    times_to_represent_muscle = 100
    exercise_list_with_duplicates = []
    exercises_by_muscle_group_id = defaultdict(list)
    for exercise in exercise_list:
        exercises_by_muscle_group_id[exercise.muscle_group_id].append(exercise)

    for muscle_group_id, exercise_list in exercises_by_muscle_group_id.items():
        random.shuffle(exercise_list)
        repeated_list = [exercise_list[i % len(exercise_list)] for i in xrange(times_to_represent_muscle)]
        exercise_list_with_duplicates.extend(repeated_list)
    return exercise_list_with_duplicates


def _make_reps_human_acceptable(reps):
    if reps > 6 and reps % 2 == 1:
        reps += 1
    if reps == 14:
        reps = 15
    return reps
