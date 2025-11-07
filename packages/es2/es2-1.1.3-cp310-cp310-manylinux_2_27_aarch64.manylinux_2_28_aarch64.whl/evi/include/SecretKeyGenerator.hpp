
#pragma once

#include "Context.hpp"
#include "InternalType.hpp"
#include "NTT.hpp"

#include "DebFBType.h"
#include "alea/alea.h"
#include "alea/algorithms.h"

#include <cstring>
#include <fstream>
#include <memory>
#include <optional>
#include <random>

namespace deb {

// template <typename Evaluator>
class SecretKeyGenerator {
public:
    SecretKeyGenerator(
        deb_preset_t preset,
        std::optional<std::vector<uint8_t>> seeds = std::nullopt);

    // deb_sk genEmptyKey();
    // static deb_sk genEmptyKey(deb_preset_t preset);

    deb_sk genSecretKey();
    deb_sk genSecretKey(int8_t *coeffs);

    static int8_t *genCoeff(const std::shared_ptr<Context> &context,
                            std::shared_ptr<alea_state> as = nullptr);
    static deb_sk
    genSecretKey(deb_preset_t preset,
                 std::optional<std::vector<uint8_t>> seeds = std::nullopt);
    static deb_sk genSecretKeyFromCoeff(const std::shared_ptr<Context> &context,
                                        int8_t *coeffs = nullptr);

    static void saveSecret(const deb_sk &sk, const std::string &filename);
    static void loadSecret(deb_sk &sk, const std::string &filename);

private:
    std::shared_ptr<alea_state> as_;
    std::shared_ptr<Context> context_;
};
} // namespace deb
