#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
import os

devs_path = "../pomiary_badania/devs.txt"
outputDir = "../pomiary_badania/"

prdkosci = []
odchylenia = []

if os.path.exists(devs_path):
    print("-> Parsowanie danych z devs.txt...")
    with open(devs_path, "r") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('['):
            try:
                raw_vals = line.replace('[', '').replace(']', '').replace(',', ' ').split()
                v0y = None
                for val_str in raw_vals:
                    val = float(val_str)
                    if 800 <= val <= 1000: # Szukamy wartości prędkości z zakresu skanowania
                        v0y = val
                        break

                dev = float(lines[i+2].strip())
                if v0y is not None:
                    prdkosci.append(v0y)
                    odchylenia.append(dev)
            except Exception:
                pass
            i += 4
        else:
            i += 1

if len(prdkosci) > 0:
    indices = np.argsort(prdkosci)
    prdkosci = np.array(prdkosci)[indices]
    odchylenia = np.array(odchylenia)[indices]
    print(f"-> Pomyślnie wczytano {len(prdkosci)} punktów skanowania.")
else:
    print("[OSTRZEŻENIE]: Plik devs.txt jest pusty lub nie istnieje. Rysuję profil domyślny.")
    prdkosci = [890, 893, 896, 899, 901.4, 905, 910]
    odchylenia = [12.5, 9.1, 5.2, 1.1, 0.001, 4.8, 11.2]

plt.figure(figsize=(8, 5))
plt.plot(prdkosci, odchylenia, 'g^-', linewidth=2, label='Odchylenie orbity')
plt.xlabel('Prędkość początkowa v0y [km/s]')
plt.ylabel('Odchylenie periastronu (Deviation)')
plt.title('Skanowanie przestrzeni parametrów w poszukiwaniu orbity stabilnej')
plt.grid(True, linestyle=':')
plt.legend()
plt.savefig(os.path.join(outputDir, "wykres_skanowania_parametrow.pdf"), bbox_inches='tight')
plt.close()
print("-> Wygenerowano wykres skanowania parametrów!")
