"""
  * Copyright (c) 2026 [Franciszek Jan Drągowski]
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

#!/usr/bin/python
import os
import shutil
import subprocess
import numpy as np
import matplotlib.pyplot as plt

cpp_file = "../src/Simulation.cpp"
backup_file = "../src/Simulation.cpp.bak"
output_plot = "../pomiary_badania/slynna_parabola_weizberga.pdf"
out_data_file = "../build/out_parabola.txt"

os.makedirs("../pomiary_badania", exist_ok=True)

if not os.path.exists(cpp_file):
    print(f"Błąd: Nie znaleziono pliku {cpp_file}!")
    exit(1)

shutil.copyfile(cpp_file, backup_file)

try:
    with open(cpp_file, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("A25 /= c*c*c*c*c;", "A25 /= c*c*c*c*c;\n        A25 *= 1.0e5; // Tymczasowe wzmocnienie")
    content = content.replace("B25 /= c*c*c*c*c;", "B25 /= c*c*c*c*c;\n        B25 *= 1.0e5; // Tymczasowe wzmocnienie")

    with open(cpp_file, "w", encoding="utf-8") as f:
        f.write(content)

    compile_cmd = "g++ -O2 -I../inc ../src/main.cpp ../src/Simulation.cpp ../src/Vector.cpp -o ../build/main_sim"
    subprocess.run(compile_cmd, shell=True, check=True)

    run_cmd = "../build/main_sim 1500000 1.0 10.0 0 > " + out_data_file
    subprocess.run(run_cmd, shell=True, check=True)

except Exception as e:
    print(f"[BŁĄD]: {e}")
    if os.path.exists(backup_file): shutil.move(backup_file, cpp_file)
    exit(1)

finally:
    if os.path.exists(backup_file): shutil.move(backup_file, cpp_file)

t_list, r_list = [], []
if os.path.exists(out_data_file):
    with open(out_data_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith('#'): continue
            cols = line.split()
            if len(cols) >= 2:
                t_list.append(float(cols[0]))
                r_list.append(float(cols[1]))

if not t_list: exit(1)
t = np.array(t_list)
r = np.array(r_list)

peri_times = []
for i in range(1, len(r) - 1):
    if r[i] < r[i-1] and r[i] < r[i+1]:
        poly = np.polyfit(t[i-1:i+2], r[i-1:i+2], 2)
        t_min = -poly[1] / (2 * poly[0])
        peri_times.append(t_min)

peri_times = np.array(peri_times)
N_orbits = len(peri_times)

if N_orbits < 3: exit(1)

P0 = peri_times[1] - peri_times[0]
t_kepler = peri_times[0] + np.arange(N_orbits) * P0
delta_T = peri_times - t_kepler

plt.figure(figsize=(10, 6))
plt.plot(np.arange(N_orbits), delta_T * 1000, 'ro-', markersize=4, label='Wynik symulacji (wzmocnienie 2.5PN $10^5$)')
p_fit = np.polyfit(np.arange(N_orbits), delta_T * 1000, 2)
plt.plot(np.arange(N_orbits), np.polyval(p_fit, np.arange(N_orbits)), 'k--', alpha=0.5, label='Teoretyczna parabola')

plt.xlabel('Liczba orbit')
plt.ylabel(r'Skumulowane przesunięcie czasu periastronu $\Delta T_p$ [ms]')
plt.title('Skumulowane przesunięcie fazy orbitalnej układu')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()
plt.savefig(output_plot, dpi=300)
