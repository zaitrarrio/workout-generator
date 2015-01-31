import json
import traceback
from workout_generator.mailgun.tasks import send_email_with_data


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


def email_admin_on_exception(fn):
    def inner(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
        except Exception as e:
            stack_trace = traceback.format_exc()
            notify_admin(e, stack_trace)
            raise e
        return result
    return inner


def notify_admin(exception, stack_trace):
    text = "Exception: %s\n\n" % exception
    text += stack_trace
    if hasattr(exception, "message"):
        text += "\n%s" % exception.message
    send_email_with_data("scott.lobdell@gmail.com", "Workout Generator Error!", text)
