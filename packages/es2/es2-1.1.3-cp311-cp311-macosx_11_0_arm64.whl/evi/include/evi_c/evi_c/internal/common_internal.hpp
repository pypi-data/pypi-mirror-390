////////////////////////////////////////////////////////////////////////////////
//                                                                            //
// Copyright (C) 2024, CryptoLab Inc. All rights reserved.                    //
//                                                                            //
// This software and/or source code may be commercially used and/or           //
// disseminated only with the written permission of CryptoLab Inc,            //
// or in accordance with the terms and conditions stipulated in the           //
// agreement/contract under which the software and/or source code has been    //
// supplied by CryptoLab Inc. Any unauthorized commercial use and/or          //
// dissemination of this file is strictly prohibited and will constitute      //
// an infringement of copyright.                                              //
//                                                                            //
////////////////////////////////////////////////////////////////////////////////

#pragma once

#include "evi_c/common.h"

#include "EVI/ComputeBuffer.hpp"
#include "EVI/Context.hpp"
#include "EVI/Decryptor.hpp"
#include "EVI/Encryptor.hpp"
#include "EVI/Evaluator.hpp"
#include "EVI/Index.hpp"
#include "EVI/KeyGenerator.hpp"
#include "EVI/KeyPack.hpp"
#include "EVI/Message.hpp"
#include "EVI/Query.hpp"
#include "EVI/SealInfo.hpp"
#include "EVI/SearchResult.hpp"
#include "EVI/SecretKey.hpp"

#include "utils/Exceptions.hpp"

#include <optional>
#include <string>
#include <vector>

namespace evi::c_api::detail {

extern thread_local std::string g_last_error;

evi_status_t set_error(evi_status_t status, const char *message);
evi_status_t translate_exception();

template <typename Fn>
evi_status_t invoke_and_catch(Fn &&fn) {
    try {
        fn();
        return set_error(EVI_STATUS_SUCCESS, "");
    } catch (...) {
        return translate_exception();
    }
}

std::optional<float> to_optional(const float *value);
std::optional<double> to_optional(const double *value);

} // namespace evi::c_api::detail

struct evi_context {
    explicit evi_context(evi::Context ctx) : impl(std::move(ctx)) {}
    evi::Context impl;
};

struct evi_keypack {
    explicit evi_keypack(evi::KeyPack pack) : impl(std::move(pack)) {}
    evi::KeyPack impl;
};

struct evi_keygenerator {
    explicit evi_keygenerator(evi::KeyGenerator keygen) : impl(std::move(keygen)) {}
    evi::KeyGenerator impl;
};

struct evi_multikeygenerator {
    explicit evi_multikeygenerator(evi::MultiKeyGenerator keygen) : impl(std::move(keygen)) {}
    evi::MultiKeyGenerator impl;
};

struct evi_secret_key {
    explicit evi_secret_key(evi::SecretKey key) : impl(std::move(key)) {}
    evi::SecretKey impl;
};

struct evi_encryptor {
    explicit evi_encryptor(evi::Encryptor enc) : impl(std::move(enc)) {}
    evi::Encryptor impl;
};

struct evi_query {
    explicit evi_query(evi::Query q) : impl(std::move(q)) {}
    evi::Query impl;
};

struct evi_index {
    explicit evi_index(evi::Index idx) : impl(std::move(idx)) {}
    evi::Index impl;
};

struct evi_compute_buffer {
    explicit evi_compute_buffer(evi::ComputeBuffer buf) : impl(std::move(buf)) {}
    evi::ComputeBuffer impl;
};

struct evi_homevaluator {
    explicit evi_homevaluator(evi::HomEvaluator eval) : impl(std::move(eval)) {}
    evi::HomEvaluator impl;
};

struct evi_search_result {
    explicit evi_search_result(evi::SearchResult res) : impl(std::move(res)) {}
    evi::SearchResult impl;
};

struct evi_decryptor {
    explicit evi_decryptor(evi::Decryptor dec) : impl(std::move(dec)) {}
    evi::Decryptor impl;
};

struct evi_message {
    explicit evi_message(evi::Message msg) : impl(std::move(msg)) {}
    evi::Message impl;
};

struct evi_seal_info {
    explicit evi_seal_info(evi::SealInfo info) : impl(std::move(info)) {}
    evi::SealInfo impl;
};
