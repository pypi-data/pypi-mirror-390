# Auto-generated from notebook: assignment4_(1).ipynb
# Data handling
import pandas as pd
import numpy as np

# Visualization
import seaborn as sns
import matplotlib.pyplot as plt

# ML Preprocessing + Metrics
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, confusion_matrix

# Deep Learning (Keras / TensorFlow)
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.optimizers import Adam

from imblearn.over_sampling import SMOTE

import warnings
warnings.filterwarnings("ignore")

# Load ECG dataset

data = pd.read_csv("ecg.csv")

# Drop rows with NaN values
data.dropna(inplace=True)

print("Shape:", data.shape)
print("Columns:", data.columns)

# Target column is the last one
target_col = data.columns[-1]
print("Target column:", target_col)

#take input features in x and drops last column
X = data.drop(target_col, axis=1).values
y = data[target_col].values

# Balance dataset using SMOTE (only training data)
smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)

print("Before SMOTE:", np.bincount(y_train.astype(int)))
print("After SMOTE :", np.bincount(y_train_bal.astype(int)))


# Plot class distribution
sns.countplot(x=target_col, data=data)
plt.title("Normal (0) vs Anomaly (1) Distribution")
plt.show()

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Balance dataset using SMOTE (only training data)
smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)

print("Before SMOTE:", np.bincount(y_train.astype(int)))
print("After SMOTE :", np.bincount(y_train_bal.astype(int)))

scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)
X_train_bal_scaled = scaler.transform(X_train_bal)

print("Train Shape:", X_train_scaled.shape)
print("Test Shape:", X_test_scaled.shape)
print("Balanced Train Shape:", X_train_bal_scaled.shape)

#build autoemcoder

# Input size = number of features (e.g., 140 ECG values)
input_dim = X_train_scaled.shape[1]

autoencoder = models.Sequential([
    layers.Input(shape=(input_dim,)),      # Input layer

    # Encoder
    layers.Dense(64, activation="relu"),
    layers.Dense(32, activation="relu"),
    layers.Dense(16, activation="relu"),

    # Bottleneck
    layers.Dense(8, activation="relu"),

    # Decoder
    layers.Dense(16, activation="relu"),
    layers.Dense(32, activation="relu"),
    layers.Dense(64, activation="relu"),

    # Output (same size as input)
    layers.Dense(input_dim, activation="sigmoid")  # works with MinMaxScaler
])

# Compile
autoencoder.compile(optimizer=Adam(learning_rate=0.001),
                    loss="mse",
                    metrics=["mae"])

autoencoder.summary()
# Print model summary (layers, params)

#train
from tensorflow.keras.callbacks import EarlyStopping

early_stopping = EarlyStopping(
    monitor='val_loss',  # Monitor validation loss
    patience=5,          # Number of epochs with no improvement after which training will be stopped.
    restore_best_weights=True # Restore model weights from the epoch with the best value of the monitored quantity.
)

history = autoencoder.fit(
    X_train_scaled, X_train_scaled,
    epochs=20, batch_size=512,
    validation_data=(X_test_scaled, X_test_scaled),
    callbacks=[early_stopping], # Add early stopping callback
    verbose=1
)


# Plot training and validation loss
plt.plot(history.history['loss'], label="Train Loss")
plt.plot(history.history['val_loss'], label="Validation Loss")
plt.xlabel("Epochs")
plt.ylabel("MSE Loss")
plt.legend()
plt.show()

# Get predictions
X_train_pred = autoencoder.predict(X_train_scaled)
X_test_pred = autoencoder.predict(X_test_scaled)

# Reconstruction errors
#error = (original - reconstructed)^2
train_errors = np.mean(np.square(X_train_scaled - X_train_pred), axis=1)
test_errors = np.mean(np.square(X_test_scaled - X_test_pred), axis=1)

# Threshold (mean + std of training error)
threshold = np.mean(train_errors) + np.std(train_errors)
print("Reconstruction Threshold:", threshold)

# Create a DataFrame for plotting
error_df = pd.DataFrame({'reconstruction_error': test_errors, 'true_class': y_test})
error_df['true_class'] = error_df['true_class'].astype(int)

# Plot the distribution of reconstruction errors
plt.figure(figsize=(10, 6))
sns.histplot(data=error_df, x='reconstruction_error', hue='true_class', kde=True, bins=50)
plt.axvline(threshold, color='red', linestyle='dashed', linewidth=2, label=f'Threshold: {threshold:.4f}')
plt.title('Distribution of Reconstruction Errors for Normal and Anomaly Classes')
plt.xlabel('Reconstruction Error')
plt.ylabel('Frequency')
plt.legend()
plt.show()

# Predict anomalies
y_pred = [1 if e > threshold else 0 for e in test_errors]

# Accuracy
acc = accuracy_score(y_test, y_pred)
print("Accuracy:", acc)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()
