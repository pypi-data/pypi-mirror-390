#pragma once

#include "InternalType.hpp"

#include <cstdint>
#include <set>
#include <vector>

namespace deb {

namespace utils {
void findPrimeFactors(std::set<deb_u64> &s, deb_u64 n);
deb_u64 findPrimitiveRoot(deb_u64 prime);

bool isPrime(const deb_u64 n);
std::vector<deb_u64> seekPrimes(const deb_u64 center, const deb_u64 gap,
                                deb_u64 number, const bool only_smaller);
} // namespace utils

enum class NttType : uint32_t {
    NEGACYCLIC, // X^N + 1
    NONE
};

class NTT {
public:
    NTT() = default;
    NTT(deb_u64 degree, deb_u64 prime);

    template <int OutputModFactor = 1> // possible value: 1, 2, 4
    void computeForward(deb_u64 *op) const;

    template <int OutputModFactor = 1> // possible value: 1, 2
    void computeBackward(deb_u64 *op) const;

private:
    deb_u64 prime_;
    deb_u64 two_prime_;
    deb_u64 degree_;

    // TODO(juny): make support constexpr for NTT
    // roots of unity (bit reversed)
    std::vector<deb_u64> psi_rev_;
    std::vector<deb_u64> psi_inv_rev_;
    std::vector<deb_u64> psi_rev_shoup_;
    std::vector<deb_u64> psi_inv_rev_shoup_;

    // variables for last step of backward NTT
    deb_u64 degree_inv_;
    deb_u64 degree_inv_barrett_;
    deb_u64 degree_inv_w_;
    deb_u64 degree_inv_w_barrett_;

    void computeForwardNativeSingleStep(deb_u64 *op, const deb_u64 t) const;
    void computeBackwardNativeSingleStep(deb_u64 *op, const deb_u64 t) const;
    void computeBackwardNativeLast(deb_u64 *op) const;
};
} // namespace deb
