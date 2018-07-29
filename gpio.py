import os

def __run_or_die(cmd):
    if 0 != os.system(cmd):
        raise Exception(f"Failed to run {cmd}")

def mode_out(pin):
    cmd = f"gpio mode {pin} out"
    __run_or_die(cmd)

def mode_in(pin):
    cmd = f"gpio mode {pin} in"
    __run_or_die(cmd)
