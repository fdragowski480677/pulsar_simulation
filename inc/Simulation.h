#ifndef SIMULATION_H
#define SIMULATION_H

#include "Vector.h"

// Symulacja ruchu względnego w układzie podwójnym z poprawkami postnewtonowskimi
// (1PN, 2PN, opcjonalnie 2.5PN - reakcja od emisji fal grawitacyjnych).
// Integrator: Dormand-Prince 5(4) z adaptacyjnym krokiem czasowym.

class Simulation{

    // Parametry fizyczne
    double m, mu, eta;

    // Stan: położenie i prędkość względna
    Vector X, V;

    // Kontrola kroku adaptacyjnego
    double tStep;       // bieżący krok czasowy [s]
    double tStepMin;    // dolne ograniczenie kroku
    double tStepMax;    // górne ograniczenie kroku
    double absTol;      // tolerancja bezwzględna
    double relTol;      // tolerancja względna

    // Stan integratora
    double tNow;            // bieżący czas
    Vector kLast;           // ostatni etap (FSAL: pierwszy etap kolejnego kroku)
    bool   hasKLast;        // czy mamy zapisany etap FSAL

    // Statystyki
    long stepsAccepted;
    long stepsRejected;

    bool to2PN;             // jeśli true: tylko 1PN+2PN, bez członu dyssypacyjnego

    const double G = 1.327 * 1.e11;     // km^3 / Mo / s^2
    const double c = 3.e5;              // km/s

    // Przyspieszenie dla zadanego stanu (PN do 2.5PN włącznie)
    Vector calcAcc(const Vector& pos, const Vector& vel);

    // Jeden próbny krok DP5(4) - bez modyfikacji stanu.
    // Wypełnia nowy stan (Xn, Vn), 5. rząd, oraz wektor błędu (errX, errV).
    // k1 podajemy z zewnątrz (FSAL); kLastOut = k7 (do zapisu jako FSAL).
    void dpStep(double h,
                const Vector& k1,
                Vector& Xn, Vector& Vn,
                Vector& errX, Vector& errV,
                Vector& kLastOut);

    public:
    Simulation(
        double tStep_   = 1.0,
        bool   to2PN_   = false,
        double m1       = 1.387,
        double m2       = 1.441,
        double r0       = 746600.0,
        double v0x      = 0.0,
        double v0y      = 900.0,
        double absTol_  = 1.e-6,
        double relTol_  = 1.e-9)
    {
        tStep   = tStep_;
        to2PN   = to2PN_;
        m       = m1 + m2;
        mu      = m1 * m2 / m;
        eta     = mu / m;
        X       = Vector(r0, 0.);
        V       = Vector(v0x, v0y);

        absTol  = absTol_;
        relTol  = relTol_;
        tStepMin = 1.e-6;
        tStepMax = 1.e4;

        tNow            = 0.0;
        hasKLast        = false;
        stepsAccepted   = 0;
        stepsRejected   = 0;
    }

    void Print();
    void PrintMag();

    // Jeden adaptacyjny krok DP5(4) (krok może być powtórzony przy odrzuceniu).
    void Proceed();

    // Wykonuje kroki, dopóki tNow < tEnd. Ostatni krok jest przycięty,
    // aby trafić dokładnie w tEnd.
    void Advance(double tEnd);

    // Akcesory
    double GetTime() const { return tNow; }
    double GetStep() const { return tStep; }
    long   GetStepsAccepted() const { return stepsAccepted; }
    long   GetStepsRejected() const { return stepsRejected; }

    // Pomocnicze: energia i moment pędu na jednostkę masy zredukowanej
    // (poziom newtonowski - do diagnostyki dyssypacji 2.5PN).
    double EnergyNewtonian() const;
    double AngMomNewtonian() const;
};

#endif
