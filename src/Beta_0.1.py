
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# Генерация сигналов

def generate_carrier():
    n = 1024
    t = np.arange(n) / 1_000_000
    signal = np.exp(2j * np.pi * 100_000 * t)
    noise = 0.1 * (
        np.random.randn(n) + 1j * np.random.randn(n)
    )
    return signal + noise

def generate_bpsk():
    bits = np.random.choice([-1, 1], 1024)
    noise = 0.1 * (
        np.random.randn(1024) + 1j * np.random.randn(1024)
    )
    return bits + noise

def generate_qpsk():
    i = np.random.choice([-1, 1], 1024)
    q = np.random.choice([-1, 1], 1024)
    signal = (i + 1j * q) / np.sqrt(2)
    noise = 0.1 * (
        np.random.randn(1024) + 1j * np.random.randn(1024)
    )
    return signal + noise

# Признаки сигнала

def get_features(signal):
    amplitude = np.abs(signal)
    phase = np.angle(signal)

    power = np.mean(amplitude ** 2)
    mean_amplitude = np.mean(amplitude)
    amplitude_std = np.std(amplitude)
    phase_std = np.std(phase)

    return [
        power,
        mean_amplitude,
        amplitude_std,
        phase_std
    ]

# Создание набора данных

X = []
y = []

generators = [
    (generate_carrier, 0),
    (generate_bpsk, 1),
    (generate_qpsk, 2)
]

for generator, label in generators:
    for _ in range(100):
        signal = generator()
        X.append(get_features(signal))
        y.append(label)

X = np.array(X)
y = np.array(y)

# Разделение данных

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# Обучение и проверка

model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print("Обучение завершено")
print("Количество примеров:", len(X))
print("Точность на тестовых данных:", round(accuracy * 100, 2), "%")
from sklearn.metrics import confusion_matrix

print("Матрица ошибок:")
print(confusion_matrix(y_test, predictions))

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/radio_model.pkl")

print("Модель сохранена в models/radio_model.pkl")