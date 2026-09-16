"""
  * Copyright (c) 2026 Franciszek Jan Drągowski, Paweł Sajdak
  *
  * This program is free software: you can redistribute it and/or modify
  * it under the terms of the GNU General Public License as published by
  * the Free Software Foundation, either version 3 of the License, or
  * (at your option) any later version.
  *
  * This program is distributed in the hope that it will be useful,
  * but WITHOUT ANY WARRANTY; without even the implied warranty of
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  * GNU General Public License for more details.
  *
  * You should have received a copy of the GNU General Public License
  * along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import os

# Program do analizy wyników symulacji z dużego pliku (2GB)
# Oblicza rzeczywistą odległość ze współrzędnych x i y, 
# unikając ładowania całego pliku do pamięci RAM naraz.

outputDir = "plots"
dataDir = "../build/"
fileName = "out.txt"

# Upewnienie się, że folder wyjściowy istnieje
os.makedirs(outputDir, exist_ok=True)

filePath = os.path.join(dataDir, fileName)

times = []
distances = []

print(f"Wczytywanie i przetwarzanie pliku {fileName} (to może chwilę potrwać)...")

# Wczytywanie linijka po linijce zapewnia niskie zużycie RAM
with open(filePath, 'r') as file:
    # Pominięcie 3 pierwszych wierszy informacyjnych
    for _ in range(3):
        next(file)
        
    for line in file:
        parts = line.split()
        if len(parts) >= 8:
            # Kolumna 0: Czas
            t = float(parts[0])
            # Kolumna 6: Położenie x
            x = float(parts[6])
            # Kolumna 7: Położenie y
            y = float(parts[7])
            
            times.append(t)
            # Obliczenie odległości z twierdzenia Pitagorasa
            distances.append(np.sqrt(x**2 + y**2))

# Konwersja na szybkie tablice numpy
times = np.array(times)
distances = np.array(distances)

# Początkowa odległość obliczona na podstawie pierwszej linijki danych
r_0 = distances[0]
print(f"Zanotowana odległość początkowa r_0: {r_0:.4f} km")

# Przeskalowanie czasów (np. na miliardy sekund)
times_scaled = times * 1.e-9

# Odchylenia odległości od wartości początkowej
distanceDevs = distances - r_0

########## Rysowanie #####################
# Dla pliku 2GB (ok. 16.6 mln linii) n=10 dałoby zbyt wielki plik PDF. 
# Zwiększamy n, aby narysować rozsądną liczbę punktów.
n = 1000
print(f"Generowanie wykresu (wykorzystanie co {n}-tego punktu)...")

fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(times_scaled[::n], distanceDevs[::n], s=0.1, color='darkorange', label='Odchylenie od r_0')
ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)

ax.set_xlabel(r'Czas [$10^9$ s]', fontsize=12)
ax.set_ylabel(r'Odchylenie separacji [km]', fontsize=12)

# Jeśli chcesz wymusić stałe limity osi Y jak w poprzednim skrypcie, odkomentuj linię niżej:
# ax.set_ylim(-0.005, 0.001)

ax.set_title('Zmiany separacji obiektów względem początkowej wartości r_0', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(fontsize=14, markerscale=30.0, loc='center right')

# Zapis wykresu
outputFile = os.path.join(outputDir, fileName[:-4] + "_analiza.pdf")
fig.savefig(outputFile, bbox_inches='tight')
plt.close()

print(f"Wykres zapisany pomyślnie jako: {outputFile}")
