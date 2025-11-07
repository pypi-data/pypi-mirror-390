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

evi_status_t evi_keypack_create(const evi_context_t *context, evi_keypack_t **out_pack);
evi_status_t evi_keypack_create_from_path(const evi_context_t *context, const char *directory,
                                          evi_keypack_t **out_pack);
void evi_keypack_destroy(evi_keypack_t *pack);

evi_status_t evi_keypack_save_enc_key(evi_keypack_t *pack, const char *path);
evi_status_t evi_keypack_load_enc_key(evi_keypack_t *pack, const char *path);
evi_status_t evi_keypack_save_eval_key(evi_keypack_t *pack, const char *path);
evi_status_t evi_keypack_load_eval_key(evi_keypack_t *pack, const char *path);

#ifdef __cplusplus
}
#endif
