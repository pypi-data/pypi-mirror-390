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

evi_status_t evi_compute_buffer_create(const evi_context_t *context, evi_compute_buffer_t **out_buffer);
void evi_compute_buffer_destroy(evi_compute_buffer_t *buffer);
evi_status_t evi_compute_buffer_get_context(const evi_compute_buffer_t *buffer, evi_context_t **out_context);

#ifdef __cplusplus
}
#endif
