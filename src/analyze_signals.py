import numpy as np
carrier = np.load("data/synthetic/carrier.npy")
bpsk = np.load("data/synthetic/bpsk.npy")
qpsk = np.load("data/synthetic/qpsk.npy")

print("Carrier power: ", np.mean(np.abs(carrier)**2))
print("BPSK power: ", np.mean(np.abs(bpsk)**2))
print("QPSK power: ", np.mean(np.abs(qpsk)**2))


print("Carrier amplitude:", np.mean(np.abs(carrier)))
print("BPSK amplitude:", np.mean(np.abs(bpsk)))
print("QPSK amplitude:", np.mean(np.abs(qpsk)))

carrier_spectrum = np.abs(np.fft.fft(carrier))
bpsk_spectrum = np.abs(np.fft.fft(bpsk))
qpsk_spectrum = np.abs(np.fft.fft(qpsk))

print("Carrier peak:", np.argmax(carrier_spectrum))
print("BPSK peak:", np.argmax(bpsk_spectrum))
print("QPSK peak:", np.argmax(qpsk_spectrum))

print("\nГотово: характеристики рассчитаны.")