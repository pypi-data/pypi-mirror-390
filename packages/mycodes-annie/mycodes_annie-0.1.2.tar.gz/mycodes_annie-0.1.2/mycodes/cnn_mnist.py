# =============================================================
# 🧠 MNIST (CSV, offline) → Convolutional Neural Network (Keras)
# Sequential version — mirrors your CIFAR CNN syntax/style
# =============================================================

# --- a) IMPORT PACKAGES ---
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# --- b) LOAD TRAIN/TEST FROM CSV ---
train_path = "/home/anuja/I2K221191/pgs/mnist_train.csv"
test_path  = "/home/anuja/I2K221191/pgs/mnist_test.csv"

print(f"📂 Loading training data from: {train_path}...")
train_df = pd.read_csv(train_path)

print(f"📂 Loading test data from: {test_path}...")
test_df = pd.read_csv(test_path)

# --- c) PREPROCESS DATA ---
# MNIST CSV: first column = label, remaining 784 columns = pixels
x_train = train_df.iloc[:, 1:].values.astype("float32")
y_train = train_df.iloc[:, 0].values
x_test  = test_df.iloc[:, 1:].values.astype("float32")
y_test  = test_df.iloc[:, 0].values

# Reshape flat pixels → 28×28×1 for CNN (grayscale)
x_train = x_train.reshape(x_train.shape[0], 28, 28, 1)
x_test  = x_test.reshape(x_test.shape[0], 28, 28, 1)

# Normalize pixel values (0–255 → 0–1)
x_train /= 255.0
x_test  /= 255.0

# One-hot encode labels (to mirror CIFAR style using categorical crossentropy)
y_train = keras.utils.to_categorical(y_train, num_classes=10)
y_test  = keras.utils.to_categorical(y_test, num_classes=10)

print("✅ Data loaded and preprocessed successfully")
print("x_train:", x_train.shape, "y_train:", y_train.shape)
print("x_test :", x_test.shape,  "y_test :", y_test.shape)

# --- d) DEFINE CNN MODEL ---
model = keras.Sequential([
    # Convolutional Block 1
    layers.Conv2D(32, (3, 3), activation="relu", input_shape=(28, 28, 1), name="Conv_1"),
    layers.MaxPooling2D((2, 2), name="Pool_1"),

    # Convolutional Block 2
    layers.Conv2D(64, (3, 3), activation="relu", name="Conv_2"),
    layers.MaxPooling2D((2, 2), name="Pool_2"),

    # Classification Head
    layers.Flatten(name="Flatten_Layer"),
    layers.Dense(100, activation="relu", name="Dense_1"),
    layers.Dense(10, activation="softmax", name="Output_Layer"),
])

model.summary()

# --- e) COMPILE & TRAIN ---
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

history = model.fit(
    x_train, y_train,
    epochs=11,
    batch_size=128,
    validation_split=0.1,
    verbose=1
)

# --- f) VISUALIZE ONE TEST IMAGE ---
plt.imshow(x_test[2].squeeze(), cmap="gray")
true_label = int(np.argmax(y_test[2]))
plt.title(f"Label: {true_label}")
plt.axis("off")
plt.show()

# --- g) EVALUATE ON TEST DATA ---
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print(f"\nTest Accuracy: {test_acc:.4f} | Test Loss: {test_loss:.4f}")

# --- h) PREDICT RANDOM SAMPLE ---
import random
n = random.randint(0, len(x_test) - 1)

plt.imshow(x_test[n].squeeze(), cmap="gray")
plt.title(f"Actual Label: {int(np.argmax(y_test[n]))}")
plt.axis("off")
plt.show()

probs = model.predict(x_test, verbose=0)
pred_class = int(np.argmax(probs[n]))
print("Predicted class:", pred_class)

# --- i) PLOT TRAINING CURVES ---
plt.figure()
plt.plot(history.history["loss"], label="train_loss")
plt.plot(history.history["val_loss"], label="val_loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("MNIST CNN (CSV) — Loss")
plt.legend()
plt.grid(True)
plt.show()

plt.figure()
plt.plot(history.history["accuracy"], label="train_acc")
plt.plot(history.history["val_accuracy"], label="val_acc")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.title("MNIST CNN (CSV) — Accuracy")
plt.legend()
plt.grid(True)
plt.show()
