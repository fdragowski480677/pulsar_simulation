#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
import os

# Ścieżka do pliku z danymi i folderu wynikowego
dataFile = "../build/out.txt"
outputDir = "../pomiary_badania/"
os.makedirs(outputDir, exist_ok=True)

# Globalna stała okresu orbitalnego - dostępna dla wszystkich wykresów
TExp = 7.7519 * 3600  # Oczekiwany okres orbitalny PSR B1913+16 [s]

print("-> Wczytywanie danych...")
try:
    # skiprows=3 żeby ominąć 3 linijki nagłówka i nie mylić numpy!
    data = np.loadtxt(dataFile, comments="#", skiprows=3)
except Exception as e:
    print(f"Błąd odczytu pliku: {e}")
    exit()

t  = data[:,0]
r  = data[:,1]
v  = data[:,2]
dt = data[:,3]
E  = data[:,4]
L  = data[:,5]

try:
    x = data[:,6]
    y = data[:,7]
    has_spatial_data = True
except IndexError:
    print("\n[OSTRZEŻENIE]: Brak kolumn X i Y w pliku out.txt! (Pomijanie wykresów 2D/3D)")
    has_spatial_data = False

# --- DOPASOWANIE LINIOWE ---
fit_r_coeffs = np.polyfit(t, r, 1)
fit_r_line = np.polyval(fit_r_coeffs, t)

fit_v_coeffs = np.polyfit(t, v, 1)
fit_v_line = np.polyval(fit_v_coeffs, t)

# 1. Separacja
print("-> Generowanie: Wykres 1 (Separacja)...")
plt.figure(figsize=(8, 6))
plt.plot(t, r, color='#0072B2', label="Separacja r(t)", linewidth=1.0)
plt.plot(t, fit_r_line, color='#D55E00', label=f"Trend liniowy (a={fit_r_coeffs[0]:.2e})", linewidth=2.5, linestyle='--')
plt.xlabel("Czas [s]")
plt.ylabel("|r| [km]")
plt.title("Separacja w czasie + Dopasowanie liniowe")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(os.path.join(outputDir, "wykres_1_separacja.pdf"), format='pdf', bbox_inches='tight')
plt.close()

# 2. Prędkość
print("-> Generowanie: Wykres 2 (Prędkość)...")
plt.figure(figsize=(8, 6))
plt.plot(t, v, color='#009E73', label="Prędkość v(t)", linewidth=1.0)
plt.plot(t, fit_v_line, color='#CC79A7', label=f"Trend liniowy (a={fit_v_coeffs[0]:.2e})", linewidth=2.5, linestyle='--')
plt.xlabel("Czas [s]")
plt.ylabel("|v| [km/s]")
plt.title("Prędkość względna + Dopasowanie liniowe")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(os.path.join(outputDir, "wykres_2_predkosc.pdf"), format='pdf', bbox_inches='tight')
plt.close()

# 3. Krok adaptacyjny
print("-> Generowanie: Wykres 3 (Krok adaptacyjny)...")
plt.figure(figsize=(8, 6))
plt.semilogy(t[1:], dt[1:], color='#E69F00', linewidth=1.5, label="Krok dt")
plt.xlabel("Czas [s]")
plt.ylabel("Krok czasowy dt [s] (skala log)")
plt.title("Praca algorytmu Dormand-Prince (bez 1. kroku)")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(os.path.join(outputDir, "wykres_3_krok_czasu.pdf"), format='pdf', bbox_inches='tight')
plt.close()

# 4. Ubytek energii
print("-> Generowanie: Wykres 4 (Ubytek energii)...")
plt.figure(figsize=(8, 6))
delta_E = E - E[0]
window = min(279, len(delta_E))
if window > 1:
    smoothed_E = np.convolve(delta_E, np.ones(window)/window, mode='valid')
    t_smoothed = t[window-1:]
    plt.plot(t_smoothed, smoothed_E, color='#800000', linewidth=3.0, label="Średni ubytek energii (Fale Grawitacyjne)")
