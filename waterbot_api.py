import json
import db
from flask import Flask, render_template, jsonify, g

app = Flask(__name__)

with open('.config.json') as f:
    app.config['WATERBOT'] = json.load(f)

def get_db():
    database = getattr(g, '_database', None)
    if database is None:
        database = g._database = db.get_db('waterbot.db')
    return database

@app.teardown_appcontext
def teardown_db(exception):
    database = getattr(g, '_database', None)
    if database is not None:
        database.close()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/api/v0/config', methods=["GET","POST"])
def config_v0():
    return jsonify(app.config['WATERBOT'])

@app.route('/api/v0/zones', methods=["GET","POST"])
def zones_v0():
    return jsonify(app.config['WATERBOT']['zones'])

@app.route('/api/v0/zone/<int:zone_id>', methods=["GET","POST"])
def zone(zone_id):
    if str(zone_id) not in app.config['WATERBOT']['zones']:
        return jsonify({"error":f"Zone {zone} not known"}), 404
    return jsonify(app.config['WATERBOT']['zones'][str(zone_id)])

@app.route('/api/v0/tasks', methods=["GET","POST"])
def tasks_v0():
    conn = get_db()
    return jsonify(db.tasks(conn))

@app.route('/api/v0/task/<int:task_id>', methods=["GET","POST"])
def task_v0(task_id):
    conn = get_db()
    result = db.task(conn, task_id)
    if 1 == len(result):
        return jsonify(result[0])
    return jsonify({"error":f"Task {task_id} not found"}), 404

@app.route('/api/v0/cancel-task/<int:task_id>', methods=["POST"])
def cancel_task_v0(task_id):
    conn = get_db()
    rowcount = db.task_terminate(conn, task_id)
    if 1 == rowcount:
        return task_v0(task_id)
    return jsonify({"error":f"Task {task_id} not changed"}), 409

@app.route('/api/v0/water-zone/<int:zone_id>/<int:seconds>', methods=["POST"])
def water_zone_v0(zone_id, seconds):
    if str(zone_id) not in app.config['WATERBOT']['zones']:
        return jsonify({"error":f"Zone {zone_id} not known"}), 404
    if seconds < 1:
        return jsonify({"error":f"{seconds} seconds is less than one second"}), 400
    if seconds > 3600:
        return jsonify({"error":f"{seconds} seconds is longer than one hour"}), 400
    conn = get_db()
    rowcount, task_id = db.water_zone(conn, zone_id, seconds)
    if 1 == rowcount:
        return task_v0(task_id)
    return jsonify({"error":f"Failed to create task for {zone_id}"})
