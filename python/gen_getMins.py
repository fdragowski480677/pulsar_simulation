#!/usr/bin/python
import subprocess
import re

def set_v0y(val):
    path = "../src/main.cpp"
    with open(path, "r", encoding="utf-8") as f: content = f.read()
    content = re.sub(r'(/\*v0y\*/\s*)[0-9.]+(,)', fr'\g<1>{val}\g<2>', content)
    with open(path, "w", encoding="utf-8") as f: f.write(content)

def run():
    print("\n>>> Generowanie danych pod getMins (Krótki spadek orbity) <<<")
    set_v0y("901.6")
    subprocess.run(["cmake", "--build", "."], cwd="../build", check=True)
    
    print("-> Obliczenia w C++ (To może chwilę potrwać)...")
    with open("../build/out.txt", "w") as out:
        # Czas=1500000, dt=1.0, krok=0.0 (gęsto), to2PN=0 (dyssypacja 2.5PN)
        subprocess.run(["./main", "1500000", "1.0", "0.0", "0"], cwd="../build", stdout=out, check=True)
    
    print("-> Uruchamiam Twoje skrypty z biblioteki...")
    subprocess.run(["python3", "getMins.py"])
    # Wywołuje z Twojego draw.py tylko te wykresy, które pokazują spadek (np. 1, 4, 10)
    subprocess.run(["python3", "draw.py", "1", "4", "10"])

if __name__ == "__main__":
    run()

