import json

with open("exercises.json", "rb") as f:
    json_content = f.read()
    exercise_list = json.loads(json_content)


with open("video_output.json", "rb") as f:
    json_content = f.read()
    end_index = json_content.index("}") + 1
    json_dict = json.loads(json_content[:end_index])
    for video_id, gfy_name in json_dict.items():
        for exercise_dict in exercise_list:
            if exercise_dict["video_id"] == video_id:
                exercise_dict["gfy_name"] = gfy_name
    for exercise_dict in exercise_list:
        if "gfy_name" not in exercise_dict:
            exercise_dict["gfy_name"] = None


with open("exercises2.json", "w+") as f:
    f.write(json.dumps(exercise_list, indent=4))
