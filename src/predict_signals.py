
import numpy as np
import joblib

# Загружаем сохранённую модель
model = joblib.load("models/radio_model.pkl")

# Генерируем тестовый сигнал
def generate_carrier():
    t = np.arange(1024) / 1_000_000
    signal = np.exp(2j * np.pi * 100_000 * t)
    noise = 0.1 * (
        np.random.randn(1024) + 1j * np.random.randn(1024)
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

# Вычисляем признаки так же, как при обучении
def get_features(signal):
    amplitude = np.abs(signal)
    phase = np.angle(signal)

    power = np.mean(amplitude ** 2)
    mean_amplitude = np.mean(amplitude)
    amplitude_std = np.std(amplitude)
    phase_std = np.std(phase)

    return [[
        power,
        mean_amplitude,
        amplitude_std,
        phase_std
    ]]


classes = {
    0: "Несущая",
    1: "BPSK",
    2: "QPSK"
}


correct = {"Несущая": 0, "BPSK": 0, "QPSK": 0}
total = {"Несущая": 10, "BPSK": 10, "QPSK": 10}

for i in range(10):
    signal = generate_carrier()
    prediction = model.predict(get_features(signal))[0]
    if prediction == 0:
        correct["Несущая"] += 1

for i in range(10):
    signal = generate_bpsk()
    prediction = model.predict(get_features(signal))[0]
    if prediction == 1:
        correct["BPSK"] += 1

for i in range(10):
    signal = generate_qpsk()
    prediction = model.predict(get_features(signal))[0]
    if prediction == 2:
        correct["QPSK"] += 1

with open("results.txt", "w", encoding="utf-8") as file:
    for name in correct:
        accuracy = correct[name] / total[name] * 100
        print(name, "- точность:", round(accuracy, 2), "%")
        file.write(f"{name} - точность: {round(accuracy, 2)}%\n")
