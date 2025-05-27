from flask import Flask, jsonify, request, render_template, url_for
from flask_cors import CORS
from database import *
from ml.anomaly_detector import detect_anomalies_in_df, MODEL_LOADED_SUCCESSFULLY
import io
import pandas as pd
import numpy as np

app = Flask(__name__, template_folder='frontend', static_folder="frontend")
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://127.0.0.1:5000", "http://localhost:5000", "http://localhost:5173", "http://127.0.0.1:5173"],
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

@app.route("/registration")
def registration_page():
    css_url = url_for("static", filename="regstyle.css") 
    return render_template("registration.html",
                           css_url=css_url)


@app.route('/api/auth/login', methods=["POST"])
def authorization_proccess():
    data = request.json
    email = data.get("email") # Получаем email из запроса
    password = data.get("password")

    if not email or not password:
        return jsonify({'status': "Missing email or password"}), 400

    user = get_user(email=email) # Поиск пользователя по email

    if user is None or user.password != password: # Сравнение пароля
        status = "Incorrect password or login"
    else:
        status = "Correct"
    return jsonify({'status': status})


@app.route('/api/auth/register', methods=['POST'])
def register_user_proccess():
    data = request.json
    # username_from_form = data.get('username') # Если ты собираешь display_name
    email = data.get('email')
    password = data.get('password')

    if not email or not password: # Проверка только email и password, если username не для логина
        return jsonify({"message": "Missing email or password"}), 400

    if get_user(email=email): # Проверка по email
        return jsonify({"message": "User with this email already exists"}), 409

    try:
        new_user = add_user(email=email, password=password) # Добавление по email
        # Если есть display_name:
        # new_user = add_user(email=email, password=password, display_name=username_from_form)
        return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201
        
    except Exception as e:
        app.logger.error(f"Error during registration: {e}")
        return jsonify({"message": "An error occurred during registration"}), 500


@app.route("/analiswindow")
def analis_window_page():
    return render_template("analiswindow.html")


@app.route('/api/anomalies', methods=["POST"])
def find_anomalies_route():
    if not MODEL_LOADED_SUCCESSFULLY:
        return jsonify({"error": "ML Model or dependencies not loaded. Check server logs."}), 500

    if not request.is_json or "csvDATA" not in request.json:
        return jsonify({"error": "Missing 'csvDATA' in JSON payload"}), 400
    
    data_str = request.json["csvDATA"]
    csv_file = io.StringIO(data_str)
    
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        app.logger.error(f"Error parsing CSV: {e}")
        return jsonify({"error": f"Error parsing CSV data: {str(e)}"}), 400

    if 'timestamp' not in df.columns or 'value' not in df.columns:
        return jsonify({"error": "CSV must contain 'timestamp' and 'value' columns"}), 400

    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df['value'] = df['value'].astype(float)
    except Exception as e:
        app.logger.error(f"Error processing columns: {e}")
        return jsonify({"error": f"Error processing timestamp or value columns: {str(e)}"}), 400
    
    if df.empty:
        return jsonify({"error": "CSV data resulted in an empty DataFrame after parsing."}), 400
        

    try:
        results_df = detect_anomalies_in_df(df)
    except ValueError as ve:
        app.logger.error(f"ValueError in detect_anomalies: {ve}")
        return jsonify({"error": str(ve)}), 400
    except RuntimeError as re:
        app.logger.error(f"RuntimeError in detect_anomalies: {re}")
        return jsonify({"error": str(re)}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in detect_anomalies: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred during anomaly detection."}), 500

    if results_df.empty:
         return jsonify({
             "anomalies_detected": [], 
             "all_points_processed": [], 
             "summary": {
                "total_points_evaluated": 0,
                "total_anomalies": 0,
                "anomalies_by_mse": 0,
                "anomalies_by_low_activity": 0
             },
             "message": "No data points were processed for anomalies (e.g. not enough data for sequences)."
        })

    results_df['timestamp'] = results_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    anomalies_detected = results_df[results_df['is_anomaly']].to_dict(orient='records')
    all_points_processed = results_df.to_dict(orient='records')

    return jsonify({
        "anomalies_detected": anomalies_detected,
        "all_points_processed": all_points_processed,
        "summary": {
            "total_points_evaluated": len(results_df),
            "total_anomalies": int(np.sum(results_df['is_anomaly'])),
            "anomalies_by_mse": int(np.sum(results_df['is_anomaly_mse'])),
            "anomalies_by_low_activity": int(np.sum(results_df['is_anomaly_low']))
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
