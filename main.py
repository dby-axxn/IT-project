from flask import Flask, jsonify, request, render_template, url_for
from flask_cors import CORS
from database import *
from pandas import DataFrame

app = Flask(__name__, template_folder='frontend', static_folder="frontend")
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://127.0.0.1:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})


@app.route("/")
def main():
    css_url = url_for("static", filename="style.css")
    return render_template("index.html",
                           css_url=css_url)

@app.route("/autorith")
def authorization():
    css_url = url_for("static", filename="authstyle.css")
    return render_template("autorith.html",
                           css_url=css_url)


@app.route('/api/auth/login', methods=["POST"])
def authorization_proccess():
    data = request.json
    user = get_user(data["email"])

    if user is None or user["password"] != data["password"]:
        status = "Incorrect password or login"
    else:
        status = "Correct"


    return jsonify({'status': status})


@app.route('/api/anomalies', methods=["POST"])
def find_anomailes():
    data : str = request.json["csvDATA"]
    lines = data.split("\n")
    labels = lines[0].split(",")
    values = [[elem.split(",")[i].strip() for elem in lines[1:]] for i in range(len(labels))]

    csvData = {labels[i].strip(): values[i] for i in range(len(labels))}

    csvDF = DataFrame(csvData)

    # TODO
    # подставьте сюда ml-функцию


    # return jsonify({'dataset': dataset, "labels": label})

if __name__ == '__main__':
    app.run(debug=True)
