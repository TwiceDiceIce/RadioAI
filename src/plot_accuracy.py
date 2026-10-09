import matplotlib.pyplot as plt

names = []
accuracy = []

with open("results.txt", "r", encoding="utf-8") as file:
    for line in file:
        if "точность:" in line:
            parts = line.strip().split(" - точность: ")
            name = parts[0]
            value = float(parts[1].replace("%", ""))

            names.append(name)
            accuracy.append(value)

plt.bar(names, accuracy)

plt.title("Точность распознавания сигналов")
plt.xlabel("Тип сигнала")
plt.ylabel("Точность (%)")
plt.ylim(0, 100)

plt.show()