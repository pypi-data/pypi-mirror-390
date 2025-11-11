# GRU model using California Housing dataset (Colab-ready)
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense

def gru():
    data = fetch_california_housing(as_frame=True)
    df = data.frame

    series = df['MedHouseVal'].values.astype('float32').reshape(-1, 1)

    scaler = MinMaxScaler()
    series_s = scaler.fit_transform(series)

    seq_len = 10
    X, y = [], []
    for i in range(len(series_s) - seq_len):
        X.append(series_s[i:i + seq_len])
        y.append(series_s[i + seq_len])
    X = np.array(X)
    y = np.array(y)

    train_size = int(0.8 * len(X))
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    model = Sequential([
        GRU(32, input_shape=(seq_len, 1)),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')

    # --- train ---

    # --- predict + inverse scale ---
    pred_s = model.predict(X_test)
    pred = scaler.inverse_transform(pred_s)
    y_true = scaler.inverse_transform(y_test)

    # --- show sample predictions ---
    for i in range(min(10, len(pred))):
        print(f"Predicted: {pred[i,0]:.4f} | Actual: {y_true[i,0]:.4f}")
