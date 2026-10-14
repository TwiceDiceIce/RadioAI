from virtual_radio import VirtualRadio
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import uuid

# Параметры шифрования
alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
vigenere_key = "ключ"
xor_key = b"key"
aes_key = AESGCM.generate_key(bit_length=128)

radio = VirtualRadio()
# Параметры раций
radio_settings = {
    1: {"channel": 1, "encryption": 3, "version": 0},
    2: {"channel": 1, "encryption": 3, "version": 0},
}

# Синхрон инициациированный  любой из двух раций
def synchronize_radios(channel, encryption, sender):
    
    if sender not in (1, 2):
        print("Ошибка: неизвестная станция.")
        return False

    if channel not in radio.CHANNELS:
        print("Ошибка: такого рабочего канала нет.")
        return False

    if encryption not in (1, 2, 3):
        print("Ошибка: неизвестный алгоритм шифрования.")
        return False

    receiver = 2 if sender == 1 else 1

    version = max(
        radio_settings[1]["version"],
        radio_settings[2]["version"],
    ) + 1

    beacon = f"{version}|{channel}|{encryption}".encode("utf-8")

    print(f"\nАльфа № {sender}: синхронизация раций")
    print("Выбран рабочий канал:", channel)
    print("Алгоритм:", encryption)

    for attempt in range(1, 4):
        print(f"Маяк: попытка {attempt} из 3")

        delivered = radio.transmit(
            sender, radio.CONTROL_CHANNEL, beacon
        )

        if not delivered:
            print("Маяк потерян.")
            continue

        packet = radio.receive(receiver)

        if packet is None:
            print("Маяк не получен.")
            continue

        control_channel, data = packet

        if control_channel != radio.CONTROL_CHANNEL:
            print("Получен пакет не с управляющего канала.")
            continue

        try:
            received_version, received_channel, received_encryption = (
                int(value) for value in data.decode("utf-8").split("|")
            )
        except (ValueError, UnicodeDecodeError):
            print("Ошибка: некорректный управляющий маяк.")
            return False

        if received_version != version:
            print("Ошибка: версия настроек не совпадает.")
            return False

        if received_channel not in radio.CHANNELS:
            print("Ошибка: получен недопустимый канал.")
            return False

        if received_encryption not in (1, 2, 3):
            print("Ошибка: неизвестный алгоритм шифрования.")
            return False

        # Подтверждаем получение конкретного маяка.
        if not radio.send_ack(sender, receiver):
            print("ACK синхронизации потерян. Повторяем маяк.")
            continue

        # Применяем согласованные настройки после ACK.
        new_settings = {
            "channel": received_channel,
            "encryption": received_encryption,
            "version": received_version,
        }

        radio_settings[1] = new_settings.copy()
        radio_settings[2] = new_settings.copy()

        print("Рации синхронизированы!")
        print("Альфа № 1:", radio_settings[1])
        print("Альфа № 2:", radio_settings[2])
        return True

    print("Не удалось синхронизировать рации.")
    return False

# Шифр Виженера

def encrypt_vigenere(message):
    result = ""
    key_position = 0

    for letter in message:
        is_upper = letter.isupper()
        lower_letter = letter.lower()

        if lower_letter in alphabet:
            letter_position = alphabet.index(lower_letter)
            shift = alphabet.index(
                vigenere_key[key_position % len(vigenere_key)].lower()
            )

            encrypted_letter = alphabet[
                (letter_position + shift) % len(alphabet)
            ]

            if is_upper:
                encrypted_letter = encrypted_letter.upper()

            result += encrypted_letter
            key_position += 1
        else:
            result += letter

    return result


def decrypt_vigenere(message):
    result = ""
    key_position = 0

    for letter in message:
        is_upper = letter.isupper()
        lower_letter = letter.lower()

        if lower_letter in alphabet:
            letter_position = alphabet.index(lower_letter)
            shift = alphabet.index(
                vigenere_key[key_position % len(vigenere_key)].lower()
            )

            decrypted_letter = alphabet[
                (letter_position - shift) % len(alphabet)
            ]

            if is_upper:
                decrypted_letter = decrypted_letter.upper()

            result += decrypted_letter
            key_position += 1
        else:
            result += letter

    return result

