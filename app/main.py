import streamlit as st
import subprocess
import sys
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="RadioAI", page_icon="📡")

st.title("📡 RadioAI")
st.subheader("Анализ и распознавание радиосигналов")

st.divider()

st.header("1. Проверка модели")

if st.button("Запустить проверку"):
    result = subprocess.run(
        [sys.executable, "src/predict_signals.py"],
        capture_output=True,
        text=True,
        encoding="cp1251"
    )

    if result.returncode == 0:
        names = []
        values = []

        for line in result.stdout.splitlines():
            if "точность:" in line:
                name, value = line.split(" - точность: ")
                names.append(name)
                values.append(float(value.replace("%", "").strip()))

        if values:
            st.success("Проверка завершена")

            cols = st.columns(len(names))
            for i, col in enumerate(cols):
                col.metric(names[i], f"{values[i]:.1f}%")

            st.bar_chart({
                "Тип сигнала": names,
                "Точность (%)": values
            }, x="Тип сигнала", y="Точность (%)")
        else:
            st.warning("Результаты не найдены")
            st.code(result.stdout)
    else:
        st.error("Ошибка при проверке")
        st.code(result.stderr)

st.divider()

st.header("2. Визуализация сигнала")

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
plt.close(fig)

fig, ax = plt.subplots()
ax.plot(np.abs(np.fft.fft(signal)))
ax.set_title(f"{signal_type}: спектр")
ax.set_xlabel("Частотный отсчёт")
ax.set_ylabel("Амплитуда")
st.pyplot(fig)
plt.close(fig)

st.divider()

st.header("3. Распознавание сигнала")

if st.button("Распознать выбранный сигнал"):
    model = None

    try:
        import joblib
        model = joblib.load("models/radio_model.pkl")
    except Exception as error:
        st.error(f"Не удалось загрузить модель: {error}")

    if model is not None:
        amplitude = np.abs(signal)
        phase = np.angle(signal)

        features = [[
            np.mean(amplitude ** 2),
            np.mean(amplitude),
            np.std(amplitude),
            np.std(phase)
        ]]

        prediction = model.predict(features)[0]

        classes = {
            0: "Несущая",
            1: "BPSK",
            2: "QPSK"
        }

        st.success(f"Модель распознала сигнал: {classes[prediction]}")