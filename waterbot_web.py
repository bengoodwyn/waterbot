import json
from waterbot_api import *
from flask import Flask, render_template, jsonify, redirect, g

app = Flask(__name__)

def get_api():
    api = getattr(g, '_api', None)
    if api is None:
        config_filename = 'test_config.json' if app.config['TESTING'] else 'config.json'
        database_filename = ':memory:' if app.config['TESTING'] else 'waterbot.db'
        api = g._api = WaterbotApi(config_filename=config_filename, database_filename=database_filename)
    return api

@app.teardown_appcontext
def teardown_api(exception):
    api = None

@app.route('/', methods=['GET'])
def default():
    return redirect("/ui/index.html", code=302)

@app.route('/ui/<document>', methods=['GET'])
def ui(document):
    return render_template(document)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/api/v0/config', methods=["GET","POST"])
def config_v0():
    return jsonify(get_api().config)

@app.route('/api/v0/zones', methods=["GET","POST"])
def zones_v0():
    return jsonify(get_api().zones())

@app.route('/api/v0/zone/<int:zone_id>', methods=["GET","POST"])
def zone(zone_id):
    try:
        zone = get_api().zone(zone_id)
        return jsonify(zone)
    except ZoneNotFound as e:
        return jsonify({"error":str(e)}), 404

@app.route('/api/v0/tasks', methods=["GET","POST"])
def tasks_v0():
    return jsonify(get_api().tasks())

@app.route('/api/v0/task/<int:task_id>', methods=["GET","POST"])
def task_v0(task_id):
    try:
        task = get_api().task(task_id)
        return jsonify(task)
    except TaskNotFound as e:
        return jsonify({"error":str(e)}), 404

@app.route('/api/v0/cancel-task/<int:task_id>', methods=["POST"])
def cancel_task_v0(task_id):
    try:
        get_api().terminate_task(task_id)
        return jsonify(get_api().task(task_id))
    except TaskNotFound as e:
        return jsonify({"error":str(e)}), 404
    except TaskAlreadyTerminated as e:
        return jsonify({"error":str(e)}), 409

@app.route('/api/v0/water-zone/<int:zone_id>/<int:seconds>', methods=["POST"])
def water_zone_v0(zone_id, seconds):
    try:
        task = get_api().water_zone(zone_id, seconds)
        return jsonify(task), 201
    except ZoneNotFound as e:
        return jsonify({"error":str(e)}), 404
    except TooLong as e:
        return jsonify({"error":str(e)}), 400
    except TooShort as e:
        return jsonify({"error":str(e)}), 400
    except TaskNotCreated as e:
        return jsonify({"error":str(e)}), 500
