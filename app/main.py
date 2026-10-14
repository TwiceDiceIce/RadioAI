import streamlit as st
import sys
import os

# Добавляем папку src для импорта модулей проекта
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_path, "src")

if src_path not in sys.path:
    sys.path.insert(0, src_path)

if src_path not in sys.path:
    sys.path.insert(0, src_path)

import Alpha as alpha
# Подключение виртуальной радиостанции
from src.virtual_radio import VirtualRadio

# Сохранение состояния Альфы
if "alpha_radio" not in st.session_state:
    st.session_state.alpha_radio = VirtualRadio()

if "alpha_settings" not in st.session_state:
    st.session_state.alpha_settings = {
        1: {"channel": 1, "encryption": 3, "version": 0},
        2: {"channel": 1, "encryption": 3, "version": 0},
    }
# Подключаем сохранённые объекты к логике Альфы
alpha.radio = st.session_state.alpha_radio
alpha.radio_settings = st.session_state.alpha_settings
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

st.divider()

st.header("Тестирование Alpha")

st.write(
    "Проверь работу шифрования, каналов, пакетов "
    "и подтверждения доставки перед использованием радиостанций."
)

if st.button("4.Запустить тесты", key="alpha_run_tests"):
    import contextlib
    import io

    test_results = []

    for test in alpha.get_test_list():
        output = io.StringIO()

        try:
            with contextlib.redirect_stdout(output):
                result = test["function"]()

            test_results.append({
                "name": test["name"],
                "description": test["description"],
                "status": "Пройден" if result else "Не пройден",
                "log": output.getvalue(),
            })

        except Exception as error:
            test_results.append({
                "name": test["name"],
                "description": test["description"],
                "status": "Ошибка",
                "log": output.getvalue() + str(error),
            })

    st.session_state.alpha_test_results = test_results

if "alpha_test_results" in st.session_state:
    results = st.session_state.alpha_test_results

    passed = sum(
        1 for test in results
        if test["status"] == "Пройден"
    )

    st.write(f"Результат: {passed} из {len(results)} тестов пройдено.")

    for test in results:
        with st.expander(
            f"{test['status']}: {test['name']}"
        ):
            st.write(test["description"])

            if test["log"]:
                st.text(test["log"])



st.header("5. Альфа 0.1 — виртуальная радиосвязь")

st.write("Управление двумя виртуальными радиостанциями.")

# Выбор станции
sender = st.selectbox(
    "Передающая станция",
    [1, 2],
    format_func=lambda number: f"Альфа № {number}",
    key="alpha_sender",
)

# Выбор канала
channel = st.selectbox(
    "Рабочий канал",
    list(range(1, 17)),
    key="alpha_channel",
)

# Выбор шифрования
encryption_names = {
    1: "Виженер",
    2: "XOR",
    3: "AES-128-GCM",
}

encryption = st.selectbox(
    "Алгоритм шифрования",
    options=[1, 2, 3],
    format_func=lambda number: encryption_names[number],
    key="alpha_encryption",
)

# Текст сообщения
message = st.text_area(
    "Текст сообщения",
    key="alpha_message",
)

if st.button("Отправить сообщение", key="alpha_send"):
    if not message.strip():
        st.warning("Сначала введи текст сообщения.")
    else:
        # Подключаем сохранённые объекты
        alpha.radio = st.session_state.alpha_radio
        alpha.radio_settings = st.session_state.alpha_settings

        # Сохраняем AES-ключ между перезапусками страницы
        if "alpha_aes_key" not in st.session_state:
            st.session_state.alpha_aes_key = alpha.aes_key

        alpha.aes_key = st.session_state.alpha_aes_key

        # Сохраняем историю обработанных сообщений
        if "alpha_received_message_ids" not in st.session_state:
            st.session_state.alpha_received_message_ids = {
                1: set(),
                2: set(),
            }
        if "alpha_received_messages" not in st.session_state:
            st.session_state.alpha_received_messages = {1: {}, 2: {}}

        alpha.received_messages = st.session_state.alpha_received_messages
        
        if "alpha_messages" not in st.session_state:
            st.session_state.alpha_messages = []

        alpha.received_message_ids = (
            st.session_state.alpha_received_message_ids
        )

        # Синхронизируем настройки радиостанций
        synchronized = alpha.synchronize_radios(
            channel,
            encryption,
            sender,
        )

        if synchronized:
            received_message = alpha.send_message(
                sender,
                message,
                channel,
                encryption,
            )

            if received_message:
                st.success("Передача завершена.")
                st.subheader("Принятое сообщение")
                st.write(f"Альфа № {2 if sender == 1 else 1}:")
                st.text(received_message)
            else:
                st.warning(
                    "Не удалось подтвердить доставку сообщения."
                )
        else:
            st.error("Не удалось синхронизировать радиостанции.")

st.subheader("Текущие настройки")
encryption_names = {
    1: "Виженер",
    2: "XOR",
    3: "AES-128-GCM",
}
for number in [1, 2]:
    settings = st.session_state.alpha_settings[number]

    st.markdown(f"**Альфа № {number}**")
    st.write(f"Канал: {settings['channel']}")
    st.write(
        f"Шифрование: {encryption_names[settings['encryption']]}"
    )
    st.write(f"Версия: {settings['version']}")

    if number == 1:
        st.divider()
