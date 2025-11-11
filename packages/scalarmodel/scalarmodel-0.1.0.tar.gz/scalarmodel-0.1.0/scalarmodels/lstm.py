# -------------------------------
# LSTM for California Housing Data
# -------------------------------

# Import necessary libraries
import pandas as pd
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# -------------------------------
# 1️⃣ Load the California housing dataset
# -------------------------------
data = fetch_california_housing(as_frame=True)
df = data.frame

# We'll use the median house value (target column)
series = df['MedHouseVal'].astype('float32').values.reshape(-1, 1)

# -------------------------------
# 2️⃣ Normalize the data
# -------------------------------
scaler = MinMaxScaler()
series_s = scaler.fit_transform(series)

# -------------------------------
# 3️⃣ Create input-output sequences
# -------------------------------
seq_len = 10
X, y = [], []
for i in range(len(series_s) - seq_len):
    X.append(series_s[i:i + seq_len])
    y.append(series_s[i + seq_len])

X = np.array(X)
y = np.array(y)

# -------------------------------
# 4️⃣ Split into training and testing sets
# -------------------------------
train_size = int(0.8 * len(X))
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# -------------------------------
# 5️⃣ Build the LSTM model
# -------------------------------
model = Sequential([
    LSTM(32, input_shape=(seq_len, 1)),
    Dense(1)
])

model.compile(optimizer='adam', loss='mse')

model.fit(X_train, y_train, epochs=10, batch_size=16, validation_data=(X_test, y_test))

pred_s = model.predict(X_test)

# Inverse transform predictions
pred = scaler.inverse_transform(pred_s)
y_true = scaler.inverse_transform(y_test)

print("Predicted vs Actual values:\n")
for i in range(min(10, len(pred))):
    print(f"Predicted: {pred[i,0]:.4f} | Actual: {y_true[i,0]:.4f}")
