#include "Vector.h"
#include <iostream>
#include <cmath>


Vector& Vector::operator+=(const Vector& v){
    x += v.x;
    y += v.y;
    return *this;
}

Vector Vector::operator+(const Vector& v) const{
    return Vector(x + v.x, y + v.y);
}

Vector Vector::operator-(const Vector& v) const{
    return Vector(x - v.x, y - v.y);
}

Vector Vector::operator*(double a) const{
    return Vector(x*a, y*a);
}

double Vector::operator*(const Vector& v) const{
    return x*v.x + y*v.y;
}

double Vector::Mag() const{
    return std::sqrt(x*x + y*y);
}

double Vector::MagSq() const{
    return x*x + y*y;
}

void Vector::Print() const{
    std::cout << x << "\t" << y;
}