# Шифр XOR
def encrypt_xor(message):
    message_bytes = message.encode("utf-8")
    result = bytearray()

    for i in range(len(message_bytes)):
        result.append(message_bytes[i] ^ xor_key[i % len(xor_key)])

    return bytes(result)

def decrypt_xor(encrypted):
    result = bytearray()

    for i in range(len(encrypted)):
        result.append(encrypted[i] ^ xor_key[i % len(xor_key)])

    return bytes(result).decode("utf-8")

# AES-128
def encrypt_aes(message):
    nonce = os.urandom(12)
    encrypted = AESGCM(aes_key).encrypt(
        nonce, message.encode("utf-8"), None
    )
    return nonce + encrypted

def decrypt_aes(encrypted):
    nonce = encrypted[:12]
    ciphertext = encrypted[12:]
    decrypted = AESGCM(aes_key).decrypt(nonce, ciphertext, None)
    return decrypted.decode("utf-8")

# Шифрование и дешифрование
def encrypt_message(message, channel):
    if channel == 1:
        return encrypt_vigenere(message).encode("utf-8")
    elif channel == 2:
        return encrypt_xor(message)
    elif channel == 3:
        return encrypt_aes(message)

    raise ValueError("Неизвестный канал")

def decrypt_message(encrypted_data, channel):
    if channel == 1:
        return decrypt_vigenere(encrypted_data.decode("utf-8"))
    elif channel == 2:
        return decrypt_xor(encrypted_data)
    elif channel == 3:
        return decrypt_aes(encrypted_data)

    raise ValueError("Неизвестный канал")

# Отправка с подтверждением и повторами
def find_best_channel(current_channel):
    candidates = [
        channel
        for channel in radio.CHANNELS
        if channel != current_channel
    ]

    if not candidates:
        return None

    return max(
        candidates,
        key=lambda channel: radio.channel_quality[channel]
    )

def send_message(sender, message, channel, encryption):
    print(f"\nАльфа № {sender} отправляет:", message)
    print("Рабочий канал:", channel)
    print("Алгоритм шифрования:", encryption)

    message_id = uuid.uuid4().hex
    encrypted_data = encrypt_message(message, encryption)
    receiver = 2 if sender == 1 else 1

    max_attempts = 3
    max_channel_switches = 3
    switches = 0
    tried_channels = {channel}
    
    while True:
        delivery_confirmed = False

        # Пытаемся передать сообщение на текущем канале
        for attempt in range(1, max_attempts + 1):
            print(f"\nПопытка {attempt} из {max_attempts}")

            packet_data = (
                message_id.encode("utf-8")
                + b"|"
                + str(encryption).encode("ascii")
                + b"|"
                + encrypted_data
            )

            delivered = radio.transmit(sender, channel, packet_data)

            if not delivered:
                print("Нет доставки. Повторяем отправку.")
                continue

            received_message = receive_message(receiver, encryption)

            if not received_message:
                print("Приём не подтверждён. Повторяем отправку.")
                continue

            ack_received = radio.send_ack(sender, receiver)

            if ack_received:
                print(f"Доставка подтверждена на канале {channel}.")
                delivery_confirmed = True
                break

            print("ACK не получен. Повторяем отправку.")

        if delivery_confirmed:
            return received_message

        # Если попытки закончились, ищем другой канал
        channel_ready = False

        while switches < max_channel_switches:
            candidates = [
                candidate
                for candidate in radio.CHANNELS
                if candidate not in tried_channels
            ]

            if not candidates:
                print("ОШИБКА: не осталось непроверенных каналов.")
                return False

            new_channel = max(
                candidates,
                key=lambda candidate: radio.channel_quality[candidate]
            )

            tried_channels.add(new_channel)
            switches += 1

            print(
                f"\nПереключение: канал {channel} "
                f"(качество {radio.channel_quality[channel]}/100) "
                f"-> канал {new_channel} "
                f"(качество {radio.channel_quality[new_channel]}/100)"
            )

            if not synchronize_radios(new_channel, encryption, sender):
                print(
                    f"Синхронизация канала {new_channel} не удалась. "
                    "Пробуем следующий канал."
                )
                continue

            channel = new_channel
            channel_ready = True
            break

        if not channel_ready:
            print(
                "ОШИБКА: не удалось перейти на рабочий канал "
                "в пределах лимита переключений."
            )
            return False
