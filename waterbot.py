import logging
import time
import json
import gpio
import os
import time
import atexit
import waterbot_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("waterbot")

def reset_gpio(api):
    logger.info("Resetting all configured GPIO pins")
    common = api.config["common_gpio"]
    gpio.mode_out(common)
    gpio.off(common)

    for pin in api.zones():
        gpio.mode_out(pin)
        gpio.off(pin)

def start_watering(api, task):
    logger.info("Begin watering {}".format(str(task)))

    common = api.config["common_gpio"]
    zone_id = task["zone_id"]
    task_id = task["task_id"]

    api.start_task(task_id)

    gpio.on(common)
    gpio.on(zone_id)

    return task_id

def stop_watering(api, task):
    logger.info("End watering {}".format(str(task)))

    common = api.config["common_gpio"]
    zone_id = task["zone_id"]
    task_id = task["task_id"]

    gpio.off(common)
    gpio.off(zone_id)

    try:
        api.terminate_task(task_id)
    except waterbot_api.TaskAlreadyTerminated:
        pass

def has_watered_long_enough(task):
    return time.time() >= task["ts_started"] + task["seconds"]

def was_watering_canceled(task):
    return task["ts_terminated"] != None

def continue_task(api, task_id):
    task = api.task(task_id)
    if was_watering_canceled(task) or has_watered_long_enough(task):
        stop_watering(api, task)
        return None
    else:
        return task_id

def start_new_task(api):
    pending_tasks = api.pending_tasks()
    if len(pending_tasks) > 0:
        return start_watering(api, pending_tasks[0])
    else:
        return None

def poll_waterbot(api, task_id):
    if task_id:
        task_id = continue_task(api, task_id)
    if not task_id:
        task_id = start_new_task(api)
    return task_id

def main():
    api = waterbot_api.WaterbotApi()
    logger.info("Starting with config {}".format(str(api.config)))
 
    atexit.register(reset_gpio, api)
    reset_gpio(api)

    active_task_id = None
    while True:
        active_task_id = poll_waterbot(api, active_task_id)
        time.sleep(1)

if __name__ == "__main__":
    main()
