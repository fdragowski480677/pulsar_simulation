#!/usr/bin/python
import os
import subprocess
import re

OUTPUT_DIR = "../pomiary_badania"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def set_v0y(val):
    path = "../src/main.cpp"
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f: content = f.read()
    content = re.sub(r'(/\*v0y\*/\s*)[0-9.]+(,)', fr'\g<1>{val}\g<2>', content)
    with open(path, "w", encoding="utf-8") as f: f.write(content)

def main():
    print("=========================================================")
    print("URUCHAMIANIE KOMPLETNEGO PROCESU BADAWCZEGO")
    print("=========================================================")

    # 1. Czyszczenie starego pliku skanowania
    devs_path = os.path.join(OUTPUT_DIR, "devs.txt")
    if os.path.exists(devs_path): os.remove(devs_path)

    # Gęsta lista prędkości z Twojego pierwszego pytania
    velocities = ["890.0", "893.0", "896.0", "898.0", "899.0", "900.0",
                  "901.0", "901.4", "902.0", "903.0", "904.0", "905.0", "910.0"]

    print("\n[KROK 1/3] Skanowanie prędkości v0y (Poszukiwanie orbity stabilnej)...")
    for v in velocities:
        print(f" -> Przetwarzanie v0y = {v} km/s...")
        set_v0y(v)
        subprocess.run(["cmake", "--build", "."], cwd="../build", stdout=subprocess.DEVNULL, check=True)

        with open("../build/out.txt", "w") as out:
            # Skanowanie robimy na krótszym dystansie (150k s, włączone 1PN+2PN, to2PN=1)
            subprocess.run(["./main", "150000", "1.0", "0.0", "1"], cwd="../build", stdout=out, check=True)

        subprocess.run(["python3", "getMinsAndDev.py"])

    # Generowanie wykresu profilu odchyleń
    subprocess.run(["python3", "drawScan.py"])

    # 2. Główna symulacja fizyczna dla stabilnej prędkości
    print("\n[KROK 2/3] Generowanie długiej trajektorii referencyjnej (v0y = 901.4 km/s)...")
    set_v0y("901.4")
    subprocess.run(["cmake", "--build", "."], cwd="../build", stdout=subprocess.DEVNULL, check=True)

    with open("../build/out.txt", "w") as out:
        # 1.5 miliona sekund symulacji (ponad 50 orbit) z włączoną dyssypacją fali (to2PN=0)
        subprocess.run(["./main", "1500000", "1.0", "0.0", "0"], cwd="../build", stdout=out, check=True)

    # 3. Wywołanie skryptów analitycznych i rysujących
    print("\n[KROK 3/3] Wywoływanie Twojej biblioteki wykresów...")
    subprocess.run(["python3", "getMins.py"])
    subprocess.run(["python3", "draw.py"])

    print("\n=========================================================")
    print(f"SUKCES! Wszystkie pliki (.pdf oraz devs.txt) są w: {os.path.abspath(OUTPUT_DIR)}")
    print("=========================================================")

if __name__ == "__main__":
    main()