received_message_ids = {1: set(), 2: set()}        
received_messages = {1: {}, 2: {}}

def receive_message(receiver, encryption):
    packet = radio.receive(receiver)

    if packet is None:
        print(f"Альфа № {receiver}: сообщение не получено.")
        return False

    channel, packet_data = packet
    expected_encryption = radio_settings[receiver]["encryption"]
    
    expected_channel = radio_settings[receiver]["channel"]

    if channel != expected_channel:
        print(f"Альфа № {receiver}: неверный рабочий канал.")
        return False

    if encryption != expected_encryption:
        print(
            f"Альфа № {receiver}: несовпадение алгоритмов шифрования. "
            f"Ожидался алгоритм {expected_encryption}, "
            f"получен {encryption}."
        )
        return False

    try:
        message_id_bytes, encryption_bytes, encrypted_data = (
            packet_data.split(b"|", 2)
        )
        message_id = message_id_bytes.decode("utf-8")
        packet_encryption = int(encryption_bytes.decode("ascii"))

        if packet_encryption not in (1, 2, 3):
            raise ValueError("неизвестный алгоритм шифрования")

    except (ValueError, UnicodeDecodeError):
        print("Ошибка: некорректный формат пакета.")
        return False

    if packet_encryption != expected_encryption:
        print(
            f"Альфа № {receiver}: несовпадение алгоритмов шифрования. "
            f"Ожидался алгоритм {expected_encryption}, "
            f"в пакете указан {packet_encryption}."
        )
        return False

    # Повторно полученное сообщение не показываем,
    # но считаем его доставленным.
    if message_id in received_message_ids[receiver]:
        print(
            f"Альфа № {receiver}: дубликат сообщения "
            f"{message_id}, повторно не отображаем."
        )

        if message_id in received_messages[receiver]:
            return received_messages[receiver][message_id]

        print("Ошибка: текст сообщения не найден в сохранённых данных.")
        return False

    try:
        message = decrypt_message(encrypted_data, packet_encryption)
    except Exception as error:
        print(f"Ошибка расшифровки: {error}")
        return False

    received_message_ids[receiver].add(message_id)
    received_messages[receiver][message_id] = message

    print(f"Альфа № {receiver} получила:", message)
    return message

def run_all_tests():
    tests = [
        ("Целостность AES-128-GCM", test_aes_integrity),
        ("Несовпадение алгоритмов", test_encryption_mismatch),
        ("Неизвестный алгоритм", test_unknown_encryption),
        ("Повреждённый пакет", test_malformed_packet),
        ("Неправильный канал", test_wrong_channel),
        ("Потеря ACK и дубликаты", test_ack_loss_and_duplicate),
    ]

    passed = 0
    failed = 0

    print("\n--- Тестирование Alpha ---")

    for test_name, test_function in tests:
        print(f"\n[{test_name}]")

        try:
            result = test_function()

            if result is True:
                print(f"Итог: {test_name} — ПРОЙДЕН")
                passed += 1
            else:
                print(f"Итог: {test_name} — НЕ ПРОЙДЕН")
                failed += 1

        except Exception as error:
            print(f"Итог: {test_name} — ОШИБКА: {error}")
            failed += 1

    print("\n--- Итоги тестирования Alpha ---")
    print(f"Пройдено: {passed}")
    print(f"Не пройдено: {failed}")
    print(f"Всего: {len(tests)}")

