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

evi_status_t evi_encryptor_create(const evi_context_t *context, evi_encryptor_t **out_encryptor);
void evi_encryptor_destroy(evi_encryptor_t *encryptor);

// encode
// input : 1 data, output : 1 query
evi_status_t evi_encryptor_encode_vector(const evi_encryptor_t *encryptor, const float *data, size_t dim,
                                         evi_encode_type_t encode_type, int level, const float *scale,
                                         evi_query_t **out_query);

// input : batch data, output : batch queries
evi_status_t evi_encryptor_encode_batch(const evi_encryptor_t *encryptor, const float *const *data, const size_t dim,
                                        size_t data_count, evi_encode_type_t encode_type, int level, const float *scale,
                                        evi_query_t ***out_queries, size_t *out_count);

// input : batch data, output : 1 query
evi_status_t evi_encryptor_encode_vectors(const evi_encryptor_t *encryptor, const float *const *data, const size_t dim,
                                          size_t data_count, evi_encode_type_t encode_type, int level,
                                          const float *scale, evi_query_t **out_query);

// encrypt
// input : 1 data, output : 1 query
evi_status_t evi_encryptor_encrypt_vector_with_path(const evi_encryptor_t *encryptor, const char *enckey_path,
                                                    const float *data, size_t dim, evi_encode_type_t encode_type,
                                                    int level, const float *scale, evi_query_t **out_query);

// input : 1 data, output : 1 query
evi_status_t evi_encryptor_encrypt_vector_with_pack(const evi_encryptor_t *encryptor, const evi_keypack_t *pack,
                                                    const float *data, size_t dim, evi_encode_type_t encode_type,
                                                    int level, const float *scale, evi_query_t **out_query);

// input : batch data, output : batch query
evi_status_t evi_encryptor_encrypt_batch_with_path(const evi_encryptor_t *encryptor, const char *enckey_path,
                                                   const float *const *data, const size_t dim, size_t data_count,
                                                   evi_encode_type_t encode_type, int level, const float *scale,
                                                   evi_query_t ***out_queries, size_t *out_count);

// input : batch data, output : batch query
evi_status_t evi_encryptor_encrypt_batch_with_pack(const evi_encryptor_t *encryptor, const evi_keypack_t *pack,
                                                   const float *const *data, const size_t dim, size_t data_count,
                                                   evi_encode_type_t encode_type, int level, const float *scale,
                                                   evi_query_t ***out_queries, size_t *out_count);

#ifdef __cplusplus
}
#endif
