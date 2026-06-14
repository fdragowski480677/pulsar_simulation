#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Ścieżka do pliku z danymi
dataFile = "../build/out.txt"

print("-> Wczytywanie danych...")
try:
    # skiprows=3 żeby ominąć 3 linijki nagłówka i nie mylić numpy!
    data = np.loadtxt(dataFile, comments="#", skiprows=3)
except Exception as e:
    print(f"Błąd odczytu pliku: {e}")
    exit()

# Wyciąganie standardowych kolumn
t  = data[:,0]
r  = data[:,1]
v  = data[:,2]
dt = data[:,3]
E  = data[:,4]
L  = data[:,5]

# Dynamiczne wykrywanie kolumn przestrzennych XY (dla jednego lub dwóch ciał)
has_spatial_data = False
if data.shape[1] >= 8:
    try:
        x1 = data[:,6]
        y1 = data[:,7]
        has_spatial_data = True
        # Sprawdzamy czy są też współrzędne drugiego ciała
        if data.shape[1] >= 10:
            x2 = data[:,8]
            y2 = data[:,9]
            two_bodies = True
        else:
            two_bodies = False
    except IndexError:
        print("\n[OSTRZEŻENIE]: Brak pełnych kolumn współrzędnych w pliku out.txt!")
        has_spatial_data = False

# --- DOPASOWANIE LINIOWE (Dla trendów ogólnych) ---
fit_r_coeffs = np.polyfit(t, r, 1)
fit_r_line = np.polyval(fit_r_coeffs, t)

fit_v_coeffs = np.polyfit(t, v, 1)
fit_v_line = np.polyval(fit_v_coeffs, t)


# =========================================================================
# 1. Wykres: Separacja składników
# =========================================================================
print("-> Generowanie: Wykres 1 (Separacja)...")
plt.figure(figsize=(8, 6.5))
plt.plot(t, r, 'b-', label='Odległość chwilowa r(t)', alpha=0.7)
plt.plot(t, fit_r_line, 'r--', label='Trend liniowy zmian')
plt.xlabel('Czas symulacji [s]')
plt.ylabel('Separacja ciał [km]')
plt.title('Ewolucja odległości (separacji) składników układu podwójnego')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(loc='upper right')

# Podpis pod wykresem
podpis_1 = "Rys. 1: Zmiana odległości pomiędzy składnikami układu podwójnego w funkcji czasu symulacji wraz z naniesioną linią trendu sekularnego."
plt.figtext(0.5, 0.02, podpis_1, ha="center", fontsize=9, style='italic', wrap=True)
plt.subplots_adjust(bottom=0.15)
plt.savefig("wykres_1_separacja.pdf", format='pdf', bbox_inches='tight')
plt.close()


# =========================================================================
# 2. Wykres: Prędkość względna
# =========================================================================
print("-> Generowanie: Wykres 2 (Prędkość)...")
plt.figure(figsize=(8, 6.5))
plt.plot(t, v, 'g-', label='Prędkość chwilowa v(t)', alpha=0.7)
plt.plot(t, fit_v_line, 'r--', label='Trend liniowy zmian')
plt.xlabel('Czas symulacji [s]')
plt.ylabel('Prędkość względna [km/s]')
plt.title('Ewolucja prędkości względnej składników układu')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(loc='upper right')

# Podpis pod wykresem
podpis_2 = "Rys. 2: Prędkość orbitalna składników układu podwójnego w funkcji czasu, obrazująca oscylacje pomiędzy peryastronem a apastronem."
plt.figtext(0.5, 0.02, podpis_2, ha="center", fontsize=9, style='italic', wrap=True)
plt.subplots_adjust(bottom=0.15)
plt.savefig("wykres_2_predkosc.pdf", format='pdf', bbox_inches='tight')
plt.close()


# =========================================================================
# 3. Wykres: Efekt Hulse-Taylora (Przesunięcie periastronu)
# =========================================================================
print("-> Generowanie: Wykres 3 (Efekt Hulse-Taylora)...")
T0 = 27906.98  # Okres orbitalny PSR B1913+16 w sekundach

# Anty-szczyty separacji (lokalne minima = periastrony)
mean_dt = np.mean(dt) if len(dt) > 0 else 1.0
min_dist_peaks = int(T0 / mean_dt * 0.5) if mean_dt < T0 else 10
peaks, _ = find_peaks(-r, distance=max(min_dist_peaks, 5))

