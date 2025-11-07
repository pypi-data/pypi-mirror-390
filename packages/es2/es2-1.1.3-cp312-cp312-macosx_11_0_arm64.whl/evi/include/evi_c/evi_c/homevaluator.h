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

#ifdef __cplusplus
extern "C" {
#endif

evi_status_t evi_homevaluator_create(const evi_context_t *context, evi_homevaluator_t **out_eval);
void evi_homevaluator_destroy(evi_homevaluator_t *eval);

evi_status_t evi_homevaluator_load_eval_key_pack(evi_homevaluator_t *eval, const evi_keypack_t *pack);
evi_status_t evi_homevaluator_load_eval_key_path(evi_homevaluator_t *eval, const char *path);
evi_status_t evi_homevaluator_load_eval_key_buffer(evi_homevaluator_t *eval, const uint8_t *data, size_t length);

evi_status_t evi_homevaluator_search(evi_homevaluator_t *eval, const evi_index_t *index, const evi_query_t *query,
                                     const evi_compute_buffer_t *buffer, evi_search_result_t **out_result);

#ifdef __cplusplus
}
#endif
