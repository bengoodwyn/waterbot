from flask import Flask, render_template
import json

app = Flask(__name__)

with open('.config.json') as f:
    app.config['WATERBOT'] = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')
