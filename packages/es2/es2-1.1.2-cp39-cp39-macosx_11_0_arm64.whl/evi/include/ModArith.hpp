#pragma once

#include "Basic.hpp"
#include "InternalType.hpp"
#include "Macro.h"
#include "NTT.hpp"

#include <algorithm>
#include <memory>

//#ifdef DEB_OPENMP
//#include <omp.h>
//#endif

namespace deb {

class ModArith {
public:
    explicit ModArith() = default;
    explicit ModArith(deb_size_t size, deb_u64 prime,
                      NttType ntt_type = NttType::NEGACYCLIC);

    inline deb_u64 getPrime() const { return prime_; }
    inline deb_size_t getDefaultArraySize() const {
        return default_array_size_;
    }

    // InputModFactor: input value must be in the range
    //                [0, InputModFactor * prime).
    // OutputModFactor: output value will be in the range
    //                [0, OutputModFactor * prime).
    template <int InputModFactor = 4, int OutputModFactor = 1>
    inline void reduceModFactor(deb_u64 &op) const {
        static_assert((InputModFactor == 1) || (InputModFactor == 2) ||
                          (InputModFactor == 4),
                      "InputModFactor must be 1, 2 or 4");
        static_assert((OutputModFactor == 1) || (OutputModFactor == 2) ||
                          (OutputModFactor == 4),
                      "OutputModFactor must be 1, 2 or 4");

        if constexpr (InputModFactor > 2 && OutputModFactor <= 2)
            op = subIfGE(op, two_prime_);

        if constexpr (InputModFactor > 1 && OutputModFactor == 1)
            op = subIfGE(op, prime_);
    }

    // Barrett Parameters:
    //    1. exponent: 64 (implicit)
    //    2. ratio   : 2^64 / prime (barrettRatiofor64)
    // Rough algorithm description:
    //    1. Compute approximate value for the quotient (op * ratio) >> exponent
    //    2. res = op - approxQuotient * prime is in range [0, 2 * prime)
    //    3. Whenever OutputModFactor == 1, res additionally gets reduced if
    //      necessary.
    template <int OutputModFactor = 1> deb_u64 reduceBarrett(deb_u64 op) const {
        static_assert((OutputModFactor == 1) || (OutputModFactor == 2),
                      "OutputModFactor must be 1 or 2");

        deb_u64 approx_quotient = mul64To128Hi(op, barrett_ratio_for_deb_u64_);
        deb_u64 res = op - approx_quotient * prime_;
        // res in [0, 2*prime)

        reduceModFactor<2, OutputModFactor>(res);
        return res;
    }

    // Basic Assumption:
    //     4 * prime < 2^64
    // Precomputation:
    //     1. twoTo64 = 2^64 modulo prime
    //     2. twoTo64Shoup = Scaled approximation to twoTo64 / prime,
    //       in the fashion of Shoup's modular multiplication.
    // Rough algorithm description:
    //     1. Decompose the 128-bit integer (op) into (hi) * 2^64 + (lo).
    //     2. Do modular multiplication (hi) * 2^64 in Shoup's way, using the
    //       precomputed values.
    //     3. Do Barret reduction (lo) which is a 64-bit integer.
    //     4. Add two results of step 2 and step 3.
    template <int OutputModFactor = 1>
    deb_u64 reduceBarrett(deb_u128 op) const {
        static_assert((OutputModFactor == 1) || (OutputModFactor == 2) ||
                          (OutputModFactor == 4),
                      "OutputModFactor must be 1, 2 or 4");

        deb_u64 hi = u128Hi(op);
        deb_u64 lo = u128Lo(op);

        deb_u64 quot = mul64To128Hi(hi, two_to_64_shoup_) +
                       mul64To128Hi(lo, barrett_ratio_for_deb_u64_);
        deb_u64 res = hi * two_to_64_ + lo;
        res -= quot * prime_;

        reduceModFactor<4, OutputModFactor>(res);
        return res;
    }

    deb_u64 reduceNative(deb_u64 op) const { return op % prime_; }

    inline deb_u64 add(deb_u64 op1, deb_u64 op2) const {
        return subIfGE(op1 + op2, prime_);
    }
    inline deb_u64 sub(deb_u64 op1, deb_u64 op2) const {
        return (op1 >= op2) ? op1 - op2 : prime_ - op2 + op1;
    }

    template <int OutputModFactor = 1>
    deb_u64 mul(deb_u64 op1, deb_u64 op2) const {
        static_assert((OutputModFactor == 1) || (OutputModFactor == 2) ||
                          (OutputModFactor == 4),
                      "OutputModFactor must be 1, 2 or 4");

        return reduceBarrett<OutputModFactor>(mul64To128(op1, op2));
    }

    template <int OutputModFactor = 1>
    deb_u64 pow(deb_u64 base, deb_u64 expt) const {
        static_assert((OutputModFactor == 1) || (OutputModFactor == 2) ||
                          (OutputModFactor == 4),
                      "OutputModFactor must be 1, 2 or 4");

        deb_u64 res = 1;
        while (expt > 0) {
            if (expt & 1) // if odd
                res = mul<4>(res, base);
            base = mul<4>(base, base);
            expt >>= 1;
        }

        reduceModFactor<4, OutputModFactor>(res);

        return res;
    }

