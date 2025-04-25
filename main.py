from flask import Flask, jsonify, request, render_template, url_for
from flask_cors import CORS
from database import *

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
    print(css_url)
    return render_template("index.html",
                           css_url=css_url)

@app.route("/autorith")
def authorization():
    css_url = url_for("static", filename="authstyle.css")
    print(css_url)
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


if __name__ == '__main__':
    app.run(debug=True)
