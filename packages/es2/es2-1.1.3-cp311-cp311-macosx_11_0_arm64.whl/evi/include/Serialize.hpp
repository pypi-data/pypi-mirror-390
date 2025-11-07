#pragma once

#include "DebFBType.h"
#include "InternalType.hpp"

#include <sstream>

namespace deb {

template <typename T> using Vector = flatbuffers::Vector<T>;

std::vector<deb_fb::Complex> toComplexVector(const deb_complex *data,
                                             const deb_size_t size);
std::vector<deb_complex>
toDebComplexVector(const Vector<const deb_fb::Complex *> *data);

flatbuffers::Offset<deb_fb::Message>
serializeMessage(flatbuffers::FlatBufferBuilder &builder,
                 const deb_message &message);
deb_message deserializeMessage(const deb_fb::Message *message);

flatbuffers::Offset<deb_fb::Coeff>
serializeCoeff(flatbuffers::FlatBufferBuilder &builder, const deb_coeff &coeff);

deb_coeff deserializeCoeff(const deb_fb::Coeff *coeff);

flatbuffers::Offset<deb_fb::Poly>
serializePoly(flatbuffers::FlatBufferBuilder &builder, const deb_poly &poly);

deb_poly deserializePoly(const deb_fb::Poly *poly);

flatbuffers::Offset<deb_fb::Bigpoly>
serializeBigpoly(flatbuffers::FlatBufferBuilder &builder,
                 const deb_bigpoly &bigpoly);

deb_bigpoly deserializeBigpoly(deb_preset_t preset,
                               const deb_fb::Bigpoly *bigpoly);

flatbuffers::Offset<deb_fb::Cipher>
serializeCipher(flatbuffers::FlatBufferBuilder &builder,
                const deb_cipher &cipher);

deb_cipher deserializeCipher(const deb_fb::Cipher *cipher);

flatbuffers::Offset<deb_fb::Sk>
serializeSk(flatbuffers::FlatBufferBuilder &builder, const deb_sk &sk);

deb_sk deserializeSk(const deb_fb::Sk *sk);

flatbuffers::Offset<deb_fb::Swk>
serializeSwk(flatbuffers::FlatBufferBuilder &builder, const deb_swk &swk);

deb_swk deserializeSwk(const deb_fb::Swk *swk);

template <typename T>
void appendOffsetToVector(const flatbuffers::Offset<T> &offset,
                          std::vector<uint8_t> &type_vec,
                          std::vector<flatbuffers::Offset<void>> &value_vec) {
    if constexpr (std::is_same_v<T, deb_fb::Swk>) {
        type_vec.push_back(deb_fb::DebUnion_Swk);
    } else if constexpr (std::is_same_v<T, deb_fb::Sk>) {
        type_vec.push_back(deb_fb::DebUnion_Sk);
    } else if constexpr (std::is_same_v<T, deb_fb::Cipher>) {
        type_vec.push_back(deb_fb::DebUnion_Cipher);
    } else if constexpr (std::is_same_v<T, deb_fb::Bigpoly>) {
        type_vec.push_back(deb_fb::DebUnion_Bigpoly);
    } else if constexpr (std::is_same_v<T, deb_fb::Poly>) {
        type_vec.push_back(deb_fb::DebUnion_Poly);
    } else if constexpr (std::is_same_v<T, deb_fb::Message>) {
        type_vec.push_back(deb_fb::DebUnion_Message);
    } else if constexpr (std::is_same_v<T, deb_fb::Coeff>) {
        type_vec.push_back(deb_fb::DebUnion_Coeff);
    } else {
        throw std::runtime_error(
            "[appendOffsetToVector] Unsupported type for serialization");
    }
    value_vec.push_back(flatbuffers::Offset<void>(offset.Union()));
}

template <typename T>
flatbuffers::Offset<deb_fb::Deb> toDeb(flatbuffers::FlatBufferBuilder &builder,
                                       const flatbuffers::Offset<T> &offset) {
    std::vector<uint8_t> type_vec;
    std::vector<flatbuffers::Offset<void>> value_vec;

    appendOffsetToVector(offset, type_vec, value_vec);

    return deb_fb::CreateDeb(builder, builder.CreateVector(type_vec),
                             builder.CreateVector(value_vec));
}

template <typename T> void serializeToStream(const T &data, std::ostream &os) {
    flatbuffers::FlatBufferBuilder builder;
    if constexpr (std::is_same_v<T, deb_swk>) {
        builder.Finish(toDeb(builder, serializeSwk(builder, data)));
    } else if constexpr (std::is_same_v<T, deb_sk>) {
        builder.Finish(toDeb(builder, serializeSk(builder, data)));
    } else if constexpr (std::is_same_v<T, deb_cipher>) {
        builder.Finish(toDeb(builder, serializeCipher(builder, data)));
    } else if constexpr (std::is_same_v<T, deb_bigpoly>) {
        builder.Finish(toDeb(builder, serializeBigpoly(builder, data)));
    } else if constexpr (std::is_same_v<T, deb_poly>) {
        builder.Finish(toDeb(builder, serializePoly(builder, data)));
    } else if constexpr (std::is_same_v<T, deb_message>) {
        builder.Finish(toDeb(builder, serializeMessage(builder, data)));
    } else if constexpr (std::is_same_v<T, deb_coeff>) {
        builder.Finish(toDeb(builder, serializeCoeff(builder, data)));
    } else {
        throw std::runtime_error(
            "[serializeToStream] Unsupported type for serialization");
    }
    deb_size_t size = builder.GetSize();
    os.write(reinterpret_cast<const char *>(&size), sizeof(deb_size_t));
    os.write(reinterpret_cast<const char *>(builder.GetBufferPointer()),
             builder.GetSize());
}

template <typename T>
void deserializeFromStream(std::istream &is, T &data,
                           std::optional<deb_preset_t> preset = std::nullopt) {
    deb_size_t size;
    is.read(reinterpret_cast<char *>(&size), sizeof(deb_size_t));
    deb_assert(size > 0,
               "[deserializeFromStream] Invalid size for deserialization");
    std::vector<uint8_t> buffer(size);
    is.read(reinterpret_cast<char *>(buffer.data()), size);
    flatbuffers::Verifier verifier(buffer.data(), buffer.size());
    deb_assert(deb_fb::VerifyDebBuffer(verifier),
               "[deserializeFromStream] Invalid buffer for deserialization");
    const auto *deb = deb_fb::GetDeb(buffer.data());
    deb_assert(deb->list()->size() == 1,
               "[deserializeFromStream] Invalid Deb buffer: expected exactly "
               "one element");
    if constexpr (std::is_same_v<T, deb_swk>) {
        data = deserializeSwk(deb->list()->GetAs<deb_fb::Swk>(0));
    } else if constexpr (std::is_same_v<T, deb_sk>) {
        data = deserializeSk(deb->list()->GetAs<deb_fb::Sk>(0));
    } else if constexpr (std::is_same_v<T, deb_cipher>) {
        data = deserializeCipher(deb->list()->GetAs<deb_fb::Cipher>(0));
    } else if constexpr (std::is_same_v<T, deb_bigpoly>) {
        if (!preset.has_value()) {
            throw std::runtime_error("[deserializeFromStream] Preset must be "
                                     "provided for deserializing deb_bigpoly");
        }
        data = deserializeBigpoly(preset.value(),
                                  deb->list()->GetAs<deb_fb::Bigpoly>(0));
    } else if constexpr (std::is_same_v<T, deb_poly>) {
        data = deserializePoly(deb->list()->GetAs<deb_fb::Poly>(0));
    } else if constexpr (std::is_same_v<T, deb_message>) {
        data = deserializeMessage(deb->list()->GetAs<deb_fb::Message>(0));
    } else if constexpr (std::is_same_v<T, deb_coeff>) {
        data = deserializeCoeff(deb->list()->GetAs<deb_fb::Coeff>(0));
    } else {
        throw std::runtime_error(
            "[deserializeFromStream] Unsupported type for deserialization");
    }
}
} // namespace deb
