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

evi_status_t evi_index_create(const evi_context_t *context, evi_data_type_t data_type, evi_index_t **out_index);
void evi_index_destroy(evi_index_t *index);

evi_status_t evi_index_append(evi_index_t *index, const evi_query_t *item);

evi_status_t evi_index_batch_append(evi_index_t *index, evi_query_t *const *items, size_t count, uint64_t **out_ids,
                                    size_t *out_count);

evi_status_t evi_index_serialize_to_path(const evi_index_t *index, const char *path);
evi_status_t evi_index_deserialize_from_path(evi_index_t *index, const char *path);

evi_status_t evi_index_get_show_dim(const evi_index_t *index, uint32_t *out_show_dim);
evi_status_t evi_index_get_item_count(const evi_index_t *index, uint32_t *out_count);
evi_status_t evi_index_get_level(const evi_index_t *index, int *out_level);

void evi_index_query_array_destroy(evi_query_t **queries, size_t count);
void evi_index_id_array_destroy(uint64_t *ids);

#ifdef __cplusplus
}
#endif
