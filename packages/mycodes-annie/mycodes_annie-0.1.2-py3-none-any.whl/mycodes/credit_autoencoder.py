
##anaomly_detection credit card

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, precision_score, recall_score

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# --- b) LOAD DATA (local CSV) ---
FILE_PATH = "/home/anuja/I2K221191/pgs/creditcard.csv"  # <-- change if needed
df = pd.read_csv(FILE_PATH)

# X: all features except ['Time','Class']; y: 'Class' (0=normal, 1=fraud)
X = df.drop(['Time', 'Class'], axis=1).values.astype("float32")
y = df['Class'].values.astype("float32")

# --- c) SCALE FEATURES ---
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X).astype("float32")
INPUT_DIM = X_scaled.shape[1]    # expected 29 (V1..V28 + Amount)

print("Loaded shapes")
print("  X_scaled:", X_scaled.shape, " y:", y.shape)
print("  Input dimension:", INPUT_DIM)

# --- d) ISOLATE NORMAL TRANSACTIONS & SPLIT (train/val for AE) ---
X_normal = X_scaled[y == 0.0]    # train AE only on non-fraud
X_train_normal, X_val_normal = train_test_split(
    X_normal, test_size=0.2, random_state=42
)

print(f"Training Autoencoder on {X_train_normal.shape[0]} normal transactions")
print(f"Validation (normal): {X_val_normal.shape[0]} transactions")

# --- e) DEFINE AUTOENCODER (Sequential; your style) ---
LATENT_DIM = 14          # ~ INPUT_DIM/2
INTERMEDIATE_DIM = 24

model = keras.Sequential([
    layers.Input(shape=(INPUT_DIM,), name="Input_Layer"),
    layers.Dense(INTERMEDIATE_DIM, activation="relu", name="Encoder_L1"),
    layers.Dense(LATENT_DIM, activation="relu", name="Latent_Representation"),
    layers.Dense(INTERMEDIATE_DIM, activation="relu", name="Decoder_L1"),
    layers.Dense(INPUT_DIM, activation="linear", name="Output_Reconstruction"),  # linear for z-scored features
])

model.summary()

# --- f) COMPILE & TRAIN ---
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss="mse",                      # reconstruction loss
    metrics=["accuracy"]             # kept for parity; not meaningful for AE
)

EPOCHS = 20
BATCH_SIZE = 128

print("\nStarting Autoencoder training...")
history = model.fit(
    X_train_normal, X_train_normal,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    validation_data=(X_val_normal, X_val_normal),
    shuffle=True,
    verbose=1
)
print("Autoencoder training complete.")

# --- g) RECONSTRUCT ALL SAMPLES & COMPUTE MSE ERROR ---
reconstructions = model.predict(X_scaled, verbose=0)
mse = np.mean(np.square(X_scaled - reconstructions), axis=1)

# --- h) CHOOSE THRESHOLD FROM **ALL NORMAL** ERRORS (friend's functionality) ---
normal_error = mse[y == 0.0]
THRESHOLD = np.percentile(normal_error, 95)   # friend's rule
print(f"\nCalculated Anomaly Threshold (95th pct of normal): {THRESHOLD:.6f}")

# --- i) CLASSIFY ANOMALIES (fraud=1) ---
is_anomaly = mse > THRESHOLD
y_pred = np.where(is_anomaly, 1.0, 0.0)  # anomaly→1.0 (fraud), normal→0.0

# --- j) REPORT METRICS (minority class = 1.0, i.e., fraud) ---
print("\nConfusion Matrix")
print(confusion_matrix(y, y_pred))

precision = precision_score(y, y_pred, pos_label=1.0)
recall    = recall_score(y, y_pred, pos_label=1.0)
print(f"Precision (fraud=1): {precision*100:.2f}%")
print(f"Recall    (fraud=1): {recall*100:.2f}%")

# --- k) PLOTS: TRAINING LOSS & ERROR HISTOGRAM ---
plt.figure()
plt.plot(history.history["loss"], label="train_loss")
plt.plot(history.history["val_loss"], label="val_loss")
plt.xlabel("Epoch"); plt.ylabel("MSE Loss"); plt.title("Autoencoder — Training Loss (Credit Card)")
plt.legend(); plt.grid(True); plt.show()

plt.figure()
plt.hist(normal_error, bins=50, alpha=0.6, label="Normal errors")
plt.hist(mse[y == 1.0], bins=50, alpha=0.6, label="Fraud errors")
plt.axvline(THRESHOLD, color="r", linestyle="--", label=f"Threshold={THRESHOLD:.4f}")
plt.xlabel("Reconstruction Error (MSE)")
plt.ylabel("Count")
plt.title("Reconstruction Error Distribution (Credit Card)")
plt.legend(); plt.grid(True); plt.show()

