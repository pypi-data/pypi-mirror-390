# Auto-generated from notebook: Assignment_No_2_(1).ipynb
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import random
import numpy as np
from keras import layers, models

from google.colab import drive
drive.mount('/content/drive')

with np.load('/content/drive/MyDrive/Files_OA/mnist.npz', allow_pickle=True) as f:
    x_train, y_train = f['x_train'], f['y_train']
    x_test, y_test = f['x_test'], f['y_test']

print(f"The length of the dataset is : {len(x_train)}")

print(f"The shape of the training dataset is {x_train.shape}")

print(f"The shape of the testing dataset is {x_test.shape}")

import matplotlib.pyplot as plt
import numpy as np

# Find one index for each digit (0-9) in the training data
digit_indices = [np.where(y_train == i)[0][0] for i in range(10)]

# Display one image for each digit
plt.figure(figsize=(10, 5))
for i, idx in enumerate(digit_indices):
    plt.subplot(2, 5, i + 1)
    plt.matshow(x_train[idx], cmap='gray', fignum=0)
    plt.title(f"Digit: {y_train[idx]}")
    plt.axis('off')

plt.tight_layout()
plt.show()

max_pixel_value = x_train.max()
x_train = x_train.astype("float32") / max_pixel_value
x_test = x_test.astype("float32") / max_pixel_value

model = models.Sequential([
    layers.Input(shape=(28, 28)),
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dense(128, activation='tanh'),
    layers.Dense(64, activation='relu'),
    layers.Dense(10, activation='softmax')
])

# Display the model architecture, showing each layer, output shape, and number of parameters
model.summary()

model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=0.01),loss='sparse_categorical_crossentropy',metrics=['accuracy'])

early_stop = keras.callbacks.EarlyStopping(monitor="val_loss",patience=3,restore_best_weights=True)
history = model.fit(
    x_train, y_train,
    epochs=50,
    validation_data=(x_test, y_test),
    callbacks=[early_stop],
    verbose=1
)

n = random.randint(0, len(x_test)-1)
predicted_values = model.predict(x_test[n:n+1], verbose=0)
predicted_class = np.argmax(predicted_values[0])

plt.imshow(x_test[n], cmap='gray')
plt.title(f"Predicted: {predicted_class}, Actual: {y_test[n]}")
plt.show()

# List all recorded metrics from training
list(history.history.keys())

test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print(f"Test Loss = {test_loss:.3f}")
print(f"Test Accuracy = {test_acc*100:.2f}%")

train_loss, train_acc = model.evaluate(x_train, y_train, verbose=0)
print(f"Training Loss = {train_loss:.3f}")
print(f"Training Accuracy = {train_acc*100:.2f}%")

plt.figure(figsize=(8,5))
plt.plot(history.history['accuracy'], marker='o')
plt.plot(history.history['val_accuracy'], marker='s')
plt.title('MODEL ACCURACY OVER EPOCHS', fontsize=14, fontweight='bold')
plt.ylabel('Accuracy', fontsize=12)
plt.xlabel('Epoch', fontsize=12)
plt.legend(['Train', 'Validation'], loc='lower right')
plt.grid(True)
plt.show()

plt.figure(figsize=(8,5))
plt.plot(history.history['loss'], marker='o')
plt.plot(history.history['val_loss'], marker='s')
plt.title('MODEL LOSS OVER EPOCHS', fontsize=14, fontweight='bold')
plt.ylabel('Loss', fontsize=12)
plt.xlabel('Epoch', fontsize=12)
plt.legend(['Train', 'Validation'], loc='upper right')
plt.grid(True)
plt.show()
