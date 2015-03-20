import datetime
import traceback
# import json
from collections import defaultdict

from workout_generator.logging.user_logger import UserLogger
from workout_generator.constants import WorkoutComponent
from workout_generator.constants import Phase
from workout_generator.constants import MuscleGroup


class WorkoutLogger(object):

    day_to_index = {
        "Sunday": 0,
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6,
    }

    def __init__(self, user):
        self.user_logger = UserLogger.for_user_and_prefix(user, "workout")
        self.user = user
        self.initial_stack_height = None

    def log_start(self):
        self._log("Starting Workout Generation at %s" % datetime.datetime.utcnow())
        # add user's goal, which then has the cardio type
        # and the current phase

    def _log(self, message):
        stack_height = len(traceback.format_stack())
        if self.initial_stack_height is None:
            self.initial_stack_height = stack_height
        offset = stack_height - self.initial_stack_height
        offset_spaces = "".join(["  " for _ in xrange(offset)])
        final_message = "%s%s" % (offset_spaces, message)
        self.user_logger.add_message(final_message)

    def log_initial_day_framework_collection(self, day_framework_collection):
        for day_name, isoweekday in self.day_to_index.items():
            cardio_level = day_framework_collection.get_cardio_for_day_index(isoweekday)
            self._log("(Initial Day Framework) Cardio level on UTC %s is %s" % (day_name, cardio_level or "no cardio"))
            workout_component_ids = day_framework_collection.get_workout_components_for_day_index(isoweekday)
            component_str = ", ".join([WorkoutComponent.get_by_id(id).title for id in workout_component_ids])
            self._log("(Initial Day Framework) Workout components on %s: %s" % (day_name, component_str))

    def log_recreate_filter(self):
        self._log("Recreating exercise filter")

    def log_dead_end_for_component(self, workout_component_id):
        workout_component = WorkoutComponent.get_by_id(workout_component_id).title
        self._log("No exercises available for current filter for %s" % workout_component)

    def log_no_more_for_component(self, workout_component_id, exception):
        workout_component = WorkoutComponent.get_by_id(workout_component_id).title
        self._log("Not commiting anymore exercises for %s (%s)" % (workout_component, exception))

    def log_empty_workout(self):
        self._log("Returning an empty workout")

    def log_initial_cardio_session(self, cardio_session):
        self._log("Initial cardio session completed:")
        # cardio_str = json.dumps(cardio_session.to_json(), indent=4)
        # self._log(cardio_str)
        self._log("Initial cardio total time: %s" % cardio_session.get_total_time())

    def log_user_exercise_filter(self, exercise_filter):
        self._log("Starting individual workout generation.  User for " +
                "fitness %s, experience %s, phase %s, and %s equipment items: %s" %
                (
                    self.user.fitness_level,
                    self.user.experience,
                    Phase.get_by_id(self.user.current_phase_id).title,
                    len(self.user.get_available_equipment_ids()),
                    exercise_filter.count()
                )
        )

    def log_initial_today_exercise_filter(self, exercise_filter):
        self._log("Initial Exercise Filter for today (after previous workouts accounted for): %s" % exercise_filter.count())

    def log_retry_today_exercise_filter(self, exercise_filter):
        self._log("Loosened constraints on exercise filter, now have: %s available exercises" % exercise_filter.count())

    def log_component_filter(self, workout_component_id, exercise_filter):
        component_title = WorkoutComponent.get_by_id(workout_component_id).title
        self._log("For %s, %s exercises available" % (component_title, exercise_filter.count()))

    def log_filter_before_action(self, exercise_filter, action):
        self._log("About to discard exercises (%s), %s are available before action" % (action, exercise_filter.count()))
        workout_component_to_count = defaultdict(int)
        for exercise in exercise_filter.query:
            workout_component_to_count[exercise.workout_component_id] += 1
        workout_component_to_count = {WorkoutComponent.get_by_id(k).title: v for k, v in workout_component_to_count.items()}
        for k, v in workout_component_to_count.items():
            self._log("  %s: %s" % (k, v))

    def log_available_exercises(self, exercise_list):
        available_muscle_group_ids = []
        workout_component = "(No available exercises)"
        if exercise_list:
            workout_component = WorkoutComponent.get_by_id(exercise_list[0].workout_component_id).title

        self._log("Before exercise selection, %s exercises are available for %s" % (len(exercise_list), workout_component))
        for exercise in exercise_list:
            available_muscle_group_ids.append(exercise.muscle_group_id)
        available_muscle_group_ids = list(set(available_muscle_group_ids))
        muscle_names = ", ".join([MuscleGroup.get_name_for_id(id) for id in available_muscle_group_ids])
        self._log("Available muscle groups: %s" % muscle_names)

    def log_available_superset_exercise(self, exercise_list):
        available_muscle_group_ids = []
        workout_component = "(No available exercises)"
        if exercise_list:
            workout_component = WorkoutComponent.get_by_id(exercise_list[0].workout_component_id).title

        self._log("Before Superset exercise selection, %s exercises are available for %s" % (len(exercise_list), workout_component))
        for exercise in exercise_list:
            available_muscle_group_ids.append(exercise.muscle_group_id)
        available_muscle_group_ids = list(set(available_muscle_group_ids))
        muscle_names = ", ".join([MuscleGroup.get_name_for_id(id) for id in available_muscle_group_ids])
        self._log("Available superset muscle groups: %s" % muscle_names)

    def log_superset_exercise(self, exercise):
        if exercise is None:
            self._log("Superset exercise is None, nothing was available")
        else:
            self._log("Superset Exercise selected: %s (Muscle Group: %s)\n" % (exercise.name, MuscleGroup.get_name_for_id(exercise.muscle_group_id)))

    def log_exercise_selection(self, exercise):
        self._log("Exercise selected: %s (Muscle Group: %s)\n" % (exercise.name, MuscleGroup.get_name_for_id(exercise.muscle_group_id)))

    def log_previous_workouts(self, previous_workouts):
        self._log("%s previous workouts exist" % len(previous_workouts))

    def log_muscle_restriction(self, previous_exercise, related_muscle_group_set):
        self._log("Previous exercise was %s with muscle group %s" % (previous_exercise.name, MuscleGroup.get_name_for_id(previous_exercise.muscle_group_id)))
        muscle_names = ", ".join([MuscleGroup.get_name_for_id(id) for id in related_muscle_group_set])
        self._log("Restricting to muscle groups: %s" % muscle_names)

    def log_end(self):
        self._log("Ending Workout Generation at %s\n" % datetime.datetime.utcnow())

    def log_finish_workout(self, workout):
        self._log("===========Finished generating a workout========")

    def log_start_workout(self, workout_component_ids):
        self._log("===========Starting workout generation=========")
        component_str = ", ".join([WorkoutComponent.get_by_id(id).title for id in workout_component_ids])
        if not workout_component_ids:
            component_str = "NONE"
        self._log("Workout components for this workout: %s" % component_str)

    def log_num_exercises(self, volume_info, num_exercises, workout_component_id):
        workout_component = WorkoutComponent.get_by_id(workout_component_id).title
        self._log("Volume for %s: Range is [%s, %s], selected %s" %
                (workout_component, volume_info.min_exercises, volume_info.max_exercises, num_exercises))

    def log_retry_mode(self):
        self._log("Selecting first exercise, restricting to compound only")

    def log_rollback_mode(self):
        self._log("Retrying for first exercise, allowing isolated movements")

    def log_add_more_time(self, target_time, current_time, workout_component_id):
        workout_component = WorkoutComponent.get_by_id(workout_component_id).title
        self._log("Trying to add more time.  Current time is %s, target time is %s.  Adding for %s" %
                (current_time, target_time, workout_component))

    def log_muscle_exhausted(self):
        self._log("UNREACHED CASE")

    def log_muscle_max_reached(self, muscle_group_id):
        muscle_group = MuscleGroup.get_name_for_id(muscle_group_id)
        self._log("Max exercises reached for %s, re-opening filter to other muscles" % muscle_group)

    def log_retry_select_exercise(self):
        self._log("No exercises available, discarding previous exercise constraint")

    def log_supersetting(self, is_supersetting):
        if is_supersetting:
            self._log("This workout does have supersetting")
        else:
            self._log("This workout does NOT have supersetting")

    def log_day(self, isoweekday):
        index_to_day = {v: k for k, v in self.day_to_index.items()}
        day_str = index_to_day[isoweekday]
        self._log("Starting workout generation for UTC %s" % day_str)

    def log_super_set_filter_update(self, component_filter, initial_count):
        self._log("After super set filter applied, %s exercises dropped (%s to %s)" %
                (initial_count - component_filter.count(), initial_count, component_filter.count()))

    def log_superset_filters(self, first_filter, second_filter):
        self._log("Filtering by exercise type. %s exercises are in first filter, %s are in the superset filter" %
                (first_filter.count(), second_filter.count()))

    @classmethod
    def for_user(self, user):
        return WorkoutLogger(user)

    def commit(self):
        self.user_logger.commit()
