from flask import Flask, jsonify, request
from flask_cors import *
from anomaly_detection_income import income_data_fetch, check_new_income_anomaly
from mistral_analysis import analysis
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)
@app.route("/income/anomaly", methods=['GET'])
def home():
    return jsonify(income_data_fetch())

@app.route("/income/new/anomaly", methods=['POST'])
def anomaly():
    data = request.json
    new_income = data.get('new_income')
    return check_new_income_anomaly(new_income)

@app.route("/analysis", methods=['POST'])
@cross_origin(origins="http://localhost:4200")  # Allow frontend requests
def run_analysis():
    return jsonify(analysis())

# ✅ Handle preflight OPTIONS request for /analysis
@app.route("/analysis", methods=['OPTIONS'])
def handle_options():
    response = jsonify({"message": "CORS Preflight OK"})
    response.status_code = 200
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:4200")
    response.headers.add("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

if __name__ == '__main__':
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run()