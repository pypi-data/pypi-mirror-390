#FNN CIFAR
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

train_path="/home/anuja/I2K221191/pgs/train_data.csv"
test_path="/home/anuja/I2K221191/pgs/test_data.csv"

train_df=pd.read_csv(train_path)
test_df=pd.read_csv(test_path)

x_train=train_df.iloc[:,:-1].values
y_train=train_df.iloc[:,-1].values
x_test=test_df.iloc[:,:-1].values
y_test=test_df.iloc[:,-1].values

print("Loaded shapes")
print("x_train",x_train.shape,"y_train",y_train.shape)

x_train=(x_train/255.0).astype("float32")
x_test=(x_test/255.0).astype("float32")                               

model=keras.Sequential([
 layers.Input(shape=(32*32*3,)),
 layers.Dense(512,activation="relu"),
 layers.Dropout(0.2),
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
    batch_size=128,
    validation_split=0.1,
    verbose=1
)

test_loss,test_acc=model.evaluate(x_test,y_test,verbose=0)
print(f"Accuracy:{test_acc}")

plt.figure()
plt.plot(history.history["loss"],label="loss")

plt.plot(history.history["val_loss"],label="val_loss")
plt.xlabel("Epoch");plt.ylabel("Accuracy")
plt.legend;plt.grid(True);plt.show()