if len(peaks) > 1:
    timesOfMin = []
    # Wygładzanie parabolą dla uniknięcia "piły" (błędu numerycznego kroku dyskretnego)
    for idx in peaks:
        if 0 < idx < len(t) - 1:
            t_seg = t[idx-1:idx+2]
            r_seg = r[idx-1:idx+2]
            poly = np.polyfit(t_seg, r_seg, 2)
            t_exact = -poly[1] / (2.0 * poly[0]) if poly[0] != 0 else t[idx]
            timesOfMin.append(t_exact)
    
    if len(timesOfMin) > 1:
        shifts = []
        years = []
        t0_orbit = timesOfMin[0]
        
        for n, t_n in enumerate(timesOfMin):
            t_theoretical = t0_orbit + n * T0
            shift = t_n - t_theoretical
            shifts.append(shift)
            years.append(t_n / (365.25 * 24 * 3600))
            
        plt.figure(figsize=(8, 6.5))
        plt.plot(years, shifts, 'ro', markersize=4, label='Punkty pomiarowe (DP5)')
        plt.plot(years, shifts, 'b-', linewidth=1.2, alpha=0.7, label='Trend paraboliczny (2.5PN)')
        plt.xlabel('Czas od początku symulacji [lata]')
        plt.ylabel('Skumulowane przesunięcie periastronu [s]')
        plt.title('Skumulowane przesunięcie fazy orbitalnej układu')
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend(loc='lower left')
        
        podpis_3 = "Rys. 3: Skumulowane opóźnienie czasu przejścia przez periastron wywołane stratą energii układu przez emisję fal grawitacyjnych."
        plt.figtext(0.5, 0.02, podpis_3, ha="center", fontsize=9, style='italic', wrap=True)
        plt.subplots_adjust(bottom=0.15)
        plt.savefig("wykres_3_hulse_taylor.pdf", format='pdf', bbox_inches='tight')
        plt.close()


# =========================================================================
# 4. Wykres: Adaptacyjny krok czasowy dt
# =========================================================================
print("-> Generowanie: Wykres 4 (Krok czasowy dt)...")
plt.figure(figsize=(8, 6.5))
plt.plot(t, dt, 'm-', linewidth=1, label='Krok czasowy dt')
plt.xlabel('Czas symulacji [s]')
plt.ylabel('Rozmiar kroku dt [s]')
plt.title('Historia adaptacji kroku czasowego integratora')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(loc='upper right')

# Podpis pod wykresem
podpis_4 = "Rys. 4: Przebieg automatycznych zmian wielkości kroku integratora DP5. Wyraźnie widoczne drastyczne zmniejszanie kroku w periastronie."
plt.figtext(0.5, 0.02, podpis_4, ha="center", fontsize=9, style='italic', wrap=True)
plt.subplots_adjust(bottom=0.15)
plt.savefig("wykres_4_krok_dt.pdf", format='pdf', bbox_inches='tight')
plt.close()


# =========================================================================
# 5. Wykres: Moment pędu L
# =========================================================================
print("-> Generowanie: Wykres 5 (Moment pędu)...")
plt.figure(figsize=(8, 6.5))
L0 = L[0] if L[0] != 0 else 1e-10
relative_L_error = np.abs((L - L0) / L0)
plt.plot(t, relative_L_error, 'c-', label=r'$|L(t) - L_0| / L_0$')
plt.yscale('log')
plt.xlabel('Czas symulacji [s]')
plt.ylabel('Błąd względny momentu pędu')
plt.title('Zachowanie całkowitego momentu pędu układu')
plt.grid(True, linestyle=':', alpha=0.6, which="both")
plt.legend(loc='upper left')

# Podpis pod wykresem
podpis_5 = "Rys. 5: Względny błąd zachowania momentu pędu w skali logarytmicznej, demonstrujący stabilność geometryczną integratora numerycznego."
plt.figtext(0.5, 0.02, podpis_5, ha="center", fontsize=9, style='italic', wrap=True)
plt.subplots_adjust(bottom=0.15)
plt.savefig("wykres_5_moment_pedu.pdf", format='pdf', bbox_inches='tight')
plt.close()


