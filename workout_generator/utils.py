import json


def read_file(file_path, mode="r"):
    with open(file_path, mode=mode) as fptr:
        return fptr.read()


def read_file_as_json(file_path, mode="r"):
    return json.loads(read_file(file_path, mode=mode))


def base_round(x, base=5):
    return int(base * round(float(x) / base))


def get_new_trim_by_percent(parent_total_time, items_to_trim, target_percent):
    # TODO add test coverage for this func
    total_percent_trimmable = 0.0
    for trimmable in items_to_trim:
        percent_of_parent = trimmable.get_total_time() / parent_total_time
        percent_trimmable_of_parent = trimmable.percent_trimmable * percent_of_parent
        total_percent_trimmable += percent_trimmable_of_parent

    if total_percent_trimmable < 1.0:
        target_percent *= (1.0 / total_percent_trimmable)

    return target_percent
