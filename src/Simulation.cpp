#include "Simulation.h"
#include <iostream>
#include <cmath>
#include <algorithm>

// ------------------------------------------------------------------
// Przyspieszenie postnewtonowskie (Pati & Will 2002)
// Identyczne wzory jak w wariancie ze stałokrokowym RK4 (zps2-main).
// ------------------------------------------------------------------
Vector Simulation::calcAcc(const Vector& pos, const Vector& vel){
    double r    = pos.Mag();
    Vector n    = pos*(1.0/r);
    double v    = vel.Mag();
    double rDot = vel*n;

    double A1 = -(1+3*eta)*v*v + (3.0/2.0)*eta*rDot*rDot + 2*(2+eta)*(m/r)*G;
    A1 /= c*c;

    double A2 =  -eta*(3-4*eta)*v*v*v*v + 0.5*eta*(13-4*eta)*v*v*(m/r)*G;
    A2 +=        (3.0/2.0)*eta*(3-4*eta)*v*v*rDot*rDot + (2+25*eta+2*eta*eta)*rDot*rDot*(m/r)*G;
    A2 +=        -(15.0/8.0)*eta*(1-3*eta)*rDot*rDot*rDot*rDot - (3.0/4.0)*(12+29*eta)*(m/r)*(m/r)*G*G;
    A2 /= c*c*c*c;

    double B1  = 2*(2-eta);
    B1 /= c*c;

    double B2  = 0.5*eta*(15+4*eta)*v*v - (3.0/2.0)*eta*(3+2*eta)*rDot*rDot;
    B2 +=       -0.5*(4+41*eta+8*eta*eta)*(m/r)*G;
    B2 /= c*c*c*c;

    double A25, B25;
    if(to2PN){
        A25 = 0.0;
        B25 = 0.0;
    }
    else{
        A25  = 3*v*v + (17.0/3.0)*(m/r)*G;
        A25 *= G;
        A25 /= c*c*c*c*c;

        B25  = v*v + 3*(m/r)*G;
        B25 *= G;
        B25 /= c*c*c*c*c;
    }

    double nCoeff = -1 + A1 + A2 + (8.0/5.0)*eta*(m/r)*rDot*A25;
    nCoeff *= G*(m/(r*r));

    double vCoeff = rDot*(B1+B2) - (8.0/5.0)*eta*(m/r)*B25;
    vCoeff *= G*(m/(r*r));

    return n*nCoeff + vel*vCoeff;
}

// ------------------------------------------------------------------
// Współczynniki Dormand-Prince 5(4) - tabela Butchera
// (FSAL: ostatni etap k7 = pierwszy etap kolejnego kroku)
// ------------------------------------------------------------------
namespace {
    // Wagi rozwinięcia 5. rzędu (b)
    constexpr double b1 = 35.0/384.0;
    constexpr double b3 = 500.0/1113.0;
    constexpr double b4 = 125.0/192.0;
    constexpr double b5 = -2187.0/6784.0;
    constexpr double b6 = 11.0/84.0;
    // b2 = 0, b7 = 0

    // Różnica wag (b - b*) -> estymator błędu lokalnego
    constexpr double e1 = 71.0/57600.0;
    constexpr double e3 = -71.0/16695.0;
    constexpr double e4 = 71.0/1920.0;
    constexpr double e5 = -17253.0/339200.0;
    constexpr double e6 = 22.0/525.0;
    constexpr double e7 = -1.0/40.0;
}

