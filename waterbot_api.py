import json
import db

class ZoneNotFound(Exception):
    def __init__(self, zone_id):
        super().__init__(f"Zone '{zone_id}' not found")
        self.zone_id = zone_id

class TooShort(Exception):
    def __init__(self, value, minimum_value):
        super().__init__(f"'{value}' is less than the minimum value of '{minimum_value}'")
        self.value = value
        self.minimum_value = minimum_value

class TooLong(Exception):
    def __init__(self, value, maximum_value):
        super().__init__(f"'{value}' is more than the maximum value of '{maximum_value}'")
        self.value = value
        self.maximum_value = maximum_value

class TaskNotFound(Exception):
    def __init__(self, task_id):
        super().__init__(f"Task '{task_id}' was not found")
        self.task_id = task_id

class TaskAlreadyTerminated(Exception):
    def __init__(self, task_id):
        super().__init__(f"Task '{task_id}' was already terminated")
        self.task_id = task_id

class TaskNotCreated(Exception):
    def __init__(self, zone_id, seconds):
        super().__init__(f"Failed to create task to water zone '{zone_id}' for '{seconds}' seconds")
        self.zone_id = zone_id
        self.seconds = seconds

class WaterbotApi:
    def __init__(self, config_filename='.config.json', database_filename='waterbot.db'):
        with open(config_filename) as f:
            self.config = json.load(f)
        self.conn = db.get_db(database_filename)

    def __del__(self):
        if self.conn:
            self.conn.close()

    def zones(self):
        return self.config['zones']

    def zone(self, zone_id):
        all_zones = self.zones()
        if str(zone_id) not in all_zones:
            raise ZoneNotFound(zone_id)
        return all_zones[str(zone_id)]

    def tasks(self):
        return db.tasks(self.conn)

    def task(self, task_id):
        tasks = db.task(self.conn, task_id)
        if len(tasks) != 1:
            raise TaskNotFound(task_id)
        return tasks[0]

    def terminate_task(self, task_id):
        self.task(task_id)
        if 1 != db.task_terminate(self.conn, task_id):
            raise TaskAlreadyTerminated(task_id)
        return self.task(task_id)

    def __validate_watering_time(self, seconds):
        minimum_seconds = 1
        maximum_seconds = 3600
        if seconds < minimum_seconds:
            raise TooShort(seconds, minimum_seconds)
        if seconds > maximum_seconds:
            raise TooLong(seconds, maximum_seconds)

    def water_zone(self, zone_id, seconds):
        self.__validate_watering_time(seconds)
        self.zone(zone_id)
        rowsaffected, task_id = db.water_zone(self.conn, zone_id, seconds)
        if 1 != rowsaffected:
            raise TaskNotCreated(zone_id, seconds)
        return self.task(task_id)
