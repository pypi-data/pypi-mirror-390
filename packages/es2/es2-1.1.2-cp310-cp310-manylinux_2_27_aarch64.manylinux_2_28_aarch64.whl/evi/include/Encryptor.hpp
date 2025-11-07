#pragma once

#include "Basic.hpp"
#include "Constant.h"
#include "Context.hpp"
#include "FFT.hpp"
#include "InternalType.hpp"
#include "ModArith.hpp"

#include "alea/alea.h"

#include <cstring>
#include <optional>
#include <stdexcept>
#include <type_traits>
#include <vector>

namespace deb {

struct EncryptOptions {
    deb_real scale = 0;
    deb_size_t level = DEB_MAX_SIZE;
    bool ntt_out = true;
    EncryptOptions &Scale(deb_real s) {
        scale = s;
        return *this;
    }
    EncryptOptions &Level(deb_size_t l) {
        level = l;
        return *this;
    }
    EncryptOptions &NttOut(bool n) {
        ntt_out = n;
        return *this;
    }
};

[[maybe_unused]] static EncryptOptions default_opt;

// TODO: make template for Encryptor
// to support constexpr functions with various presets
class Encryptor {
public:
    explicit Encryptor(
        const deb_preset_t preset,
        std::optional<std::vector<uint8_t>> seeds = std::nullopt);

    template <typename MSG, typename KEY,
              std::enable_if_t<!std::is_pointer_v<std::decay_t<MSG>>, int> = 0>
    void encrypt(const MSG &msg, const KEY &key, deb_cipher &ctxt,
                 const EncryptOptions &opt = default_opt) const;

    template <typename MSG, typename KEY>
    void encrypt(const std::vector<MSG> &msg, const KEY &key, deb_cipher &ctxt,
                 const EncryptOptions &opt = default_opt) const;

    template <typename MSG, typename KEY>
    void encrypt(const MSG *msg, const KEY &key, deb_cipher &ctxt,
                 const EncryptOptions &opt = default_opt) const;

private:
    template <typename KEY>
    void innerEncrypt([[maybe_unused]] const deb_bigpoly &ptxt,
                      [[maybe_unused]] const KEY &key,
                      [[maybe_unused]] deb_size_t poly_size,
                      [[maybe_unused]] deb_cipher &ctxt) const {
        throw std::runtime_error(
            "Encryptor::innerEncrypt: Not implemented for this key type");
    }

    template <typename MSG>
    void embeddingToN(const MSG &msg, const deb_real &delta, deb_bigpoly &ptxt,
                      const deb_size_t size) const;

    template <typename MSG>
    void encodeWithoutNTT(const MSG &msg, deb_bigpoly &ptxt,
                          const deb_size_t size, const deb_real scale) const;

    void sampleZO(const deb_size_t poly_size) const;

    void sampleGaussian(const deb_size_t idx, const deb_size_t poly_size,
                        const bool do_ntt) const;

    std::shared_ptr<Context> context_;
    std::shared_ptr<alea_state> as_;
    // compute buffers
    mutable deb_bigpoly ptxt_buffer_;
    mutable deb_bigpoly vx_buffer_;
    mutable std::vector<deb_bigpoly> ex_buffers_;

    // TODO: move to Context
    std::vector<ModArith> modarith_;
    FFT fft_;
};

// NOLINTBEGIN
#define DECL_ENCRYPT_TEMPLATE_MSG_KEY(msg_t, key_t, prefix)                    \
    prefix template void Encryptor::encrypt<msg_t, key_t>(                     \
        const msg_t &msg, const key_t &key, deb_cipher &ctxt,                  \
        const EncryptOptions &opt) const;                                      \
    prefix template void Encryptor::encrypt<msg_t, key_t>(                     \
        const std::vector<msg_t> &msg, const key_t &key, deb_cipher &ctxt,     \
        const EncryptOptions &opt) const;                                      \
    prefix template void Encryptor::encrypt<msg_t, key_t>(                     \
        const msg_t *msg, const key_t &key, deb_cipher &ctxt,                  \
        const EncryptOptions &opt) const;

#define DECL_ENCRYPT_TEMPLATE_MSG(msg_t, prefix)                               \
    DECL_ENCRYPT_TEMPLATE_MSG_KEY(msg_t, deb_sk, prefix)                       \
    DECL_ENCRYPT_TEMPLATE_MSG_KEY(msg_t, deb_swk, prefix)                      \
    prefix template void Encryptor::embeddingToN<msg_t>(                       \
        const msg_t &msg, const deb_real &delta, deb_bigpoly &ptxt,            \
        const deb_size_t size) const;                                          \
    prefix template void Encryptor::encodeWithoutNTT<msg_t>(                   \
        const msg_t &msg, deb_bigpoly &ptxt, const deb_size_t size,            \
        const deb_real scale) const;
// NOLINTEND

DECL_ENCRYPT_TEMPLATE_MSG(deb_message, extern)
DECL_ENCRYPT_TEMPLATE_MSG(deb_coeff, extern)

} // namespace deb
