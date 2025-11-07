#pragma once

#include "Context.hpp"
#include "FFT.hpp"
#include "InternalType.hpp"
#include "ModArith.hpp"

#include "alea/alea.h"

#include <cstring>
#include <optional>
#include <vector>

namespace deb {

class KeyGenerator {
public:
    explicit KeyGenerator(
        const deb_preset_t preset,
        std::optional<std::vector<uint8_t>> seeds = std::nullopt);
    explicit KeyGenerator(
        const deb_sk &sk,
        std::optional<std::vector<uint8_t>> seeds = std::nullopt);

    KeyGenerator(const KeyGenerator &) = delete;
    ~KeyGenerator() = default;

    void genSwitchingKey(const deb_bigpoly *from, const deb_bigpoly *to,
                         deb_bigpoly *ax, deb_bigpoly *bx,
                         const deb_size_t ax_size = 0,
                         const deb_size_t bx_size = 0) const;

    deb_swk genEncKey(std::optional<deb_sk> sk = std::nullopt) const;
    void genEncKeyInplace(deb_swk &enckey,
                          std::optional<deb_sk> sk = std::nullopt) const;
    deb_swk genMultKey(std::optional<deb_sk> sk = std::nullopt) const;
    void genMultKeyInplace(deb_swk &mulkey,
                           std::optional<deb_sk> sk = std::nullopt) const;
    deb_swk genConjKey(std::optional<deb_sk> sk = std::nullopt) const;
    void genConjKeyInplace(deb_swk &conjkey,
                           std::optional<deb_sk> sk = std::nullopt) const;
    deb_swk genLeftRotKey(const deb_size_t rot,
                          std::optional<deb_sk> sk = std::nullopt) const;
    void genLeftRotKeyInplace(const deb_size_t rot, deb_swk &rotkey,
                              std::optional<deb_sk> sk = std::nullopt) const;
    deb_swk genRightRotKey(const deb_size_t rot,
                           std::optional<deb_sk> sk = std::nullopt) const;
    void genRightRotKeyInplace(const deb_size_t rot, deb_swk &rotkey,
                               std::optional<deb_sk> sk = std::nullopt) const;
    deb_swk genAutoKey(const deb_size_t sig,
                       std::optional<deb_sk> sk = std::nullopt) const;
    void genAutoKeyInplace(const deb_size_t sig, deb_swk &autokey,
                           std::optional<deb_sk> sk = std::nullopt) const;

    std::vector<deb_swk>
    genModPackKeyBundle(const deb_sk &sk_from, const deb_sk &sk_to,
                        std::optional<deb_sk> sk = std::nullopt) const;
    void
    genModPackKeyBundleInplace(const deb_sk &sk_from, const deb_sk &sk_to,
                               std::vector<deb_swk> &key_bundle,
                               std::optional<deb_sk> sk = std::nullopt) const;
    // std::vector<deb_swk> genModPackKeyBundleLWE(const deb_sk &sk_from, const
    // deb_sk &sk_to) const;

    // for EVI
    deb_swk genModPackKeyEVI(const deb_size_t pad_rank,
                             std::optional<deb_sk> sk = std::nullopt) const;
    void genModPackKeyEVIInplace(const deb_size_t pad_rank, deb_swk &modkey,
                                 std::optional<deb_sk> sk = std::nullopt) const;
    // deb_swk genMSModPackKeyEVI(const deb_sk &sk_from, const
    // std::vector<deb_sk> &sk_to, const deb_size_t pad_rank) const; deb_swk
    // genMSCCModPackKeyEVI(const deb_sk &sk_from, const std::vector<deb_sk>
    // &sk_to, const deb_size_t pad_rank) const; deb_swk genMSSwitchKeyEVI(const
    // deb_sk &sk_from, const std::vector<deb_sk> &sk_to) const; deb_swk
    // genMSReverseSwitchKeyEVI(const deb_sk &sk_from, const std::vector<deb_sk>
    // &sk_to) const; deb_swk genMSAdditiveSwitchKeyEVI(const deb_sk &sk_from,
    // const std::vector<deb_sk> &sk_to) const;

private:
    void frobeniusMapInNTT(const deb_bigpoly &op, const deb_i32 pow,
                           deb_bigpoly res) const;

    deb_bigpoly sampleGaussian(const deb_size_t poly_size,
                               bool do_ntt = false) const;

    void sampleUniform(deb_bigpoly &poly) const;
    void computeConst();

    std::shared_ptr<Context> context_;
    std::optional<deb_sk> sk_;
    std::shared_ptr<alea_state> as_;

    // TODO: move to Context
    std::vector<deb_u64> p_mod_;
    std::vector<deb_u64> hat_q_i_mod_;
    std::vector<deb_u64> hat_q_i_inv_mod_;
    std::vector<ModArith> modarith_;
    FFT fft_;
};

} // namespace deb
