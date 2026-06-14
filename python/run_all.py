#!/usr/bin/python
import gen_scan
import gen_getMins
import gen_long_sims

def main():
    print("=========================================================")
    print("AUTOMATYCZNY ZARZĄDCA SYMULACJI (Wersja Python)")
    print("=========================================================")
    
    # Krok 1: Wykonuje badanie stabilności i odchylenia
    gen_scan.run()
    
    # Krok 2: Generuje precyzyjne dane grawitacyjne dla standardowego czasu
    gen_getMins.run()
    
    # Krok 3: Odpala kolosalne czasy symulacji (Precesja, Shift, Spirala)
    # Odkomentuj to poniżej, gdy będziesz miał czas zostawić komputer na dłużej!
    # gen_long_sims.run()

    print("\n=========================================================")
    print("WSZYSTKIE WYZNACZONE EKSPERYMENTY ZAKOŃCZONE!")
    print("=========================================================")

if __name__ == "__main__":
    main()

