import logging
import time
import db
import json
import gpio
import os
import time
import atexit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("water_worker")

config = None
with open('.config.json') as f:
    config = json.load(f)
common = config["common_gpio"]

conn = db.get_db('waterbot.db')

def reset():
    logger.info(f"waterbot resetting all GPIO pins")
    gpio.mode_out(common)
    gpio.off(common)

    for pin in config["zones"]:
        gpio.mode_out(pin)
        gpio.off(pin)

active_task_id = None
logger.info(f"water_worker starting with config {config}")
atexit.register(reset)
reset()
while True:
    if active_task_id:
        task = db.task(conn, active_task_id)[0]
        if task["ts_terminated"] != None:
            logger.info(f"Task was terminated: {task}")
            gpio.off(common)
            gpio.off(task["zone_id"])
            active_task_id = None
        elif time.time() >= task["ts_started"] + task["seconds"]:
            logger.info(f"Task ran for long enough: {task}")
            gpio.off(common)
            gpio.off(task["zone_id"])
            db.task_terminate(conn, active_task_id)
            active_task_id = None

    if not active_task_id:
        pending_tasks = db.tasks_pending(conn)
        if len(pending_tasks) > 0:
            task = pending_tasks[0]
            active_task_id = task["task_id"]
            logger.info(f"Starting {task}")
            db.task_start(conn, task["task_id"])
            gpio.on(common)
            gpio.on(task["zone_id"])

    time.sleep(1)
