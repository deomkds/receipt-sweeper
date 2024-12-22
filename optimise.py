# Builtin.
import os
import subprocess
# First party.
import config
from simplelog import log


def optimise(file_path):
    if not config.OPTIMISE:
        log(f"Optimise is disabled.", True)
        return None

    extension = file_path.split('.')[-1]

    if extension.startswith(".pn"):
        optimise_png(file_path)
    elif extension.startswith(".jp"):
        optimise_jpg(file_path)
    else:
        log(f"File is not JPEG or PNG. Leaving as is...", True)


def optimise_png(file_path):
    log(f"Optimising with 'oxipng'...")

    original_file_size_in_kib = float(os.path.getsize(file_path)) / 1024

    obj_data = subprocess.run(["oxipng", "-s", "-t", "1", "-a", "-p", "-o", "5", file_path], capture_output=True)
    raw_output = obj_data.stderr.decode("utf-8").split("\n")

    try:
        optimised_file_size_in_kib = float(raw_output[1].split(" ")[0]) / 1024
        reduction_percentage = raw_output[1].split(" ")[2][1:-1]
    except ValueError:
        optimised_file_size_in_kib = original_file_size_in_kib
        reduction_percentage = 0

    log(f"PNG file size optimised by {reduction_percentage}%, "
        f"reduced from {original_file_size_in_kib:.2f} KiB to {optimised_file_size_in_kib:.2f} KiB.", True)
    return


def optimise_jpg(file_path):
    log(f"Optimising with 'jpegoptim'...")

    original_file_size_in_kib = float(os.path.getsize(file_path)) / 1024

    obj_data = subprocess.run(["jpegoptim", "-p", "-t", "-s", "-w1", file_path], capture_output=True)
    raw_output = obj_data.stdout.decode("utf-8").split("\n")

    try:
        optimised_file_size_in_kib = float(raw_output[0].split(" [OK] ")[1].split(" ")[2]) / 1024
        reduction_percentage = raw_output[0].split(" [OK] ")[1].split(" ")[4][1:-3]
    except ValueError:
        optimised_file_size_in_kib = original_file_size_in_kib
        reduction_percentage = 0

    log(f"JPG file size optimised by {reduction_percentage}%, "
        f"reduced from {original_file_size_in_kib:.2f} KiB to {optimised_file_size_in_kib:.2f} KiB.", True)
    return