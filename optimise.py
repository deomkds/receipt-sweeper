# Builtin.
import os
import subprocess
# First party.
from simplelog import log as dbgln

def optimise_png(file_path):
    original_file_size_in_kib = float(os.path.getsize(file_path)) / 1024

    obj_data = subprocess.run(["oxipng", "-s", "-t", "1", "-a", "-p", "-o", "5", file_path], capture_output=True)
    raw_output = obj_data.stderr.decode("utf-8").split("\n")

    try:
        optimised_file_size_in_kib = float(raw_output[1].split(" ")[0]) / 1024
        reduction_percentage = raw_output[1].split(" ")[2][1:-1]
    except ValueError:
        optimised_file_size_in_kib = original_file_size_in_kib
        reduction_percentage = 0

    dbgln(f"PNG file size optimised by {reduction_percentage}%, "
        f"reduced from {original_file_size_in_kib:.2f} KiB to {optimised_file_size_in_kib:.2f} KiB.", True)
    return


def optimise_jpg(file_path):
    original_file_size_in_kib = float(os.path.getsize(file_path)) / 1024

    obj_data = subprocess.run(["jpegoptim", "-p", "-t", "-s", "-w1", file_path], capture_output=True)
    raw_output = obj_data.stdout.decode("utf-8").split("\n")

    try:
        optimised_file_size_in_kib = float(raw_output[0].split(" [OK] ")[1].split(" ")[2]) / 1024
        reduction_percentage = raw_output[0].split(" [OK] ")[1].split(" ")[4][1:-3]
    except ValueError:
        optimised_file_size_in_kib = original_file_size_in_kib
        reduction_percentage = 0

    dbgln(f"JPG file size optimised by {reduction_percentage}%, "
        f"reduced from {original_file_size_in_kib:.2f} KiB to {optimised_file_size_in_kib:.2f} KiB.", True)
    return