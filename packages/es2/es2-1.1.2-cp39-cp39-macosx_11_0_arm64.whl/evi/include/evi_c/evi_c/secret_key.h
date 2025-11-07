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

void evi_secret_key_destroy(evi_secret_key_t *seckey);
evi_status_t evi_secret_key_create(const evi_context_t *context, evi_secret_key_t **out_key);
evi_status_t evi_secret_key_create_from_path(const char *path, evi_secret_key_t **out_key);
evi_status_t evi_secret_key_create_from_path_with_seal_info(const char *path, const evi_seal_info_t *seal_info,
                                                            evi_secret_key_t **out_key);

#ifdef __cplusplus
}
#endif
