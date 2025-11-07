#pragma once

#include "Context.hpp"
#include "FFT.hpp"
#include "InternalType.hpp"
#include "ModArith.hpp"

#include <type_traits>

namespace deb {
// TODO: make template for Decryptor
// to support constexpr functions with various presets
class Decryptor {
public:
    explicit Decryptor(const deb_preset_t preset);
    // explicit Encryptor(const deb_shared_context_t &context);

    template <typename MSG,
              std::enable_if_t<!std::is_pointer_v<std::decay_t<MSG>>, int> = 0>
    void decrypt(const deb_cipher &ctxt, const deb_sk &sk, MSG &msg,
                 deb_real scale = 0) const;

    template <typename MSG>
    void decrypt(const deb_cipher &ctxt, const deb_sk &sk, MSG *msg,
                 deb_real scale = 0) const;

    template <typename MSG>
    void decrypt(const deb_cipher &ctxt, const deb_sk &sk,
                 std::vector<MSG> &msg, deb_real scale = 0) const {
        deb_assert(msg.size() == context_->get_num_secret(),
                   "[Decryptor::decrypt] Message size mismatch");
        decrypt(ctxt, sk, msg.data(), scale);
    }

private:
    deb_bigpoly
    innerDecrypt(const deb_cipher &ctxt, const deb_sk &sk,
                 const std::optional<deb_bigpoly> &ax = std::nullopt) const;
    void decodeWithSinglePoly(const deb_bigpoly &ptxt, deb_coeff &coeff,
                              deb_real scale) const;
    void decodeWithPolyPair(const deb_bigpoly &ptxt, deb_coeff &coeff,
                            deb_real scale) const;
    void decodeWithoutFFT(const deb_bigpoly &ptxt, deb_coeff &coeff,
                          deb_real scale) const;
    void decode(const deb_bigpoly &ptxt, deb_message &msg,
                deb_real scale) const;

    std::shared_ptr<Context> context_;
    // TODO: move to Context
    std::vector<ModArith> modarith_;
    FFT fft;
};

// NOLINTBEGIN
#define DECL_DECRYPT_TEMPLATE_MSG(msg_t, prefix)                               \
    prefix template void Decryptor::decrypt<msg_t>(                            \
        const deb_cipher &ctxt, const deb_sk &sk, msg_t &msg, deb_real scale)  \
        const;                                                                 \
    prefix template void Decryptor::decrypt<msg_t>(                            \
        const deb_cipher &ctxt, const deb_sk &sk, msg_t *msg, deb_real scale)  \
        const;
// NOLINTEND

DECL_DECRYPT_TEMPLATE_MSG(deb_message, extern)
DECL_DECRYPT_TEMPLATE_MSG(deb_coeff, extern)

} // namespace deb
