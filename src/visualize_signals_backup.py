import numpy as np
import matplotlib.pyplot as plt

#Загрузка сигналов
carrier = np.load("data/synthetic/carrier.npy") 
bpsk = np.load("data/synthetic/bpsk.npy")
qpsk = np.load("data/synthetic/qpsk.npy")

#Три сигнала
plt.figure(figsize=(10, 6))

plt.subplot(3, 1, 1)#размещение графика
plt.plot(carrier.real[:100])#первые 100 отсчетов
plt.title("Сarrier")

plt.subplot(3, 1, 2)
plt.plot(bpsk.real[:100])
plt.title("BPSK")

plt.subplot(3, 1, 3)
plt.plot(qpsk.real[:100])
plt.title("QPSK")

plt.tight_layout()
plt.show()

print("Графики построены!")