    deb_u64 inverse(deb_u64 op) const { return pow<1>(op, prime_ - 2); }

    // res[i] = op1[i] * op2 modulo prime for i.
    // Each element of `res` is in range [0, OutputModFactor * prime).
    // Possible values for OutputModFactor are 1 or 2.
    template <int OutputModFactor = 1>
    void constMult(const deb_u64 *op1, const deb_u64 op2, deb_u64 *res,
                   deb_size_t array_size) const;

    template <int OutputModFactor = 1>
    void constMult(const deb_u64 *op1, const deb_u64 op2, deb_u64 *res) const {
        constMult<OutputModFactor>(op1, op2, res, default_array_size_);
    }

    template <int OutputModFactor = 1>
    void constMultInPlace(deb_u64 *op1, const deb_u64 op2) const {
        constMult<OutputModFactor>(op1, op2, op1);
    }

    void mulVector(deb_u64 *res, const deb_u64 *op1, const deb_u64 *op2,
                   deb_size_t array_size) const;

    void mulVector(deb_u64 *res, const deb_u64 *op1, const deb_u64 *op2) const {
        mulVector(res, op1, op2, default_array_size_);
    }

    // OutputModFactor: components of the output vector will be in range
    //                [0, OutputModFactor * prime).
    //   - possible values: 1, 4
    template <int OutputModFactor = 1>
    inline void forwardNTT(deb_u64 *op, deb_u64 *res) const {
        // TODO(ksh) : implement out-of-place version.
        if (op != res)
            std::copy_n(op, default_array_size_, res);
        forwardNTT<OutputModFactor>(res);
    }

    template <int OutputModFactor = 1>
    inline void forwardNTT(deb_u64 *op) const {
        // DEB_ASSERT(ntt_ != nullptr);
        static_assert((OutputModFactor == 1) || (OutputModFactor == 2) ||
                          (OutputModFactor == 4),
                      "OutputModFactor must be 1 or 4");
        ntt_->computeForward<OutputModFactor>(op);
    }

    template <int OutputModFactor = 1>
    inline void backwardNTT(deb_u64 *op, deb_u64 *res) const {
        // TODO(ksh) : implement out-of-place version.
        if (op != res)
            std::copy_n(op, default_array_size_, res);
        backwardNTT<OutputModFactor>(res);
    }

    // OutputModFactor: components of the output vector will be in range
    //                [0, OutputModFactor * prime).
    //   - possible values: 1 or 2
    template <int OutputModFactor = 1>
    inline void backwardNTT(deb_u64 *op) const {
        // DEB_ASSERT(ntt_ != nullptr);
        static_assert((OutputModFactor == 1) || (OutputModFactor == 2),
                      "OutputModFactor must be 1 or 2");

        ntt_->computeBackward<OutputModFactor>(op);
    }

    NttType getNttType() const { return ntt_type_; }

    deb_size_t get_default_size() const { return default_array_size_; }
    deb_u64 get_barrett_expt() const { return barrett_expt_; }
    deb_u64 get_barrett_ratio() const { return barrett_ratio_; }

private:
    deb_u64 prime_;
    deb_u64 two_prime_;
    deb_u64 barrett_expt_; // 2^(K-1) < prime < 2^K
    deb_u64 barrett_ratio_;

    deb_size_t default_array_size_; // degree or dimension

    deb_u64 barrett_ratio_for_deb_u64_;
    deb_u64 two_to_64_;
    deb_u64 two_to_64_shoup_;

    NttType ntt_type_;

    std::shared_ptr<NTT> ntt_ = nullptr;
};

void forwardNTT(const std::vector<ModArith> &modarith, deb_bigpoly &poly,
                deb_size_t poly_size = 0,
                [[maybe_unused]] bool check_state = false);

void backwardNTT(const std::vector<ModArith> &modarith, deb_bigpoly &poly,
                 deb_size_t poly_size = 0,
                 [[maybe_unused]] bool check_state = true);

void addPoly(const std::vector<ModArith> &modarith, const deb_bigpoly &op1,
             const deb_bigpoly &op2, deb_bigpoly &res,
             deb_size_t poly_size = 0);
void subPoly(const std::vector<ModArith> &modarith, const deb_bigpoly &op1,
             const deb_bigpoly &op2, deb_bigpoly &res,
             deb_size_t poly_size = 0);
void mulPoly(const std::vector<ModArith> &modarith, const deb_bigpoly &op1,
             const deb_bigpoly &op2, deb_bigpoly &res,
             deb_size_t poly_size = 0);
void constMulPoly(const std::vector<ModArith> &modarith, const deb_bigpoly &op1,
                  const deb_u64 *op2, deb_bigpoly &res, deb_size_t s_id,
                  deb_size_t e_id);

} // namespace deb
