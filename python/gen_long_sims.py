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
import subprocess
import re

YEAR = 31557600.0  # Rok w sekundach

def set_v0y(val):
    path = "../src/main.cpp"
    with open(path, "r", encoding="utf-8") as f: content = f.read()
    content = re.sub(r'(/\*v0y\*/\s*)[0-9.]+(,)', fr'\g<1>{val}\g<2>', content)
    with open(path, "w", encoding="utf-8") as f: f.write(content)

def run():
    print("\n>>> Generowanie danych z ekstremalnie długich symulacji <<<")
    set_v0y("901.6")
    subprocess.run(["cmake", "--build", "."], cwd="../build", check=True)
    
    # -------------------------------------------------------------
    # A) Precesja peryastronów (1000 lat) - Tryb zachowawczy 1PN+2PN
    # -------------------------------------------------------------
    print("-> 1/3: Symulacja 1000 lat precesji (Brak dyssypacji)...")
    t_prec = str(1000 * YEAR)
    with open("../build/out_precesja.txt", "w") as out:
        # Czas, dt=100.0, zapis co 30 dni (2592000s), to2PN=1
        subprocess.run(["./main", t_prec, "100.0", "2592000", "1"], cwd="../build", stdout=out)

    # -------------------------------------------------------------
    # B) Skumulowany Shift (500 lat) - Tryb 2.5PN
    # -------------------------------------------------------------
    print("-> 2/3: Symulacja 500 lat opóźnienia fazy (Dyssypacja 2.5PN)...")
    t_shift = str(500 * YEAR)
    with open("../build/out_shift.txt", "w") as out:
        # Zapiszmy co okrągły czas odpowiadający jednemu okresowi (ok. 27906s)
        subprocess.run(["./main", t_shift, "100.0", "27000", "0"], cwd="../build", stdout=out)

    # -------------------------------------------------------------
    # C) Spirala Einsteina (1 miliard lat!) - Tryb 2.5PN
    # -------------------------------------------------------------
    print("-> 3/3: Symulacja 1 MILIARD lat do kolizji obiektów...")
    t_spiral = str(1000000000 * YEAR)
    # Zapis co 10 000 lat, żeby plik tekstowy dało się w ogóle otworzyć (3.15e11 sekund)
    krok_zapisu = str(10000 * YEAR)
    with open("../build/out_spiral.txt", "w") as out:
        subprocess.run(["./main", t_spiral, "500.0", krok_zapisu, "0"], cwd="../build", stdout=out)

    print("-> Zakończono długie symulacje. Wyniki w: out_precesja.txt, out_shift.txt, out_spiral.txt")

if __name__ == "__main__":
    run()
