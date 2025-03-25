from flask import Flask, jsonify, request
from flask_cors import *
from anomaly_detection_income import fetch_income_anomaly, check_new_income_anomaly
app = Flask(__name__)

CORS(app)
@app.route("/income/anomaly", methods=['GET'])
def home():
    return jsonify(fetch_income_anomaly())

@app.route("/income/new/anomaly", methods=['POST'])
def anomaly():
    data = request.json
    new_income = data.get('new_income')
    return jsonify(check_new_income_anomaly(new_income))


if __name__ == '__main__':
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run()