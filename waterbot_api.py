import json
import waterbot_db
import os.path

class ZoneNotFound(Exception):
    def __init__(self, zone_id):
        super().__init__("Zone '{}' not found".format(zone_id))
        self.zone_id = zone_id

class TooShort(Exception):
    def __init__(self, value, minimum_value):
        super().__init__("'{}' is less than the minimum value of '{}'".format(value, minimum_value))
        self.value = value
        self.minimum_value = minimum_value

class TooLong(Exception):
    def __init__(self, value, maximum_value):
        super().__init__("'{}' is more than the maximum value of '{}'".format(value, maximum_value))
        self.value = value
        self.maximum_value = maximum_value

class TaskNotFound(Exception):
    def __init__(self, task_id):
        super().__init__("Task '{}' was not found".format(task_id))
        self.task_id = task_id

class TaskAlreadyTerminated(Exception):
    def __init__(self, task_id):
        super().__init__("Task '{}' was already terminated".format(task_id))
        self.task_id = task_id

class TaskAlreadyStarted(Exception):
    def __init__(self, task_id):
        super().__init__("Task '{}' was already started".format(task_id))
        self.task_id = task_id

class TaskNotCreated(Exception):
    def __init__(self, zone_id, seconds):
        super().__init__("Failed to create task to water zone '{}' for '{}' seconds".format(zone_id, seconds))
        self.zone_id = zone_id
        self.seconds = seconds

class WaterbotApi:
    def __init__(self, config_filename='config.json' if os.path.isfile('config.json') else 'test_config.json', database_filename='waterbot.db'):
        with open(config_filename) as f:
            self.config = json.load(f)
        self.conn = waterbot_db.get_db(database_filename)

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
        return waterbot_db.tasks(self.conn)

    def pending_tasks(self):
        return waterbot_db.tasks_pending(self.conn)

    def active_tasks(self):
        return waterbot_db.tasks_active(self.conn)

    def task(self, task_id):
        tasks = waterbot_db.task(self.conn, task_id)
        if len(tasks) != 1:
            raise TaskNotFound(task_id)
        return tasks[0]

    def terminate_task(self, task_id):
        self.task(task_id)
        if 1 != waterbot_db.task_terminate(self.conn, task_id):
            raise TaskAlreadyTerminated(task_id)
        return self.task(task_id)

    def start_task(self, task_id):
        self.task(task_id)
        if 1 != waterbot_db.task_start(self.conn, task_id):
            raise TaskAlreadyStarted(task_id)
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
        rowsaffected, task_id = waterbot_db.water_zone(self.conn, zone_id, seconds)
        if 1 != rowsaffected:
            raise TaskNotCreated(zone_id, seconds)
        return self.task(task_id)
