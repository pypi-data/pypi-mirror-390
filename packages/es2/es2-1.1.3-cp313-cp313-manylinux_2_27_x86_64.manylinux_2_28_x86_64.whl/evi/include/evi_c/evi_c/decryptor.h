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

evi_status_t evi_decryptor_create(const evi_context_t *context, evi_decryptor_t **out_decryptor);
void evi_decryptor_destroy(evi_decryptor_t *decryptor);

evi_status_t evi_decryptor_decrypt_search_result_with_seckey(evi_decryptor_t *decryptor,
                                                             const evi_search_result_t *result,
                                                             const evi_secret_key_t *seckey, int is_score,
                                                             const double *scale, evi_message_t **out_message);

evi_status_t evi_decryptor_decrypt_search_result_with_path(evi_decryptor_t *decryptor,
                                                           const evi_search_result_t *result, const char *key_path,
                                                           int is_score, const double *scale,
                                                           evi_message_t **out_message);

evi_status_t evi_decryptor_decrypt_query_with_path(evi_decryptor_t *decryptor, const evi_query_t *query,
                                                   const char *key_path, const double *scale,
                                                   evi_message_t **out_message);

evi_status_t evi_decryptor_decrypt_query_with_seckey(evi_decryptor_t *decryptor, const evi_query_t *query,
                                                     const evi_secret_key_t *seckey, const double *scale,
                                                     evi_message_t **out_message);

#ifdef __cplusplus
}
#endif
