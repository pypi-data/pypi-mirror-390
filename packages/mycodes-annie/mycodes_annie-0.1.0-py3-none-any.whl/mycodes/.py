# =============================================================
# 🧠 VGG16 Transfer Learning — Simplified Practical Version
# Steps: Load → Freeze → Add Head → Train → Evaluate → Predict
# =============================================================

# --- a) IMPORTS ---
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.applications import VGG16
import matplotlib.pyplot as plt
import numpy as np

# --- b) LOAD PRETRAINED BASE MODEL ---
base = VGG16(
    weights="/home/anuja/I2K221191/pgs/vgg16_weights.h5",   # ✅ correct local weight file
    include_top=False,
    input_shape=(224, 224, 3)
)

# Freeze base layers (so only classifier trains)
for layer in base.layers:
    layer.trainable = False

# --- c) LOAD DATASET ---
DATA_PATH = "/home/anuja/I2K221191/pgs/caltech-101-img/caltech-101-img"
classes = ['airplanes', 'ant']

gen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

train_data = gen.flow_from_directory(
    DATA_PATH,
    target_size=(224, 224),
    batch_size=32,
    subset='training',
    classes=classes
)

val_data = gen.flow_from_directory(
    DATA_PATH,
    target_size=(224, 224),
    batch_size=32,
    subset='validation',
    classes=classes
)

# --- d) BUILD MODEL ---
model = Sequential([
    base,
    Flatten(),
    Dense(256, activation='relu'),
    Dropout(0.3),
    Dense(train_data.num_classes, activation='softmax')
])

# --- e) COMPILE & TRAIN ---
model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(train_data, validation_data=val_data, epochs=5)

# --- f) EVALUATE ---
loss, acc = model.evaluate(val_data)
print(f"\n✅ Validation Accuracy: {acc*100:.2f}% | Loss: {loss:.4f}")

# --- g) PREDICT & SHOW RESULTS ---
images, labels = next(val_data)
preds = np.argmax(model.predict(images), axis=1)
true = np.argmax(labels, axis=1)

plt.figure(figsize=(10, 8))
for i in range(9):
    plt.subplot(3, 3, i+1)
    plt.imshow(images[i])
    plt.title(f"T:{classes[true[i]]}\nP:{classes[preds[i]]}")
    plt.axis('off')
plt.tight_layout()
plt.show()

# --- h) PRINT BATCH ACCURACY ---
correct = np.sum(preds == true)
print(f"\nBatch Accuracy: {correct}/{len(images)} = {correct/len(images)*100:.2f}%")
