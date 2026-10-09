import numpy as np 
import os

#Директория для сигналов
os.makedirs("data/synthetic", exist_ok = True) #создает папку

#Сигнал постоянный
def generate_carrier(n = 4096, frequency = 100000, sample_rate = 1000000):  #n — количество отсчетов, frequency — частота сигнала, sample_rate — частота дискретизации
    t = np.arange(n) / sample_rate  #массив
    signal = np.exp(2j *  np.pi * frequency * t)    # Создаем комплексную синусоиду с заданной частотой; 1j обозначает мнимую единицу
    noise = 0.1 * (np.random.randn(n) + 1j * np.random.randn(n))     # генератор СЧ
    return signal + noise   # Возврат с шумом
#Генерация с BP
def generate_bpsk(n=4096):
    bits = np.random.choice([-1, 1], size= n) #n случайных символов и две фазы состояния
    noise = 0.1 * (np.random.randn(n) + 1j * np.random.randn(n)) # Имитация РЭБ
    return bits + noise
#Генерация сигнала с QPSK-модуляцией(4 фазовых состояния)
def generate_qpsk(n=4096):
    i = np.random.choice([-1, 1], size= n)
    q = np.random.choice([-1, 1], size= n)
    signal = (i + 1j * q) / np.sqrt(2)
    noise = 0.1 * (np.random.randn(n) + 1j * np.random.randn(n)) 
    return signal + noise
carrier = generate_carrier()
bpsk = generate_bpsk()
qpsk = generate_qpsk()

np.save("data/synthetic/carrier.npy", carrier)
np.save("data/synthetic/bpsk.npy", bpsk)
np.save("data/synthetic/qpsk.npy", qpsk)

print("Сигналы созданы и сохранены!")





