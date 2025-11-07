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

void evi_query_destroy(evi_query_t *query);
void evi_query_array_destroy(evi_query_t **queries, size_t count);

evi_status_t evi_query_get_level(const evi_query_t *query, uint32_t *out_level);
evi_status_t evi_query_get_show_dim(const evi_query_t *query, uint32_t *out_show_dim);
evi_status_t evi_query_get_inner_item_count(const evi_query_t *query, uint32_t *out_count);
evi_status_t evi_query_get_block_count(const evi_query_t *query, size_t *out_count);

evi_status_t evi_query_serialize_to_path(const evi_query_t *query, const char *path);
evi_status_t evi_query_deserialize_from_path(const char *path, evi_query_t **out_query);
evi_status_t evi_query_serialize_to_stream(const evi_query_t *query, evi_stream_write_fn write_fn, void *handle);
evi_status_t evi_query_deserialize_from_stream(evi_stream_read_fn read_fn, void *handle, evi_query_t **out_query);
evi_status_t evi_query_serialize_to_string(const evi_query_t *query, char **out_data, size_t *out_size);
evi_status_t evi_query_deserialize_from_string(const char *data, size_t size, evi_query_t **out_query);

evi_status_t evi_query_vector_serialize_to_path(evi_query_t *const *queries, size_t count, const char *path);
evi_status_t evi_query_vector_deserialize_from_path(const char *path, evi_query_t ***out_queries, size_t *out_count);
evi_status_t evi_query_vector_serialize_to_stream(evi_query_t *const *queries, size_t count,
                                                  evi_stream_write_fn write_fn, void *handle);
evi_status_t evi_query_vector_deserialize_from_stream(evi_stream_read_fn read_fn, void *handle,
                                                      evi_query_t ***out_queries, size_t *out_count);
evi_status_t evi_query_vector_serialize_to_string(evi_query_t *const *queries, size_t count, char **out_data,
                                                  size_t *out_size);
evi_status_t evi_query_vector_deserialize_from_string(const char *data, size_t size, evi_query_t ***out_queries,
                                                      size_t *out_count);

#ifdef __cplusplus
}
#endif
