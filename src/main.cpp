#include <iostream>
#include <iomanip>
#include <cstdlib>
#include <string>
#include <algorithm>
#include "Simulation.h"

// Sposób wywołania:
//   main <totalTime> [tStepInitial] [sampleInterval] [to2PN] [absTol] [relTol]
//
// Parametry (wszystkie opcjonalne poza pierwszym):
//   totalTime       - łączny czas symulacji [s]
//   tStepInitial    - początkowy krok adaptacyjny [s] (domyślnie 1.0)
//   sampleInterval  - co ile sekund próbkujemy stan do wyjścia
//                     (0 = co krok integratora; domyślnie 60.0)
//   to2PN           - 1 = bez członu 2.5PN, 0 = pełna dynamika z reakcją (domyślnie 0)
//   absTol, relTol  - tolerancje sterujące krokiem (domyślnie 1e-3, 1e-9)
//
// Wyjście (stdout): nagłówek z parametrami + kolumny
//   t [s]   |r| [km]   |v| [km/s]   krok [s]   E_newt   L_newt

int main(int argc, char* argv[]){

    if (argc < 2){
        std::cerr << "Uzycie: " << argv[0]
                  << " totalTime [tStepInit=1.0] [sampleInterval=60.0]"
                  << " [to2PN=0] [absTol=1e-3] [relTol=1e-9]" << std::endl;
        return 1;
    }

    double totalTime      = std::atof(argv[1]);
    double tStepInit      = (argc > 2) ? std::atof(argv[2]) : 1.0;
    double sampleInterval = (argc > 3) ? std::atof(argv[3]) : 60.0;
    bool   to2PN          = (argc > 4) ? (std::atoi(argv[4]) != 0) : false;
    double absTol         = (argc > 5) ? std::atof(argv[5]) : 1.e-3;
    double relTol         = (argc > 6) ? std::atof(argv[6]) : 1.e-9;

    Simulation sim(tStepInit, to2PN,
                   /*m1*/1.387, /*m2*/1.441,
                   /*r0*/746600.0, /*v0x*/0.0, /*v0y*/900.0,
                   absTol, relTol);

    // Nagłówek (wiersz 1 to ludzki opis; wiersz 2 to wartości parametrów,
    // używane przez skrypty Pythona; trzeci wiersz to nazwy kolumn).
    std::cout << "# tStepInit totalTime sampleInterval to2PN absTol relTol\n";
    std::cout << tStepInit << "\t"
              << totalTime << "\t"
              << sampleInterval << "\t"
              << (to2PN ? 1 : 0) << "\t"
              << absTol << "\t"
              << relTol << "\n";
    std::cout << "# t[s]\tr[km]\tv[km/s]\tdt[s]\tE_newt\tL_newt\n";

    std::cout << std::scientific << std::setprecision(10);

    // Próbkowanie po stałych odstępach czasu (sampleInterval).
    // Jeśli sampleInterval <= 0, drukujemy po każdym kroku integratora.
    double nextSampleT = 0.0;

    auto sample = [&](){
        std::cout << sim.GetTime() << "\t";
        sim.PrintMag();
        std::cout << "\t" << sim.GetStep()
                  << "\t" << sim.EnergyNewtonian()
                  << "\t" << sim.AngMomNewtonian()
                  << "\n";
    };

    sample();
    if (sampleInterval > 0.0) nextSampleT = sampleInterval;

    if (sampleInterval > 0.0){
        while (sim.GetTime() < totalTime){
            double target = std::min(nextSampleT, totalTime);
            sim.Advance(target);
            sample();
            nextSampleT += sampleInterval;
            if (nextSampleT > totalTime) nextSampleT = totalTime;
            if (sim.GetTime() >= totalTime) break;
        }
    }
    else{
        while (sim.GetTime() < totalTime){
            sim.Proceed();
            // Nie przekroczyć totalTime
            if (sim.GetTime() > totalTime){
                // ostatni krok zostawiamy w stanie końcowym - tak też zachowuje się
                // wariant RK4. Możemy też dociąć - ale dla DP "Advance(target)" wyżej
                // robi to lepiej. Tu po prostu raportujemy.
            }
            sample();
        }
    }

    std::cerr << "# Kroki zaakceptowane: " << sim.GetStepsAccepted()
              << "  odrzucone: "          << sim.GetStepsRejected() << std::endl;

    return 0;
}
