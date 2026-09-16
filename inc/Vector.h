/*
  * Copyright (c) 2026 Franciszek Jan Drągowski, Paweł Sajdak
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

        double GetX() const { return x; } // zakładając, że prywatna zmienna to 'x'
        double GetY() const { return y; } // zakładając, że prywatna zmienna to 'y'

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