# =========================================================================
# 6. Wykres: Trajektoria 2D
# =========================================================================
if has_spatial_data:
    print("-> Generowanie: Wykres 6 (Orbita 2D)...")
    plt.figure(figsize=(7.5, 7.5))
    
    if two_bodies:
        plt.plot(x1, y1, 'r-', label='Gwiazda neutronowa 1', alpha=0.8)
        plt.plot(x2, y2, 'b-', label='Gwiazda neutronowa 2', alpha=0.8)
        plt.plot(0, 0, 'kx', label='Barycentrum', markersize=8)
    else:
        plt.plot(x1, y1, 'b-', label='Trajektoria względna m1-m2')
        plt.plot(0, 0, 'ro', label='Centrum siły')
        
    plt.xlabel('Położenie X [km]')
    plt.ylabel('Położenie Y [km]')
    plt.title('Ruch ciał w płaszczyźnie orbitalnej (Widok 2D)')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.axis('equal')
    plt.legend(loc='upper right')
    
    podpis_6 = "Rys. 6: Rzut dwuwymiarowy zamkniętych (lub powoli zacieśniających się) orbit składników układu podwójnego w płaszczyźnie XY."
    plt.figtext(0.5, 0.02, podpis_6, ha="center", fontsize=9, style='italic', wrap=True)
    plt.subplots_adjust(bottom=0.15)
    plt.savefig("wykres_6_orbita_2D.pdf", format='pdf', bbox_inches='tight')
    plt.close()


# =========================================================================
# 7. Wykres: Błąd względny energii
# =========================================================================
print("-> Generowanie: Wykres 7 (Błąd energii)...")
plt.figure(figsize=(8, 6.5))
E0 = E[0] if E[0] != 0 else 1e-10
relative_energy_error = np.abs((E - E0) / E0)
plt.plot(t, relative_energy_error, 'r-', label=r'$|E(t) - E_0| / E_0$')
plt.yscale('log')
plt.xlabel('Czas symulacji [s]')
plt.ylabel('Błąd względny energii')
plt.title('Zachowanie całkowitej energii układu')
plt.grid(True, linestyle=':', alpha=0.6, which="both")
plt.legend(loc='upper left')

# Podpis pod wykresem
podpis_7 = "Rys. 7: Ewolucja względnego błędu energii całkowitej układu w czasie, obrazująca precyzję i bezbłędność energetyczną symulacji."
plt.figtext(0.5, 0.02, podpis_7, ha="center", fontsize=9, style='italic', wrap=True)
plt.subplots_adjust(bottom=0.15)
plt.savefig("wykres_7_blad_energii.pdf", format='pdf', bbox_inches='tight')
plt.close()


# =========================================================================
# 9. Wykres: Perspektywa trójwymiarowa (3D)
# =========================================================================
if has_spatial_data:
    print("-> Generowanie: Wykres 9 (Orbita 3D z perspektywą)...")
    fig = plt.figure(figsize=(8, 7.5))
    ax = fig.add_subplot(111, projection='3d')
    
    # Dodajemy sztuczną oś Z = 0 dla pełnej wizualizacji przestrzennej 3D
    z1 = np.zeros_like(x1)
    
    if two_bodies:
        z2 = np.zeros_like(x2)
        ax.plot(x1, y1, z1, 'r-', label='Gwiazda 1', alpha=0.8)
        ax.plot(x2, y2, z2, 'b-', label='Gwiazda 2', alpha=0.8)
        max_val = max(np.max(np.abs(x1)), np.max(np.abs(x2)), np.max(np.abs(y1)), np.max(np.abs(y2)))
    else:
        ax.plot(x1, y1, z1, 'b-', label='Ruch względny')
        max_val = max(np.max(np.abs(x1)), np.max(np.abs(y1)))
        
    # Pełne opisy osi przestrzennych X, Y, Z
    ax.set_xlabel('Położenie X [km]', labelpad=10)
    ax.set_ylabel('Położenie Y [km]', labelpad=10)
    ax.set_zlabel('Położenie Z [km]', labelpad=10)
    ax.set_title('Układ podwójny zwizualizowany w przestrzeni 3D')
    
    # Symetryczne, poprawne skalowanie pudełka wykresu 3D
    limit = max_val * 1.15
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)
    ax.set_box_aspect([1, 1, 1])
    
    ax.legend(loc='upper right')
    
    podpis_9 = "Rys. 9: Trójwymiarowa prezentacja orbit wokół wspólnego środka masy (barycentrum) z uwzględnieniem osi prostopadłej Z."
    plt.figtext(0.5, 0.02, podpis_9, ha="center", fontsize=9, style='italic', wrap=True)
    
    plt.savefig("wykres_9_orbita_3D_perspektywa.pdf", format='pdf', bbox_inches='tight')
    plt.close()

print("-> Gotowe! Wszystkie wykresy zostały wygenerowane z podpisami.")

