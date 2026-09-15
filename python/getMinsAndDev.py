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
import numpy as np
import os

dataFile = "../build/out.txt"
outputDir = "../pomiary_badania/"
os.makedirs(outputDir, exist_ok=True)

# Pancerne, bezbłędne czytanie parametrów i danych bez wywoływania UserWarning z loadtxt
paramRow = []
lines_data = []

with open(dataFile, "r", encoding="utf-8") as f:
    for line in f:
        clean_line = line.strip()
        if clean_line.startswith("#") or not clean_line:
            continue
        # Pierwsza linia bez '#' to parametry symulacji
        if len(paramRow) == 0:
            paramRow = [float(x) for x in clean_line.split()]
        else:
            lines_data.append([float(x) for x in clean_line.split()])

data = np.array(lines_data)
times     = data[:,0]
distances = data[:,1]
endTime   = times[-1]

TExp = 7.7519 * 3600
t = 0.0

timesOfMin   = [times[0]]
minDistances = [distances[0]]

while (t + TExp < endTime):
    tUp = min(t + 1.5*TExp, endTime)
    start_index = int(np.argmax(times > t + TExp/2))
    end_index   = int(np.argmax(times >= tUp))
    if end_index <= start_index: break

    seg = distances[start_index:end_index]
    minIdx = int(np.argmin(seg))
    minDistance = float(seg[minIdx])
    timeOfMin   = float(times[start_index + minIdx])

    timesOfMin.append(timeOfMin)
    minDistances.append(minDistance)
    t = timeOfMin

arr = np.array(minDistances)
deviation = float(np.sqrt(np.mean((arr[1:] - arr[0])**2))) if len(arr) > 1 else 0.0

# Zapis do poprawnego folderu pomiarów (ścieżka zsynchronizowana z drawScan.py)
devs_file_path = os.path.join(outputDir, "devs.txt")
with open(devs_file_path, "a", encoding="utf-8") as f_out:
    v0y = paramRow[2] # Indeks 2 to prędkość początkowa z Twojego main.cpp
    f_out.write(f"{v0y} {deviation}\n")
