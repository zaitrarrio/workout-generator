import random

from workout_generator.constants import ExerciseType
from workout_generator.constants import Phase
from workout_generator.constants import WorkoutComponent
from workout_generator.constants import MuscleGroup
from workout_generator.workout.utils import get_reps_sets_from_volume_info
from workout_generator.workout.utils import evenly_distribute_exercises_by_muscle_group


class SuperSetManager(object):

    def __init__(self, workout_component_id, user, exercise_filter):
        self.supersetting = workout_component_id == WorkoutComponent.RESISTANCE and user.current_phase_id in Phase.SUPERSET_PHASES
        self.first_exercise_filter = exercise_filter
        self.first_volume_info = user.get_volume_for_workout_component(workout_component_id)
        self.workout_component_id = workout_component_id
        self.logger = user.workout_logger
        if self.supersetting:
            self._update_exercise_filters(user)
            self._update_volumes(user)
        self.logger.log_supersetting(self.supersetting)

    def _update_exercise_filters(self, user):
        self.superset_filter = self.first_exercise_filter.copy()
        self.first_exercise_filter = self.first_exercise_filter.for_exercise_type(ExerciseType.STRENGTH)
        if user.current_phase_id == Phase.MUSCLE_ENDURANCE:
            self.superset_filter = self.superset_filter.for_exercise_type(ExerciseType.STABILIZATION)
        elif user.current_phase_id == Phase.POWER:
            self.superset_filter = self.superset_filter.for_exercise_type(ExerciseType.POWER)
        self.logger.log_superset_filters(self.first_exercise_filter, self.superset_filter)

    def _update_volumes(self, user):
        if user.current_phase_id == Phase.MUSCLE_ENDURANCE:
            self.first_volume_info = user.get_volume_for_workout_component(self.workout_component_id, force_different_phase=Phase.HYPERTROPHY)
            self.second_volume_info = user.get_volume_for_workout_component(self.workout_component_id, force_different_phase=Phase.STABILIZATION)

        elif user.current_phase_id == Phase.POWER:
            self.first_volume_info = user.get_volume_for_workout_component(self.workout_component_id, force_different_phase=Phase.MAXIMAL_STRENGTH)
            self.second_volume_info = user.get_volume_for_workout_component(self.workout_component_id, force_different_phase=Phase.POWER)

    def get_updated_exercise_filter(self):
        return self.first_exercise_filter

    def get_volume_info_first_exercise(self):
        return self.first_volume_info

    def add_superset_exercise_to_workout(self, workout, first_exercise, first_exercise_filter):
        if not self.supersetting:
            return
        _, reps = get_reps_sets_from_volume_info(self.second_volume_info)
        second_exercise = self._select_superset_exercise(first_exercise)
        if second_exercise:
            workout.add_superset_to_exercise(first_exercise, second_exercise, reps)
            self._discard_exercise_from_filters(second_exercise, first_exercise_filter)

    def _discard_exercise_from_filters(self, exercise, first_exercise_filter):
        first_exercise_filter.discard_exercise_id(exercise.id)
        first_exercise_filter.discard_mutually_exclusive(exercise.id)

        self.superset_filter.discard_exercise_id(exercise.id)
        self.superset_filter.discard_mutually_exclusive(exercise.id)

    def _select_superset_exercise(self, first_exercise):
        self.superset_filter.discard_exercise_id(first_exercise.id)
        self.superset_filter.discard_mutually_exclusive(first_exercise.id)

        possible_muscle_ids = [first_exercise.muscle_group_id]
        possible_muscle_ids += MuscleGroup.ALLOWABLE_RELATED_FOR_SUPERSETS.get(first_exercise.muscle_group_id, [])

        exercise_filter = self.superset_filter.copy().restrict_to_muscle_group_ids(possible_muscle_ids)
        exercise_list = [exercise for exercise in exercise_filter.query]
        self.logger.log_available_superset_exercise(exercise_list)
        exercise_list = evenly_distribute_exercises_by_muscle_group(exercise_list)
        try:
            exercise = random.choice(exercise_list)
        except IndexError:
            exercise = None
        self.logger.log_superset_exercise(exercise)
        return exercise
