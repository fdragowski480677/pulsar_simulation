#!/usr/bin/python
import numpy as np
import sys

dataFile = "../build/out.txt"

try:
    data = np.loadtxt(dataFile, comments="#", skiprows=3)
except Exception as e:
    print(f"Błąd odczytu pliku: {e}")
    exit()

times     = data[:,0]
distances = data[:,1]
endTime   = times[-1]

TExp = 25000.0
t = 0.0

timesOfMin   = []
minDistances = []

# Niezawodne szukanie peryastrów metodą oknową
t_curr = times[0]
while t_curr + TExp < endTime:
    tUp = min(t_curr + 1.5*TExp, endTime)
    idx_start = np.searchsorted(times, t_curr + TExp*0.5)
    idx_end = np.searchsorted(times, tUp)
    if idx_end <= idx_start: break
    
    seg = distances[idx_start:idx_end]
    actual_idx = idx_start + int(np.argmin(seg))
    timesOfMin.append(times[actual_idx])
    minDistances.append(distances[actual_idx])
    t_curr = times[actual_idx]

arr = np.array(minDistances)
deviation = float(np.sqrt(np.mean((arr[1:] - arr[0])**2))) if len(arr) > 1 else 0.0

# Odczytujemy testowaną prędkość z argumentów wywołania skryptu
v0y = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
print(f"Deviation dla v0y={v0y}: {deviation:.6f}")

# Zapisujemy idealnie czyste 2 kolumny dla drawScan.py
with open("devs.txt", "a") as f:
    f.write(f"{v0y} {deviation}\n")

