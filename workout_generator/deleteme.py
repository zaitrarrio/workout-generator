import json

with open("exercises.json", "rb") as f:
    content = f.read()
    json_data = json.loads(content)

with open("output.html", "w+") as f:
    for exercise_json in json_data:
        video_id = exercise_json["video_id"]
        f.write(exercise_json["name"] + "<br/>")
        f.write('''<video class="exercise-video" id="video_exercise_<%= exerciseSet.superset.exercise.id %>" autoplay="" loop="" poster="true" width="480" height="360">\
<source src="https://s3-us-west-1.amazonaws.com/workout-generator-exercises/smaller_webm/small_''' + video_id  + '''.webmsd.webm" type="video/webm" class="webmsource">\
</video>''')
        f.write("<br/><br/><br/><br/>")
