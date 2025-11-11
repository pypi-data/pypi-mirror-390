#FNN mnist:
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras 
from tensorflow.keras import layers

train_path = "/home/anuja/I2K221191/pgs/mnist_train.csv"
test_path  = "/home/anuja/I2K221191/pgs/mnist_test.csv"

train_df=pd.read_csv(train_path)
test_df=pd.read_csv(test_path)

x_train=train_df.iloc[:,1:].values
y_train=train_df.iloc[:,0].values
x_test=test_df.iloc[:,1:].values
y_test=test_df.iloc[:,0].values

print("Loaded shapes")
print("x train",x_train.shape,"y_train",y_train.shape)
print("x_test",x_test.shape,"y_test:",y_test.shape)

x_train=(x_train/255.0).astype("float32")
x_test=(x_test/255.0).astype("float32")

model=keras.Sequential([
    layers.Input(shape=(784,)),
    layers.Dense(256,activation="relu"),
    layers.Dropout(0.2),
    layers.Dense(10,activation="softmax")
])
model.summary()

model.compile(
optimizer=keras.optimizers.SGD(learning_rate=0.01,momentum=0.9),
loss="sparse_categorical_crossentropy",
metrics=["accuracy"]
)


history=model.fit(
x_train,y_train,
epochs=11,
batch_size=64,
validation_split=0.1,
verbose=2
)

plt.imshow(x_test[2].reshape(28,28),cmap="grey")
plt.title(f"Label:{y_train[2]}")
plt.axis("off")
plt.show()

test_loss,test_acc=model.evaluate(x_test,y_test,verbose=0)
print(f"\nTest accuracy: Test accuracy{test_acc}")

import random
n=random.randint(0,len(x_test)-1)
plt.imshow(x_test[n].reshape(28,28),cmap="grey")
plt.title(f"Actual Label:{y_test[n]}")
plt.axis("off")
plt.show()
probs=model.predict(x_test,verbose=0)
pred_digits=int(np.argmax(probs[n]))
print("predicted_digits",pred_digits)
plt.figure()
plt.plot(history.history["loss"], label="train_loss")
plt.plot(history.history["val_loss"], label="val_loss")
plt.xlabel("Epoch"); plt.ylabel("Loss"); plt.title("MNIST FFNN (CSV) — Loss")
plt.legend(); plt.grid(True); plt.show()

plt.figure()
plt.plot(history.history["accuracy"], label="train_acc")
plt.plot(history.history["val_accuracy"], label="val_acc")
plt.xlabel("Epoch"); plt.ylabel("Accuracy"); plt.title("MNIST FFNN (CSV) — Accuracy")
plt.legend(); plt.grid(True); plt.show()
