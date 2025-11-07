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

void evi_search_result_destroy(evi_search_result_t *result);
evi_status_t evi_search_result_get_item_count(const evi_search_result_t *result, uint32_t *out_count);
evi_status_t evi_search_result_serialize_to_path(const evi_search_result_t *result, const char *path);
evi_status_t evi_search_result_deserialize_from_path(const char *path, evi_search_result_t **out_result);
evi_status_t evi_search_result_serialize_to_stream(const evi_search_result_t *result, evi_stream_write_fn write_fn,
                                                   void *handle);
evi_status_t evi_search_result_deserialize_from_stream(evi_stream_read_fn read_fn, void *handle,
                                                       evi_search_result_t **out_result);
evi_status_t evi_search_result_serialize_to_string(const evi_search_result_t *result, char **out_data,
                                                   size_t *out_size);
evi_status_t evi_search_result_deserialize_from_string(const char *data, size_t size, evi_search_result_t **out_result);

#ifdef __cplusplus
}
#endif
