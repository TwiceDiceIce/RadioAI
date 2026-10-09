import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Визуализация радиосигналов")

signal_type = st.selectbox(
    "Выбери тип сигнала",
    ["Несущая", "BPSK", "QPSK"]
)

n = 1024
noise = 0.1 * (
    np.random.randn(n) + 1j * np.random.randn(n)
)

if signal_type == "Несущая":
    t = np.arange(n) / 1_000_000
    signal = np.exp(2j * np.pi * 100_000 * t) + noise
elif signal_type == "BPSK":
    bits = np.random.choice([-1, 1], n)
    signal = bits + noise
else:
    i = np.random.choice([-1, 1], n)
    q = np.random.choice([-1, 1], n)
    signal = (i + 1j * q) / np.sqrt(2) + noise

fig, ax = plt.subplots()
ax.plot(signal.real[:100])
ax.set_title(f"{signal_type}: форма сигнала")
ax.set_xlabel("Отсчёт")
ax.set_ylabel("Амплитуда")
st.pyplot(fig)

fig, ax = plt.subplots()
ax.plot(np.abs(np.fft.fft(signal)))
ax.set_title(f"{signal_type}: спектр")
ax.set_xlabel("Номер частотного отсчёта")
ax.set_ylabel("Амплитуда")
st.pyplot(fig)