# Auto-generated from notebook: Assignment_No_3_(3).ipynb
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import datasets, layers, models
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import BatchNormalization, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import random

from google.colab import drive
drive.mount('/content/drive')

with np.load('/content/drive/MyDrive/Files_OA/cifar-10.npz', allow_pickle=True) as f:
    train_images, train_labels = f['x_train'], f['y_train']
    test_images, test_labels = f['x_test'], f['y_test']

# Find the maximum pixel value across train and test images
max_val = max(train_images.max(), test_images.max())

# Normalize images to range 0-1
train_images = train_images.astype('float32') / max_val
test_images  = test_images.astype('float32') / max_val

# One-hot encode labels
y_train_cat = to_categorical(train_labels, num_classes=10)
y_test_cat  = to_categorical(test_labels, num_classes=10)

print(f"Max value used for normalization: {max_val}")

print(f"train_images shape: {train_images.shape}, dtype: {train_images.dtype}")
print(f"train_labels shape: {train_labels.shape}, dtype: {train_labels.dtype}")



# Plot unique images with numerical labels
plt.figure(figsize=(15, 6)) # Increased figure size for better visibility
plt.suptitle("Unique Images with Numerical Labels", fontsize=16, fontweight='bold')

# Find indices of unique labels
unique_labels, unique_indices = np.unique(train_labels, return_index=True)

for i, label_index in enumerate(unique_indices):
    plt.subplot(2, 5, i + 1)  # 2 rows × 5 columns

    # Upscale the image for better clarity (optional, but can help)
    # Using bicubic interpolation for smoother upscaling
    upscaled_image = tf.image.resize(train_images[label_index], (96, 96), method='bicubic').numpy()

    # Clip the image data to the valid range [0, 1]
    clipped_image = np.clip(upscaled_image, 0, 1)

    plt.imshow(clipped_image)

    plt.xticks([])
    plt.yticks([])

    # Display the numerical label
    numerical_label = train_labels[label_index][0] # Access the scalar value
    plt.xlabel(f"{numerical_label}", fontsize=10)
    plt.grid(False)

plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to prevent title overlap
plt.show()


# Plot unique images with class names

class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']
plt.figure(figsize=(15, 6)) # Increased figure size for better visibility
plt.suptitle("Unique Images with Class Names", fontsize=16, fontweight='bold')

for i, label_index in enumerate(unique_indices):
    plt.subplot(2, 5, i + 1)  # 2 rows × 5 columns

    # Upscale the image for better clarity (optional, but can help)
    # Using bicubic interpolation for smoother upscaling
    upscaled_image = tf.image.resize(train_images[label_index], (96, 96), method='bicubic').numpy()

    # Clip the image data to the valid range [0, 1]
    clipped_image = np.clip(upscaled_image, 0, 1)

    plt.imshow(clipped_image)

    plt.xticks([])
    plt.yticks([])

    # Display the class name
    numerical_label = train_labels[label_index][0] # Access the scalar value
    class_name = class_names[numerical_label]
    plt.xlabel(f"{class_name}", fontsize=10)
    plt.grid(False)

plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to prevent title overlap
plt.show()

model = models.Sequential([
    # First convolution block
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
    BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    Dropout(0.25),

    # Second convolution block
    layers.Conv2D(64, (3, 3), activation='relu'),
    BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    Dropout(0.25),

    # Third convolution block
    layers.Conv2D(64, (3, 3), activation='relu'),
    BatchNormalization(),

    # Flatten and dense layers
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(10, activation='softmax')  # Output layer with softmax
])

# Display model summary
model.summary()

# Compile the model
# Define the Adam optimizer with a specified learning rate
adam_optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

model.compile(
    optimizer=adam_optimizer,
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Maximum number of epochs to train
max_epochs = 15

# Stop training early if validation loss doesn't improve for 3 consecutive epochs
early_stop = EarlyStopping(
    monitor='val_loss',
    patience=3,
    restore_best_weights=True
)

# Train the model
history = model.fit(
    train_images, y_train_cat,
    validation_data=(test_images, y_test_cat),
    epochs=max_epochs,      # Training will stop early if no improvement
    callbacks=[early_stop],
    batch_size=64,
    verbose=1
)

train_loss, train_acc = model.evaluate(train_images, y_train_cat)

print(f"Training Loss: {train_loss:.3f}")
print(f"Training Accuracy: {train_acc:.2f}")

test_loss, test_acc = model.evaluate(test_images, y_test_cat, verbose=0)

print(f"Test Loss: {test_loss:.3f}")
print(f"Test Accuracy: {test_acc:.2f}")

predicted_values = model.predict(test_images)

print("Shape of predicted values:", predicted_values.shape)

# Pick a random test image
n = random.randint(0, len(test_images)-1)

plt.figure(figsize=(4, 4)) # Changed figsize to a tuple (width, height)
plt.imshow(test_images[n])
plt.xticks([])
plt.yticks([])
plt.grid(False)

# Show predicted class name as title
predicted_label = class_names[np.argmax(predicted_values[n])]
plt.title(f"Predicted: {predicted_label}", fontsize=14, fontweight='bold')
plt.show()

plt.figure(figsize=(8,5))
plt.plot(history.history['accuracy'], marker='o')
plt.plot(history.history['val_accuracy'], marker='s')
plt.title('MODEL ACCURACY', fontsize=16, fontweight='bold')
plt.ylabel('Accuracy', fontsize=12)
plt.xlabel('Epoch', fontsize=12)
plt.legend(['Train', 'Validation'], loc='upper left')
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()
