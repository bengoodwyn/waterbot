import logging
import time
import json
import gpio
import os
import time
import atexit
import waterbot_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("water_worker")

api = waterbot_api.WaterbotApi()
common = api.config["common_gpio"]

def reset():
    logger.info(f"waterbot resetting all GPIO pins")
    gpio.mode_out(common)
    gpio.off(common)

    for pin in api.zones():
        gpio.mode_out(pin)
        gpio.off(pin)

active_task_id = None
logger.info(f"water_worker starting with config {api.config}")
atexit.register(reset)
reset()
while True:
    if active_task_id:
        task = api.task(active_task_id)
        if task["ts_terminated"] != None:
            logger.info(f"Task was terminated: {task}")
            gpio.off(common)
            gpio.off(task["zone_id"])
            active_task_id = None
        elif time.time() >= task["ts_started"] + task["seconds"]:
            logger.info(f"Task ran for long enough: {task}")
            gpio.off(common)
            gpio.off(task["zone_id"])
            api.terminate_task(active_task_id)
            active_task_id = None

    if not active_task_id:
        pending_tasks = api.pending_tasks()
        if len(pending_tasks) > 0:
            task = pending_tasks[0]
            active_task_id = task["task_id"]
            logger.info(f"Starting {task}")
            api.start_task(task["task_id"])
            gpio.on(common)
            gpio.on(task["zone_id"])

    time.sleep(1)