def get_test_list():
    return [
        {
            "name": "Целостность AES-128-GCM",
            "description": "Проверяет обнаружение изменений зашифрованных данных.",
            "function": test_aes_integrity,
        },
        {
            "name": "Несовпадение алгоритмов",
            "description": "Проверяет отказ при несовпадении алгоритмов шифрования.",
            "function": test_encryption_mismatch,
        },
        {
            "name": "Неизвестный алгоритм",
            "description": "Проверяет отклонение неподдерживаемого алгоритма.",
            "function": test_unknown_encryption,
        },
        {
            "name": "Повреждённый пакет",
            "description": "Проверяет обработку пакета с некорректным форматом.",
            "function": test_malformed_packet,
        },
        {
            "name": "Неправильный канал",
            "description": "Проверяет отказ при получении пакета не на рабочем канале.",
            "function": test_wrong_channel,
        },
        {
            "name": "Потеря ACK и дубликаты",
            "description": "Проверяет повторную передачу после потери ACK и обнаружение дубликатов.",
            "function": test_ack_loss_and_duplicate,
        },
    ]


def test_aes_integrity():
    print("\n--- Тест целостности AES-128-GCM ---")

    original_message = "Привет"
    encrypted = encrypt_message(original_message, 3)

    # Изменяем один байт зашифрованных данных.
    tampered = bytearray(encrypted)
    tampered[12] ^= 1

    try:
        decrypt_message(bytes(tampered), 3)
    except Exception:
        print("Подмена обнаружена.")
        return True

    print("ОШИБКА: изменённые данные были приняты.")
    return False




def test_encryption_mismatch():
    print("\n--- Тест несовпадения алгоритмов ---")

    receiver = 1
    message_id = uuid.uuid4().hex
    old_encryption = radio_settings[receiver]["encryption"]

    try:
        packet_data = (
            message_id.encode("utf-8")
            + b"|1|"
            + encrypt_message("Тест", 1)
        )

        radio.messages_for_alpha1.append((1, packet_data))
        radio_settings[receiver]["encryption"] = 3

        result = receive_message(receiver, 3)

        if result is False:
            print("Тест пройден: несовпадение обнаружено.")
            return True

        print("ОШИБКА: пакет принят несмотря на несовпадение.")
        return False

    finally:
        radio_settings[receiver]["encryption"] = old_encryption

    

def test_unknown_encryption():
    print("\n--- Тест неизвестного алгоритма ---")

    receiver = 1
    message_id = uuid.uuid4().hex

    packet_data = (
        message_id.encode("utf-8")
        + b"|9|"
        + b"test"
    )

    radio.messages_for_alpha1.append((1, packet_data))

    result = receive_message(
        receiver,
        radio_settings[receiver]["encryption"]
    )

    if result is False:
        print("Тест пройден: неизвестный алгоритм отклонён.")
        return True

    print("ОШИБКА: пакет с неизвестным алгоритмом принят.")
    return False

def test_malformed_packet():
    print("\n--- Тест повреждённого пакета ---")

    receiver = 1

    radio.messages_for_alpha1.append((1, b"broken_packet"))

    result = receive_message(
        receiver,
        radio_settings[receiver]["encryption"]
    )

    if result is False:
        print("Тест пройден: повреждённый пакет отклонён.")
        return True

    print("ОШИБКА: повреждённый пакет принят.")
    return False



def test_wrong_channel():
    print("\n--- Тест неправильного канала ---")

    receiver = 1
    expected_channel = radio_settings[receiver]["channel"]

    wrong_channel = expected_channel + 1

    if wrong_channel not in radio.CHANNELS:
        wrong_channel = expected_channel - 1

    radio.messages_for_alpha1.append(
        (wrong_channel, b"test_packet")
    )

    result = receive_message(
        receiver,
        radio_settings[receiver]["encryption"]
    )

    if result is False:
        print("Тест пройден: пакет с неправильного канала отклонён.")
        return True

    print("ОШИБКА: пакет с неправильного канала принят.")
    return False

