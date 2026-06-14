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
with open(devs_file_path, "a") as f:
    print(paramRow, file=f)
    print(len(minDistances), file=f)
    print(deviation, "\n", file=f)
