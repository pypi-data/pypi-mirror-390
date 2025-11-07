#pragma once

#include "InternalType.hpp"

#include <algorithm>

namespace deb {

using deb_u128 = unsigned __int128;
using deb_i128 = __int128;

inline deb_u64 u128Hi(const deb_u128 value) {
    return static_cast<deb_u64>(value >> 64);
}
inline deb_u64 u128Lo(const deb_u128 value) {
    return static_cast<deb_u64>(value);
}

inline deb_u128 mul64To128(const deb_u64 op1, const deb_u64 op2) {
    return static_cast<deb_u128>(op1) * op2;
}

inline deb_u64 mul64To128Hi(const deb_u64 op1, const deb_u64 op2) {
    deb_u128 mul = mul64To128(op1, op2);
    return u128Hi(mul);
}

inline deb_u64 divide128By64Lo(const deb_u64 op1_hi, const deb_u64 op1_lo,
                               const deb_u64 op2) {
    return static_cast<deb_u64>(((static_cast<deb_u128>(op1_hi) << 64) |
                                 static_cast<deb_u128>(op1_lo)) /
                                op2);
}

inline deb_u64 mulModSimple(const deb_u64 op1, const deb_u64 op2,
                            const deb_u64 mod) {
    return static_cast<deb_u64>(mul64To128(op1, op2) % mod);
}

inline deb_u64 powModSimple(deb_u64 base, deb_u64 expo, const deb_u64 mod) {
    deb_u64 res = 1;
    while (expo > 0) {
        if ((expo & 1) == 1) // if odd
            res = mulModSimple(res, base, mod);
        base = mulModSimple(base, base, mod);
        expo >>= 1;
    }

    return res;
}

inline deb_u64 mulModLazy(const deb_u64 op1, const deb_u64 op2,
                          const deb_u64 op2_barrett, const deb_u64 mod) {
    return op1 * op2 - mul64To128Hi(op1, op2_barrett) * mod;
}

inline deb_size_t bitReverse32(deb_size_t x) {
    x = (((x & 0xaaaaaaaa) >> 1) | ((x & 0x55555555) << 1));
    x = (((x & 0xcccccccc) >> 2) | ((x & 0x33333333) << 2));
    x = (((x & 0xf0f0f0f0) >> 4) | ((x & 0x0f0f0f0f) << 4));
    x = (((x & 0xff00ff00) >> 8) | ((x & 0x00ff00ff) << 8));
    return ((x >> 16) | (x << 16));
}

inline deb_size_t bitReverse(deb_size_t x, deb_u64 max_digits) {
    return bitReverse32(x) >> (32 - max_digits);
}

inline deb_u64 countLeftZeroes(deb_u64 op) {
#ifndef __has_builtin
#define __has_builtin(arg) 0
#endif
#if __has_builtin(__builtin_clzll)
    return static_cast<deb_u64>(__builtin_clzll(op));
#elif _MSC_VER
    return static_cast<deb_u64>(__lzcnt64(op));
#else
    // Algorithm: see "Hacker's delight" 2nd ed., section 5.13, algorithm 5-12.
    deb_u64 n = 64;
    deb_u64 tmp = op >> 32;
    if (tmp != 0) {
        n = n - 32;
        op = tmp;
    }
    tmp = op >> 16;
    if (tmp != 0) {
        n = n - 16;
        op = tmp;
    }
    tmp = op >> 8;
    if (tmp != 0) {
        n = n - 8;
        op = tmp;
    }
    tmp = op >> 4;
    if (tmp != 0) {
        n = n - 4;
        op = tmp;
    }
    tmp = op >> 2;
    if (tmp != 0) {
        n = n - 2;
        op = tmp;
    }
    tmp = op >> 1;
    if (tmp != 0)
        return n - 2;
    return n - op;
#endif
}

inline deb_u64 bitWidth(const deb_u64 op) {
#ifdef __cpp_lib_int_pow2
    return std::bit_width(op);
#else
    return op ? UINT64_C(64) - countLeftZeroes(op) : UINT64_C(0);
#endif
}

// Integral log2 with log2floor(0) := 0
inline deb_u64 log2floor(const deb_u64 op) {
    return op ? bitWidth(op) - 1 : UINT64_C(0);
}

inline bool isPowerOfTwo(deb_u64 op) { return op && (!(op & (op - 1))); }

template <typename T> void bitReverseArray(T *data, deb_u64 n) {
    if (!(isPowerOfTwo(n)))
        return;

    for (deb_u64 i = 1UL, j = 0UL; i < n; ++i) {
        deb_u64 bit = n >> 1;
        for (; j >= bit; bit >>= 1)
            j -= bit;

        j += bit;
        if (i < j)
            std::swap(data[i], data[j]);
    }
}

inline deb_u64 subIfGE(deb_u64 a, deb_u64 b) { return (a >= b ? a - b : a); }

inline deb_u64 invModSimple(deb_u64 a, deb_u64 prime) {
    return powModSimple(a, prime - 2, prime);
}

inline deb_real addZeroPointFive(deb_real x) {
    return x > 0 ? x + 0.5 : x - 0.5;
}
} // namespace deb
