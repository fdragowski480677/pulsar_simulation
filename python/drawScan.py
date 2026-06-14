#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
import os

dataFile = "devs.txt"

if not os.path.exists(dataFile):
    print(f"[BŁĄD]: Plik {dataFile} nie istnieje! Uruchom najpierw runExperiments.sh")
    exit()

print(f"-> Wczytywanie wyników skanowania z {dataFile}...")
try:
    data = np.loadtxt(dataFile)
    if data.ndim == 1:
        data = np.atleast_2d(data)
except Exception as e:
    print(f"Błąd wczytywania pliku: {e}")
    exit()

# Sortujemy wyniki według prędkości początkowej (kolumna 0),
# aby punkty na wykresie łączyły się w logiczną krzywą
data = data[data[:, 0].argsort()]

velocities = data[:, 0]
deviations = data[:, -1]  # Ostatnia kolumna to obliczone odchylenie (deviation)

plt.figure(figsize=(9, 6))
plt.plot(velocities, deviations, 'g^-', linewidth=2, markersize=6, label='Odchylenie od orbity zamkniętej')
plt.plot(velocities, deviations, 'ro', markersize=4)  # Wyraźne kropki dla każdego punktu

plt.xlabel('Prędkość początkowa v0y [km/s]', fontsize=11)
plt.ylabel('Odchylenie periastronu (Deviation)', fontsize=11)
plt.title('Profil optymalizacji: Skanowanie przestrzeni parametrów v0y', fontsize=12, pad=15)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(loc='upper right')

plt.savefig("wykres_skanowania_parametrow.pdf", bbox_inches='tight')
plt.close()
print(f"-> Sukces! Wygenerowano wykres skanowania z {len(velocities)} punktów pomiarowych.")

