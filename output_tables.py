from workout_generator.constants import *
from collections import Sequence

output_clses = [
    CardioMax,
    CardioZone,
    HardcodedRule,
    WorkoutComponentFrequency,
    Exhaustion,
    ExercisesPerMuscleGroup,
    CardioVolume,
    LiftingVolume,
    PhaseLengthByGoal,
    Phase,
    MuscleGroup,
    WorkoutComponent,
]

def _format(item):
    if isinstance(item, tuple):
        return "|".join([str(i) for i in item])

    # if isinstance(item, tuple):
    #     return " - ".join(str(item))
    return str(item)


with open("data.csv", "w+") as f:
    for cls in output_clses:
        f.write(str(cls).split(".")[-1])
        f.write("\n")
        f.write("\n")
        for data_list in cls.VALUES:
            print data_list
            output_str = ",".join([_format(item) for item in data_list])
            f.write(output_str)
            f.write("\n")
        f.write("\n")
        f.write("\n")