plt.plot(t, delta_E, color='#d62728', alpha=0.15, label="Surowe ΔE")
plt.xlabel("Czas [s]")
plt.ylabel("ΔE")
plt.title("Ubytek energii mechanicznej w czasie (Przefiltrowany)")
plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(os.path.join(outputDir, "wykres_4_ubytek_energii.pdf"), format='pdf', bbox_inches='tight')
plt.close()

if has_spatial_data:
    # 5. Precesja
    print("-> Generowanie: Wykres 5 (Precesja)...")
    t_now = t[0]
    peaks = []

    while (t_now + TExp < t[-1]):
        tUp = min(t_now + 1.5*TExp, t[-1])
        start_idx = int(np.argmax(t > t_now + TExp/2))
        end_idx   = int(np.argmax(t >= tUp))
        if end_idx <= start_idx: break

        seg = r[start_idx:end_idx]
        minIdx = int(np.argmin(seg))
        peaks.append(start_idx + minIdx)
        t_now = t[start_idx + minIdx]

    peaks = np.array(peaks)

    if len(peaks) > 1:
        t_per = t[peaks]
        angles_rad = np.unwrap(np.arctan2(y[peaks], x[peaks]))
        angles_arcsec = np.degrees(angles_rad) * 3600.0
        fit_prec = np.polyfit(t_per, angles_arcsec, 1)
        line_prec = np.polyval(fit_prec, t_per)

        plt.figure(figsize=(8, 6))
        plt.plot(t_per, angles_arcsec, 'ko', markersize=4, label="Położenie peryastronu")
        plt.plot(t_per, line_prec, color='red', linewidth=2.0, linestyle='--', label=f"Trend liniowy (a={fit_prec[0]:.2e} ''/s)")
        plt.xlabel("Czas [s]")
        plt.ylabel("Położenie kątowe peryastronu ['']")
        plt.title("Precesja peryastonów w czasie (Metoda Oknowa)")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig(os.path.join(outputDir, "wykres_5_precesja.pdf"), format='pdf', bbox_inches='tight')
        plt.close()

    # 6. Orbita względna 2D
    print("-> Generowanie: Wykres 6 (Orbita względna XY)...")
    plt.figure(figsize=(8, 8))
    plt.plot(x, y, color='blue', linewidth=0.5, alpha=0.8, label="Orbita wzajemna")
    plt.scatter([0], [0], color='red', marker='*', s=150, zorder=5, label="Ognisko")
    plt.xlabel("Położenie x [km]")
    plt.ylabel("Położenie y [km]")
    plt.title("Względna orbita ciał w płaszczyźnie")
    plt.axis('equal')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.savefig(os.path.join(outputDir, "wykres_6_orbita_wzgledna.pdf"), format='pdf', bbox_inches='tight')
    plt.close()

    # 8. Orbita obu ciał wokół środka masy (Barycentrum)
    print("-> Generowanie: Wykres 8 (Orbity Barycentryczne)...")
    m1, m2 = 1.387, 1.441
    M_total = m1 + m2
    x1, y1 = (m2 / M_total) * x, (m2 / M_total) * y
    x2, y2 = -(m1 / M_total) * x, -(m1 / M_total) * y

    plt.figure(figsize=(8, 8))
    plt.plot(x1, y1, color='purple', linewidth=0.6, alpha=0.8, label=f"Pulsar 1 (m={m1} Mo)")
    plt.plot(x2, y2, color='orange', linewidth=0.6, alpha=0.8, label=f"Pulsar 2 (m={m2} Mo)")
    plt.scatter([0], [0], color='black', marker='+', s=100, zorder=5, label="Barycentrum (Środek Masy)")
    plt.xlabel("Położenie x [km]")
    plt.ylabel("Położenie y [km]")
    plt.title("Rzeczywiste orbity pulsarów wokół środka masy")
    plt.axis('equal')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.savefig(os.path.join(outputDir, "wykres_8_orbity_barycentrum.pdf"), format='pdf', bbox_inches='tight')
    plt.close()

    # 9. Orbita 3D z perspektywy
    print("-> Generowanie: Wykres 9 (Orbita 3D perspektywa)...")
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    z1, z2 = np.zeros_like(x1), np.zeros_like(x2)
    step_3d = max(1, len(x1) // 5000)
    ax.plot(x1[::step_3d], y1[::step_3d], z1[::step_3d], color='purple', linewidth=0.8, label=f"Pulsar 1")
    ax.plot(x2[::step_3d], y2[::step_3d], z2[::step_3d], color='orange', linewidth=0.8, label=f"Pulsar 2")
    ax.scatter([0], [0], [0], color='black', marker='+', s=100, label="Barycentrum")
    ax.view_init(elev=25, azim=-45)
    ax.set_xlabel('Położenie X [km]')
    ax.set_ylabel('Położenie Y [km]')
    ax.set_zlabel('Położenie Z [km]')
    ax.set_title('Układ podwójny z perspektywy 3D (Z = 0)')
    max_val = max(np.max(np.abs(x1)), np.max(np.abs(x2)), np.max(np.abs(y1)), np.max(np.abs(y2)))
    limit = max_val * 1.15
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)
    ax.set_box_aspect([1, 1, 1])
    ax.legend()
    plt.savefig(os.path.join(outputDir, "wykres_9_orbita_3D_perspektywa.pdf"), format='pdf', bbox_inches='tight')
    plt.close()

