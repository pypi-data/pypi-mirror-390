#pragma once

#include "InternalType.hpp"

namespace deb {
///@brief Maximum size for a deb_size_t
constexpr deb_size_t DEB_MAX_SIZE = 4294967295;

///@brief Real number 0
constexpr deb_real REAL_ZERO = 0.0;

///@brief Real number 1
constexpr deb_real REAL_ONE = 1.0;

///@brief Real number pi
constexpr deb_real REAL_PI = 3.14159265358979323846;

///@brief Real number 2 * pi
constexpr deb_real REAL_TWO_PI = 6.283185307179586476925286766559;

///@brief Complex number 0
constexpr deb_complex COMPLEX_ZERO(REAL_ZERO, REAL_ZERO);

///@brief Complex number i
constexpr deb_complex COMPLEX_IMAG_UNIT(REAL_ZERO, REAL_ONE);
} // namespace deb
