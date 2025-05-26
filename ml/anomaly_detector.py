# ml_model/anomaly_detector.py
import pandas as pd
import numpy as np
import torch
import joblib
import json
import os
from .model_definition import LSTMModel

# Пути к файлам модели и конфигурации внутри пакета ml_model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_SAVE_PATH = os.path.join(BASE_DIR, 'lstm_anomaly_detection_model.pth')
SCALER_PATH = os.path.join(BASE_DIR, 'min_max_scaler.joblib')
CONFIG_PATH = os.path.join(BASE_DIR, 'model_config.json')

device = None
model = None
scaler_global = None
config_global = None

def load_model_and_dependencies():
    global device, model, scaler_global, config_global

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"ML Model: Using device: {device}")

    try:
        with open(CONFIG_PATH, 'r') as f:
            config_global = json.load(f)
        
        scaler_global = joblib.load(SCALER_PATH)

        model_instance = LSTMModel(
            input_size=1, 
            hidden_layer_size=100, 
            output_size=1,       
            num_layers=2, 
            dropout_prob=0.2
        )
        model_instance.load_state_dict(torch.load(MODEL_SAVE_PATH, map_location=device))
        model_instance.to(device)
        model_instance.eval()
        model = model_instance
        print("ML Model, scaler, and config loaded successfully.")
        return True
    except FileNotFoundError as e:
        print(f"Error loading ML files: {e}. Make sure model, scaler, and config files are in '{BASE_DIR}'.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during ML loading: {e}")
        return False


MODEL_LOADED_SUCCESSFULLY = load_model_and_dependencies()


def detect_anomalies_in_df(input_df: pd.DataFrame):
    """
    Обнаружение аномалий в DataFrame с помощью загруженной модели.
    DataFrame должен иметь DatetimeIndex и столбец 'value'.
    """
    if not MODEL_LOADED_SUCCESSFULLY or model is None or scaler_global is None or config_global is None:
        raise RuntimeError("Модель или ее зависимости не были успешно загружены.")

    if 'value' not in input_df.columns:
        raise ValueError("DataFrame должен содержать столбец 'value'")
    if not isinstance(input_df.index, pd.DatetimeIndex):
        raise ValueError("Индекс DataFrame должен быть DatetimeIndex")
    
    seq_length_val = config_global['seq_length']
    threshold_mse_val = config_global['threshold_mse']
    threshold_low_activity_scaled_val = config_global['low_activity_threshold_scaled']

    if len(input_df) <= seq_length_val:
        print(f"Недостаточно данных для создания последовательности (нужно > {seq_length_val}, получено {len(input_df)}).")
        return pd.DataFrame(columns=['timestamp', 'actual', 'prediction', 'mse', 'is_anomaly_mse', 'is_anomaly_low', 'is_anomaly'])

    scaled_data = scaler_global.transform(input_df[['value']])
    X_data = []
    actual_indices = []
    for i in range(len(scaled_data) - seq_length_val):
        X_data.append(scaled_data[i:i + seq_length_val])
        actual_indices.append(i + seq_length_val)
    
    if not X_data:
        print(f"Не удалось создать последовательности.")
        return pd.DataFrame(columns=['timestamp', 'actual', 'prediction', 'mse', 'is_anomaly_mse', 'is_anomaly_low', 'is_anomaly'])

    X_data_np = np.array(X_data)
    X_tensor = torch.FloatTensor(X_data_np).to(device)
    X_tensor = X_tensor.view(X_tensor.shape[0], seq_length_val, 1)

    model.eval()
    with torch.no_grad():
        predictions_scaled = model(X_tensor).cpu().numpy()

    actuals_scaled = scaled_data[actual_indices].reshape(-1, 1)
    mse_per_point = (predictions_scaled - actuals_scaled) ** 2
    anomalies_mse = mse_per_point > threshold_mse_val
    anomalies_low_activity = (actuals_scaled < threshold_low_activity_scaled_val) & (predictions_scaled > threshold_low_activity_scaled_val)
    is_anomaly = anomalies_mse.flatten() | anomalies_low_activity.flatten()

    predictions_rescaled = scaler_global.inverse_transform(predictions_scaled).flatten()
    actuals_rescaled = scaler_global.inverse_transform(actuals_scaled).flatten()
    
    result_timestamps = input_df.index[actual_indices]

    results = pd.DataFrame({
        'timestamp': result_timestamps,
        'actual': actuals_rescaled,
        'prediction': predictions_rescaled,
        'mse': mse_per_point.flatten(),
        'is_anomaly_mse': anomalies_mse.flatten(),
        'is_anomaly_low': anomalies_low_activity.flatten(),
        'is_anomaly': is_anomaly
    })
    return results