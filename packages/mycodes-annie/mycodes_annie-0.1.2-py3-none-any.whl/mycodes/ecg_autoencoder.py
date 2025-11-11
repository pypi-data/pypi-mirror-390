#Anamoly Detection ecg
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix,precision_score,recall_score
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow import keras

file_path = "/home/anuja/I2K221191/pgs/ecg_autoencoder_dataset.csv"   # <-- change if needed
df=pd.read_csv(file_path)

x=df.iloc[:,:-1].values.astype("float32")
y=df.iloc[:,-1].values.astype("float32")

scaler=StandardScaler()
x_scaled=scaler.fit_transform(x).astype("float32")

input_dim=x_scaled.shape[1]
x_normal=x_scaled[y==1.00]
x_train_normal,x_test_normal=train_test_split(
    x_normal,test_size=0.2,random_state=42
)

#now we have x_normal so create the model
intermediate_dim=120
latent_dim=70
model=keras.Sequential(
    [
    layers.Input(shape=(input_dim,),name="First_layer"),
    layers.Dense(intermediate_dim,activation="relu",name="Encode_L1"),
    layers.Dense(latent_dim,activation="relu",name="Latent_layer"),
    layers.Dense(intermediate_dim,activation="relu",name="Decode_L1"),
    layers.Dense(input_dim,activation="linear",name="output"),
    ]
    
)
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss="mse",
    metrics=["accuracy"]
)

history=model.fit(
    x_train_normal,x_train_normal,
    epochs=20,
    batch_size=128,
    validation_data=(x_test_normal,x_test_normal),
    shuffle=True,
    verbose=2
)


reconstruct=model.predict(x_scaled,verbose=0)
mse=np.mean(np.square(x_scaled-reconstruct),axis=1)
normal_errors=mse[y==1.0]
threshold=np.percentile(normal_errors,95)
is_anamoly=mse>threshold
y_pred=np.where(is_anamoly,0.0,1.0)

precision=precision_score(y,y_pred)
recall=recall_score(y,y_pred)

print(precision)
print(recall)

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
