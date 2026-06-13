#ifndef VECTOR_H
#define VECTOR_H

class Vector
{
    double x, y;

    public:
        Vector(double x_ = 0.0, double y_ = 0.0){
            x = x_;
            y = y_;
        }

        Vector& operator+=(const Vector&);
        Vector  operator+(const Vector&) const;
        Vector  operator-(const Vector&) const;
        Vector  operator*(double) const;
        friend Vector operator*(double, const Vector&);
        double  operator*(const Vector&) const;     // iloczyn skalarny

        double Mag() const;
        double MagSq() const;
        void Print() const;
};

inline Vector operator*(double a, const Vector& v){
    return v*a;
}

#endif