# 7. Błąd energii
print("-> Generowanie: Wykres 7 (Błąd energii)...")
plt.figure(figsize=(8, 6))
E_0 = E[0] if E[0] != 0 else 1e-10
relative_energy_error = np.abs((E - E_0) / E_0)
plt.plot(t, relative_energy_error, color='black', linewidth=0.5)
plt.xlabel("Czas [s]")
plt.ylabel("Względny błąd energii |(E - E0) / E0|")
plt.title("Względny błąd zachowania energii (DP5(4))")
plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(os.path.join(outputDir, "wykres_7_blad_energii_wzgledny.pdf"), format='pdf', bbox_inches='tight')
plt.close()

# 10. Skumulowane przesunięcie periastronu
print("-> Generowanie: Wykres 10 (Skumulowane przesunięcie czasu periastronu)...")
times_of_min = [t[0]]
t_current = 0.0
end_time = t[-1]

while (t_current + TExp < end_time):
    t_up = min(t_current + 1.5 * TExp, end_time)
    start_index = int(np.argmax(t > t_current + TExp / 2))
    end_index = int(np.argmax(t >= t_up))
    if end_index <= start_index: break
    seg = r[start_index:end_index]
    min_idx = int(np.argmin(seg))
    time_of_min = float(t[start_index + min_idx])
    times_of_min.append(time_of_min)
    t_current = time_of_min

if len(times_of_min) > 2:
    T0 = times_of_min[1] - times_of_min[0]
    t0 = times_of_min[0]
    shifts = [t_n - (t0 + n * T0) for n, t_n in enumerate(times_of_min)]
    years = [t_n / (365.25 * 24 * 3600) for t_n in times_of_min]

    plt.figure(figsize=(9, 6))
    plt.plot(years, shifts, 'ro', markersize=4, label='Dane z symulacji (DP5)')
    plt.plot(years, shifts, 'b-', linewidth=1.5, alpha=0.7, label='Trend ewolucyjny (2.5PN)')
    plt.xlabel('Czas od początku symulacji [lata]')
    plt.ylabel('Skumulowane przesunięcie czasu periastronu [s]')
    plt.title('Skumulowane przesunięcie fazy orbitalnej układu Hulse-Taylora')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='lower left')
    plt.savefig(os.path.join(outputDir, "wykres_10_skumulowane_przesuniecie_periastronu.pdf"), format='pdf', bbox_inches='tight')
    plt.close()
