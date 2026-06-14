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
    with open(devs_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                prdkosci.append(float(parts[0]))
                odchylenia.append(float(parts[1]))

if len(prdkosci) > 0:
    indices = np.argsort(prdkosci)
    prdkosci = np.array(prdkosci)[indices]
    odchylenia = np.array(odchylenia)[indices]
    print(f"-> Pomyślnie wczytano {len(prdkosci)} punktów skanowania.")
else:
    print("[OSTRZEŻENIE]: Plik devs.txt jest pusty lub nie istnieje.")

plt.figure(figsize=(8, 5))
plt.plot(prdkosci, odchylenia, 'bo-', linewidth=2, markersize=8)
plt.title('Profil odchyleń separacji orbity')
plt.xlabel('Prędkość początkowa v0y [km/s]')
plt.ylabel('Odchylenie periastronu (Deviation)')
plt.grid(True, linestyle='--', alpha=0.7)

out_file = os.path.join(outputDir, "wykres_skanowania_parametrow.pdf")
plt.savefig(out_file, format='pdf', bbox_inches='tight')
plt.close()
print("-> Wygenerowano wykres skanowania parametrów!")
