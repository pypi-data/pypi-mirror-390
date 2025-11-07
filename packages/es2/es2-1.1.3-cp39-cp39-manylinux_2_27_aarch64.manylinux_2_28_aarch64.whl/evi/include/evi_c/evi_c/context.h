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

evi_status_t evi_context_create(evi_parameter_preset_t preset, evi_device_type_t device, uint64_t dim,
                                evi_eval_mode_t eval_mode, const int32_t *device_id, evi_context_t **out_context);

void evi_context_destroy(evi_context_t *context);

// getters
evi_device_type_t evi_context_get_device_type(const evi_context_t *context);

evi_eval_mode_t evi_context_get_eval_mode(const evi_context_t *context);

uint32_t evi_context_get_pad_rank(const evi_context_t *context);

uint32_t evi_context_get_show_dim(const evi_context_t *context);

double evi_context_get_scale_factor(const evi_context_t *context);

#ifdef __cplusplus
}
#endif
