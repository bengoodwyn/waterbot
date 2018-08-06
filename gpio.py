import os

def __run_or_die(cmd):
    if 0 != os.system(cmd):
        raise Exception("Failed to run {}".format(cmd))

gpio_cmd = os.getenv("GPIO_COMMAND", "gpio")

def mode_out(pin):
    cmd = "{} mode {} out".format(gpio_cmd, pin)
    __run_or_die(cmd)

def mode_in(pin):
    cmd = "{} mode {} in".format(gpio_cmd, pin)
    __run_or_die(cmd)

def on(pin):
    cmd = "{} write {} 0".format(gpio_cmd, pin)
    __run_or_die(cmd)

def off(pin):
    cmd = "{} write {} 1".format(gpio_cmd, pin)
    __run_or_die(cmd)