void Simulation::dpStep(double h,
                        const Vector& k1,
                        Vector& Xn, Vector& Vn,
                        Vector& errX, Vector& errV,
                        Vector& kLastOut)
{
    // Stan: y = (X, V), pochodna f(y) = (V, a(X,V))
    // k_i odnosi się do pochodnej (V_i, k_i^V), gdzie k_i^V = a(X_i, V_i),
    // a "V-część" k_i to po prostu V_i przeniesione przez etap.
    //
    // Aby kod był czytelny, pamiętamy dla każdego etapu osobno
    // przyrosty położenia (Vi) i przyrosty prędkości (ki = a).

    // Etap 1 (FSAL): k1 = a(X, V)
    Vector V1 = V;
    Vector A1 = k1;

    // Etap 2: c2 = 1/5
    Vector X2 = X + h*(1.0/5.0)*V1;
    Vector V2 = V + h*(1.0/5.0)*A1;
    Vector A2 = calcAcc(X2, V2);

    // Etap 3: c3 = 3/10
    Vector X3 = X + h*((3.0/40.0)*V1 + (9.0/40.0)*V2);
    Vector V3 = V + h*((3.0/40.0)*A1 + (9.0/40.0)*A2);
    Vector A3 = calcAcc(X3, V3);

    // Etap 4: c4 = 4/5
    Vector X4 = X + h*((44.0/45.0)*V1 + (-56.0/15.0)*V2 + (32.0/9.0)*V3);
    Vector V4 = V + h*((44.0/45.0)*A1 + (-56.0/15.0)*A2 + (32.0/9.0)*A3);
    Vector A4 = calcAcc(X4, V4);

    // Etap 5: c5 = 8/9
    Vector X5 = X + h*((19372.0/6561.0)*V1 + (-25360.0/2187.0)*V2 + (64448.0/6561.0)*V3 + (-212.0/729.0)*V4);
    Vector V5 = V + h*((19372.0/6561.0)*A1 + (-25360.0/2187.0)*A2 + (64448.0/6561.0)*A3 + (-212.0/729.0)*A4);
    Vector A5 = calcAcc(X5, V5);

    // Etap 6: c6 = 1
    Vector X6 = X + h*((9017.0/3168.0)*V1 + (-355.0/33.0)*V2 + (46732.0/5247.0)*V3 + (49.0/176.0)*V4 + (-5103.0/18656.0)*V5);
    Vector V6 = V + h*((9017.0/3168.0)*A1 + (-355.0/33.0)*A2 + (46732.0/5247.0)*A3 + (49.0/176.0)*A4 + (-5103.0/18656.0)*A5);
    Vector A6 = calcAcc(X6, V6);

    // Rozwiązanie 5. rzędu (b-wagi). Uwaga: dla DP węzeł b7 = 0,
    // więc rozwiązanie wykorzystuje tylko k1..k6.
    Xn = X + h*(b1*V1 + b3*V3 + b4*V4 + b5*V5 + b6*V6);
    Vn = V + h*(b1*A1 + b3*A3 + b4*A4 + b5*A5 + b6*A6);

    // Etap 7: c7 = 1 - liczony "w" punkcie końcowym 5. rzędu (FSAL)
    Vector A7 = calcAcc(Xn, Vn);
    Vector V7 = Vn;

    kLastOut = A7;

    // Błąd lokalny: różnica (b - b*) zawiera również b7 (e7 != 0).
    errX = h*(e1*V1 + e3*V3 + e4*V4 + e5*V5 + e6*V6 + e7*V7);
    errV = h*(e1*A1 + e3*A3 + e4*A4 + e5*A5 + e6*A6 + e7*A7);
}

