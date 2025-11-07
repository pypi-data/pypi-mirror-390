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

// keygenerator
evi_status_t evi_keygenerator_create(const evi_context_t *context, evi_keypack_t *pack,
                                     evi_keygenerator_t **out_keygen);
void evi_keygenerator_destroy(evi_keygenerator_t *keygen);
evi_status_t evi_keygenerator_generate_secret_key(evi_keygenerator_t *keygen, evi_secret_key_t **out_key);
evi_status_t evi_keygenerator_generate_public_keys(evi_keygenerator_t *keygen, evi_secret_key_t *seckey);

// seal info
evi_status_t evi_seal_info_create(evi_seal_mode_t mode, const uint8_t *key_data, size_t key_length,
                                  evi_seal_info_t **out_info);
void evi_seal_info_destroy(evi_seal_info_t *info);

// MultiKeyGenerator
evi_status_t evi_multikeygenerator_create(const evi_context_t *const *contexts, size_t count, const char *directory,
                                          const evi_seal_info_t *seal_info, evi_multikeygenerator_t **out_keygen);
void evi_multikeygenerator_destroy(evi_multikeygenerator_t *keygen);
evi_status_t evi_multikeygenerator_check_file_exist(evi_multikeygenerator_t *keygen, int *out_exists);
evi_status_t evi_multikeygenerator_generate_keys(evi_multikeygenerator_t *keygen, evi_secret_key_t **out_key);

#ifdef __cplusplus
}
#endif
