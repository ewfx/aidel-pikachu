from flask import Flask
from anomaly_detection_income import fetch_income_anomaly
app = Flask(__name__)

@app.route("/income/anomaly")
def home():
    return fetch_income_anomaly()

if __name__ == '__main__':
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run()