def test_ack_loss_and_duplicate():
    print("\n--- Тест потери ACK и дубликатов ---")

    sender = 1
    receiver = 2
    channel = 1
    encryption = 3
    message = "Тест потери ACK"

    # Сохраняем исходные настройки.
    old_packet_loss = radio.PACKET_LOSS
    old_ack_loss = radio.ACK_LOSS
    old_sender_settings = radio_settings[sender].copy()
    old_receiver_settings = radio_settings[receiver].copy()

    old_sender_messages = radio.messages_for_alpha1.copy()
    old_receiver_messages = radio.messages_for_alpha2.copy()

    old_received_ids = received_message_ids[receiver].copy()
    old_received_messages = received_messages[receiver].copy()

    original_send_ack = radio.send_ack
    ack_attempts = 0

    def test_send_ack(ack_sender, ack_receiver, force_loss=False):
        nonlocal ack_attempts
        ack_attempts += 1

        if ack_attempts == 1:
            print("ТЕСТ: намеренно теряем первый ACK.")
            return False

        return original_send_ack(
            ack_sender,
            ack_receiver,
            force_loss=False
        )

    try:
        # Убираем случайные потери пакетов и ACK.
        radio.PACKET_LOSS = 0
        radio.ACK_LOSS = 0

        # Синхронизируем обе станции.
        if not synchronize_radios(channel, encryption, sender):
            print("ОШИБКА: не удалось синхронизировать станции.")
            return False

        # Убираем старые пакеты, чтобы они не повлияли на тест.
        radio.messages_for_alpha1.clear()
        radio.messages_for_alpha2.clear()

        received_message_ids[receiver].clear()
        received_messages[receiver].clear()

        # Теряем первый ACK, но пропускаем следующий.
        radio.send_ack = test_send_ack

        result = send_message(sender, message, channel, encryption)

        # Проверяем итог передачи и число подтверждений.
        if result != message:
            print("ОШИБКА: отправитель не получил подтверждение доставки.")
            return False

        if ack_attempts < 2:
            print("ОШИБКА: повторная попытка ACK не произошла.")
            return False

        if len(received_message_ids[receiver]) != 1:
            print("ОШИБКА: сообщение зарегистрировано не один раз.")
            return False

        if len(received_messages[receiver]) != 1:
            print("ОШИБКА: в сохранённых сообщениях есть дубликаты.")
            return False

        print("Тест пройден: повторная передача подтверждена.")
        print("Количество попыток ACK:", ack_attempts)
        return True

    finally:
        # Возвращаем исходное поведение радиостанции.
        radio.send_ack = original_send_ack
        radio.PACKET_LOSS = old_packet_loss
        radio.ACK_LOSS = old_ack_loss

        radio_settings[sender] = old_sender_settings
        radio_settings[receiver] = old_receiver_settings

        radio.messages_for_alpha1[:] = old_sender_messages
        radio.messages_for_alpha2[:] = old_receiver_messages

        received_message_ids[receiver].clear()
        received_message_ids[receiver].update(old_received_ids)

        received_messages[receiver].clear()
        received_messages[receiver].update(old_received_messages)

def main():
    while True:
        print("\n--- Система Alpha ---")
        print("1 — Передать от Альфы № 1")
        print("2 — Передать от Альфы № 2")
        print("3 — Запустить все тесты")
        print("0 — Выход")

        action = input("Выбери действие: ")

        if action == "0":
            break

        elif action == "3":
            run_all_tests()
            continue

        elif action in ("1", "2"):
            sender = int(action)

            print("\nДоступны каналы: 1–16")
            try:
                channel = int(input("Рабочий канал: "))
            except ValueError:
                print("Нужно ввести номер канала.")
                continue

            if channel not in radio.CHANNELS:
                print("Ошибка: выбери канал от 1 до 16.")
                continue

            print("\nАлгоритм шифрования:")
            print("1 — Виженер")
            print("2 — XOR")
            print("3 — AES-128-GCM")

            try:
                encryption = int(input("Алгоритм: "))
            except ValueError:
                print("Нужно ввести номер алгоритма.")
                continue

            if encryption not in (1, 2, 3):
                print("Неизвестный алгоритм.")
                continue

            if not synchronize_radios(channel, encryption, sender):
                print("Не удалось синхронизировать рации. Передача отменена.")
                continue

            message = input("\nСообщение: ")
            send_message(sender, message, channel, encryption)

        else:
            print("Неизвестная команда.")


if __name__ == "__main__":
    main()

    


