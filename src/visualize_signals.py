
import numpy as np
import matplotlib.pyplot as plt

# Загрузка сигналов
carrier = np.load("data/synthetic/carrier.npy")
bpsk = np.load("data/synthetic/bpsk.npy")
qpsk = np.load("data/synthetic/qpsk.npy")

signals = [
    ("Carrier", carrier),
    ("BPSK", bpsk),
    ("QPSK", qpsk),
]

# Создаем окно: сигнал и спектр для каждого типа
plt.figure(figsize=(12, 10))

for i, (name, signal) in enumerate(signals):
    # Первые 100 отсчетов сигнала
    plt.subplot(3, 2, 2 * i + 1)
    plt.plot(signal.real[:100])
    plt.title(f"{name} — сигнал")
    plt.xlabel("Номер отсчета")
    plt.ylabel("Амплитуда")

    # Спектр сигнала
    spectrum = np.fft.fftshift(np.fft.fft(signal))
    frequencies = np.fft.fftshift(np.fft.fftfreq(len(signal), d=1 / 1_000_000))

    plt.subplot(3, 2, 2 * i + 2)
    plt.plot(frequencies / 1000, 20 * np.log10(np.abs(spectrum) + 1e-12))
    plt.title(f"{name} — спектр")
    plt.xlabel("Частота, кГц")
    plt.ylabel("Уровень, дБ")

plt.tight_layout()
plt.show()
input("Нажми Enter для завершения...")