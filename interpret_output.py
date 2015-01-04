import json

def build(tuple_data):
    return {
        "id": tuple_data[0],
        "video_id": tuple_data[1],
        "name": tuple_data[3],
        "multi_joint": tuple_data[4],
        "min_fitness_level_id": tuple_data[5],
        "min_experience_id": tuple_data[6],
        "muscle_group_id": tuple_data[7],
        "secondary_muscle_group_id": tuple_data[8],
        "workout_compnent_id": tuple_data[9],
        "compound": tuple_data[10],
        "progressor": tuple_data[11],
        "timed": tuple_data[12],
        "one_limb": tuple_data[13],
        "exercise_type_id": tuple_data[16],
        "mutually_exclusive": tuple_data[17],
    }


if __name__ == "__main__":
    json_data = []
    with open("output.csv", "rb") as f:
        for line in f.readlines():
            line = line[1: -3]
            tuple_data = line.split(",")
            tuple_data = [i if i != "NULL" else None for i in tuple_data]
            if len(tuple_data) != 20:
                tuple_data = tuple_data[0:3] + [",".join(tuple_data[3: len(tuple_data) - 16])] + tuple_data[len(tuple_data) - 16:]
            for index, item in enumerate(tuple_data):
                try:
                    tuple_data[index] = int(item)
                except (TypeError, ValueError):
                    if item:
                        tuple_data[index] = item.replace("'", "")
            json_data.append(build(tuple_data))
    with open("exercises.json", "w+") as f:
        f.write(json.dumps(json_data, indent=4))
'''
+-------------------------+--------------+------+-----+---------+----------------+
| Field                   | Type         | Null | Key | Default | Extra          |
+-------------------------+--------------+------+-----+---------+----------------+
| id                      | int(11)      | NO   | PRI | NULL    | auto_increment |
| url                     | varchar(200) | NO   |     | NULL    |                |
| url2                    | varchar(200) | YES  |     | NULL    |                |
| name                    | varchar(100) | NO   |     | NULL    |                |
| multiJoint              | tinyint(1)   | YES  |     | NULL    |                |
| minFitnessLevel_id      | int(11)      | NO   | MUL | NULL    |                |
| minExperience_id        | int(11)      | NO   | MUL | NULL    |                |
| muscleGroup_id          | int(11)      | NO   | MUL | NULL    |                |
| secondaryMuscleGroup_id | int(11)      | YES  | MUL | NULL    |                |
| workoutComponent_id     | int(11)      | YES  | MUL | NULL    |                |
| compound                | tinyint(1)   | NO   |     | NULL    |                |
| progressor              | int(11)      | YES  |     | NULL    |                |
| timed                   | tinyint(1)   | YES  |     | NULL    |                |
| oneLimb                 | tinyint(1)   | YES  |     | NULL    |                |
| lastModified            | datetime     | YES  |     | NULL    |                |
| dayOfWeek               | varchar(20)  | YES  |     | NULL    |                |
| exerciseType2_id        | int(11)      | YES  | MUL | NULL    |                |
| mutuallyExclusive       | int(11)      | YES  |     | NULL    |                |
| workoutComponent2_id    | int(11)      | YES  | MUL | NULL    |                |
| workoutComponent3_id    | int(11)      | YES  | MUL | NULL    |                |
+-------------------------+--------------+------+-----+---------+----------------+
'''
