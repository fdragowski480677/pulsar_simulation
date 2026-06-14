#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt

dataFile = "../build/out.txt"
data = np.loadtxt(dataFile, comments="#", skiprows=3)

times = data[:,0]; distances = data[:,1]
endTime = times[-1]; TExp = 25000.0

timesOfMin = []; minDistances = []
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

timeDiffs = [timesOfMin[i+1] - timesOfMin[i] for i in range(len(timesOfMin)-1)]

if len(timeDiffs) > 0:
    plt.figure(figsize=(8, 5))
    orbity = range(1, len(timeDiffs) + 1)
    plt.plot(orbity, timeDiffs, 'ro-', linewidth=1.5, label='Zmierzony okres')
    
    # Naprawiona linia referencyjna - teraz to DOKŁADNIE pierwszy zmierzony okres z symulacji!
    T_ref = timeDiffs[0]
    plt.axhline(y=T_ref, color='k', linestyle='--', alpha=0.5, label=f'Okres referencyjny ({T_ref:.2f} s)')
    
    plt.xlabel('Numer orbity'); plt.ylabel('Okres orbitalny [s]')
    plt.title('Skracanie okresu orbitalnego (emisja fal grawitacyjnych)')
    plt.grid(True, linestyle='--', alpha=0.6); plt.legend()
    plt.savefig("wykres_getMins_okresy.pdf", bbox_inches='tight')

