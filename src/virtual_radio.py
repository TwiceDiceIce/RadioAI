import random

class VirtualRadio:
    CHANNELS = list(range(1, 17))
    CONTROL_CHANNEL = 0

    PACKET_LOSS = 0.2
    ACK_LOSS = 0.2

    def __init__(self):
        self.messages_for_alpha1 = []
        self.messages_for_alpha2 = []

        # Качество каждого рабочего канала: от 0 до 100
        self.channel_quality = {
            channel: random.randint(20, 100)
            for channel in self.CHANNELS
        }

        print("\nНачальное качество каналов:")
        for channel, quality in self.channel_quality.items():
            print(f"Канал {channel}: {quality}/100")

    # Передача пакета
        # Постепенное изменение качества радиоканалов
    def update_channel_quality(self):
        for channel in self.CHANNELS:
            change = random.randint(-5, 5)
            new_quality = self.channel_quality[channel] + change
            self.channel_quality[channel] = max(0, min(100, new_quality))

    def transmit(self, sender, channel, data):
        if channel != self.CONTROL_CHANNEL and channel not in self.CHANNELS:
            raise ValueError("Такого канала нет")

        print("\n--- Виртуальный эфир ---")
        print("Отправитель:", sender)
        print("Канал:", "Управляющий" if channel == 0 else channel)
        print("Размер данных:", len(data), "байт")
        # Постоянное изменение качества
        self.update_channel_quality()
        if channel != self.CONTROL_CHANNEL:
            print(
                f"Качество канала {channel}: "
                f"{self.channel_quality[channel]}/100"
            )

        if channel == self.CONTROL_CHANNEL:
            loss_probability = self.PACKET_LOSS
        else:
            quality = self.channel_quality[channel]
            loss_probability = (100 - quality) / 100

        if random.random() < loss_probability:
            print("ПАКЕТ ПОТЕРЯН!")
            return False

        if sender == 1:
            self.messages_for_alpha2.append((channel, data))
        elif sender == 2:
            self.messages_for_alpha1.append((channel, data))
        else:
            raise ValueError("Неизвестная станция")

        return True

    # Получение пакета
    def receive(self, receiver):
        if receiver == 1:
            queue = self.messages_for_alpha1
        elif receiver == 2:
            queue = self.messages_for_alpha2
        else:
            raise ValueError("Неизвестная станция")

        if not queue:
            return None

        return queue.pop(0)

    # Имитация ACK

    def send_ack(self, sender, receiver, force_loss=False):
        print(f"\nАльфа № {receiver} отправляет ACK Альфе № {sender}")

        if force_loss or random.random() < self.ACK_LOSS:
            print("ACK ПОТЕРЯН!")
            return False

        print("ACK доставлен.")
        return True
