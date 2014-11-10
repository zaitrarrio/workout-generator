import sys


def _output_comments(raw_text_list):
    prev_end = "    )\n\n"
    descriptors = "    # %s\n" % ", ".join(raw_text_list)
    code_start = "    VALUES = (\n"
    return prev_end + descriptors + code_start


def _output_tuple(raw_text_list):
    casted_list = []
    for item in raw_text_list:
        try:
            item = int(item)
            casted_list.append(str(item))
        except ValueError:
            casted_list.append("\"%s\"" % item)
    return "        (%s),\n" % ", ".join(casted_list)


def parse_line(line):
    raw_text = [text.strip() for text in line.split("|")]
    raw_text = [item for item in raw_text if item]

    is_descriptor_list = True
    for field in raw_text:
        try:
            int(field)
            is_descriptor_list = False
        except ValueError:
            # not an int
            pass
    if is_descriptor_list:
        return _output_comments(raw_text)
    else:
        return _output_tuple(raw_text)


def transform_file(filename):
    new_file = ""
    with open(filename, "rb") as file:
        for line in file.readlines():
            if line.startswith("|"):
                new_code = parse_line(line)
                new_file += new_code
    with open("output.py", "w+") as file:
        file.write(new_file)


if __name__ == "__main__":
    filename = sys.argv[1]
    transform_file(filename)
