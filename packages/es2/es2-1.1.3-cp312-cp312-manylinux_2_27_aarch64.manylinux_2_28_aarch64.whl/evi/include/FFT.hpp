#pragma once
#include "InternalType.hpp"

#include <complex>
#include <vector>

namespace deb {
class FFT {
public:
    FFT(const deb_u64 degree);

    void forwardFFT(deb_message &msg) const;
    void backwardFFT(deb_message &msg) const;

    auto getPowerOfFive(deb_u64 rot) const { return powers_of_five_[rot]; }

private:
    // deb_u64 degree_; // a.k.a. Polynomial degree N
    std::vector<deb_u64> powers_of_five_;
    std::vector<deb_complex> complex_roots_;
    std::vector<deb_complex> roots_;
    std::vector<deb_complex> inv_roots_;
};
} // namespace deb
