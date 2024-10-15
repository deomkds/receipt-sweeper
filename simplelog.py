import os
from datetime import datetime


def log(text, src_path, current_file, line_break=False):
    moment_obj = datetime.now()
    moment = moment_obj.strftime("%Y-%m-%d %H:%M:%S")
    path = os.path.join(src_path, 'rename_log.txt')
    br = f"\n" if line_break else f""
    output_line = f"{br}{moment}: {current_file} -> {text}"
    print(output_line)
    with open(path, "a") as log_file:
        log_file.write(f"{output_line}\n")
