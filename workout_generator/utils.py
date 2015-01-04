import simplejson as json


def read_file_as_json(file_path, mode="r"):
    return json.loads(read_file(file_path, mode=mode))
