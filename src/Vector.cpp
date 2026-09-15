/*
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
  */

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
