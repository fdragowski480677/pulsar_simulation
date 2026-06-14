#!/usr/bin/python
import os
import subprocess
import re

def set_v0y(val):
    path = "../src/main.cpp"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # Bezpieczna podmiana /*v0y*/ w C++
    content = re.sub(r'(/\*v0y\*/\s*)[0-9.]+(,)', fr'\g<1>{val}\g<2>', content)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def run():
    print("\n>>> Generowanie danych pod getMinsAndDevs (Skanowanie v0y) <<<")
    velocities = ["890.0", "893.0", "896.0", "898.0", "899.0", "900.0", 
                  "901.0", "901.4", "902.0", "903.0", "904.0", "905.0", 
                  "906.0", "908.0", "910.0"]
    
    if os.path.exists("devs.txt"):
        os.remove("devs.txt")
        
    for v in velocities:
        print(f"-> Test dla v0y = {v} km/s...")
        set_v0y(v)
        subprocess.run(["cmake", "--build", "."], cwd="../build", check=True)
        
        with open("../build/out.txt", "w") as out:
            # Parametry: Czas=150000, dt=1.0, krok=0.0 (zapis co krok), to2PN=1
            subprocess.run(["./main", "150000", "1.0", "0.0", "1"], cwd="../build", stdout=out, check=True)
            
        # Przekazujemy prędkość do Twojego skryptu
        subprocess.run(["python3", "getMinsAndDev.py", v])
        
    print("-> Uruchamiam drawScan.py...")
    subprocess.run(["python3", "drawScan.py"])

if __name__ == "__main__":
    run()