// ------------------------------------------------------------------
// Pojedynczy adaptacyjny krok DP5(4).
// Sterowanie krokiem: standardowy schemat
//      h_new = h * safety * (1/err_norm)^(1/p),   p = 5
// z ograniczeniami min/max factor.
// ------------------------------------------------------------------
void Simulation::Proceed(){
    constexpr double safety    = 0.9;
    constexpr double minFactor = 0.2;
    constexpr double maxFactor = 5.0;
    constexpr double pOrder    = 5.0;
    constexpr int    maxAttempts = 20;

    // FSAL: pierwszy etap to ostatni etap poprzedniego (zaakceptowanego) kroku
    Vector k1 = hasKLast ? kLast : calcAcc(X, V);

    for(int attempt = 0; attempt < maxAttempts; ++attempt){
        Vector Xn, Vn, errX, errV, kNew;
        dpStep(tStep, k1, Xn, Vn, errX, errV, kNew);

        // Skalowane normy błędu - kombinacja tolerancji bezwzględnej i względnej.
        // sc_i = absTol + relTol * max(|y_i|, |y_i^{n+1}|)
        auto scaleSq = [&](double a, double b) {
            double s = absTol + relTol * std::max(std::fabs(a), std::fabs(b));
            return s*s;
        };

        // X i V mają różne jednostki (km vs km/s) - więc skalowanie per-komponent.
        double sxX = scaleSq(X.Mag(), Xn.Mag());
        double sxV = scaleSq(V.Mag(), Vn.Mag());

        double err2 = (errX.MagSq()/sxX + errV.MagSq()/sxV) / 4.0;
        double errNorm = std::sqrt(err2);

        if (errNorm <= 1.0 || tStep <= tStepMin*1.0000001){
            // Krok zaakceptowany
            X = Xn;
            V = Vn;
            tNow += tStep;
            kLast = kNew;
            hasKLast = true;
            ++stepsAccepted;

            // Nowy krok (powiększ, ale z ograniczeniem)
            double factor;
            if (errNorm == 0.0)
                factor = maxFactor;
            else
                factor = safety * std::pow(1.0/errNorm, 1.0/pOrder);

            factor = std::min(maxFactor, std::max(minFactor, factor));
            tStep  = std::min(tStepMax, std::max(tStepMin, tStep*factor));
            return;
        }
        else{
            // Krok odrzucony - zmniejsz krok i spróbuj jeszcze raz.
            ++stepsRejected;
            double factor = safety * std::pow(1.0/errNorm, 1.0/pOrder);
            factor = std::max(minFactor, factor);
            tStep  = std::max(tStepMin, tStep*factor);
            // FSAL nieaktualne po odrzuconym kroku z innym h - ale k1 = a(X,V)
            // pozostaje poprawne (X,V się nie zmieniły), więc liczymy dalej.
        }
    }

    // Bezpiecznik: jeśli mimo wszystko nie udało się zaakceptować kroku,
    // wymuszamy ruch krokiem minimalnym aby symulacja się nie zacięła.
    Vector Xn, Vn, errX, errV, kNew;
    tStep = tStepMin;
    dpStep(tStep, k1, Xn, Vn, errX, errV, kNew);
    X = Xn; V = Vn;
    tNow += tStep;
    kLast = kNew;
    hasKLast = true;
    ++stepsAccepted;
}

void Simulation::Advance(double tEnd){
    while (tNow < tEnd){
        // Ostatni krok przycinamy, by trafić dokładnie w tEnd
        if (tNow + tStep > tEnd){
            double savedStep = tStep;
            tStep = tEnd - tNow;
            Proceed();
            // Po dotarciu do tEnd przywracamy "naturalny" krok,
            // ograniczając go do najmniejszego z (poprzedni, nowo zaproponowany)
            tStep = std::min(savedStep, tStep);
            break;
        }
        Proceed();
    }
}

// ------------------------------------------------------------------
void Simulation::Print(){
    X.Print(); std::cout << "\n";
    V.Print(); std::cout << "\n";
}

void Simulation::PrintMag(){
    std::cout << X.Mag() << "\t" << V.Mag();
}

double Simulation::EnergyNewtonian() const {
    // E/mu (na jednostkę masy zredukowanej): v^2/2 - G m / r
    double r = X.Mag();
    double v2 = V.MagSq();
    return 0.5*v2 - G*m/r;
}

double Simulation::AngMomNewtonian() const {
    // |L|/mu = |X x V| (2D: składowa z)
    // Vector nie ma jawnie x/y publicznie, więc liczymy przez relację
    // |X x V| = sqrt(X^2 V^2 - (X·V)^2)
    double xv  = X * V;
    double X2  = X.MagSq();
    double V2  = V.MagSq();
    double L2  = X2*V2 - xv*xv;
    return (L2 > 0.0) ? std::sqrt(L2) : 0.0;
}
