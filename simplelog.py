# Bultin.
import os
from datetime import datetime
# First party.
import config


def log(text, essential=False, line_break=False):
    if config.VERBOSE or essential:
        moment_obj = datetime.now()
        moment = moment_obj.strftime("%Y-%m-%d %H:%M:%S")
        path = os.path.join(config.src_path, 'rename_log.txt')
        br = f"\n" if line_break else f""
        output_line = f"{br}{moment}: {config.current_file} -> {text}"
        print(output_line)
        with open(path, "a") as log_file:
            log_file.write(f"{output_line}\n")
