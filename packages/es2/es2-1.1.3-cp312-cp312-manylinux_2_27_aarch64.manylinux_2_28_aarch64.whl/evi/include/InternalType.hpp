#pragma once

#include "Context.hpp"
#include "Timer.hpp"
#include "deb/deb_type.h"

#include <algorithm>
#include <memory>
#include <optional>
#include <utility>
#include <vector>

namespace deb {

class deb_complex {
public:
    deb_complex() noexcept : r_(0), i_(0) {}
    constexpr deb_complex(const deb_real r, const deb_real i) noexcept
        : r_(r), i_(i) {}
    void real(const deb_real r) noexcept { r_ = r; }
    void imag(const deb_real i) noexcept { i_ = i; }
    deb_real &real() noexcept { return r_; }
    deb_real &imag() noexcept { return i_; }
    deb_real real() const noexcept { return r_; }
    deb_real imag() const noexcept { return i_; }

private:
    deb_real r_;
    deb_real i_;
};

class deb_message {
public:
    deb_message() = delete;
    explicit deb_message(const std::shared_ptr<Context> &context)
        : data_(context->get_num_slots()) {}
    explicit deb_message(const deb_size_t size) : data_(size) {}
    explicit deb_message(const deb_size_t size, const deb_complex &init)
        : data_(size, init) {}
    explicit deb_message(const deb_size_t size, const deb_complex *array)
        : data_(array, array + size) {}
    explicit deb_message(std::vector<deb_complex> data)
        : data_(std::move(data)) {}

    deb_complex &operator[](deb_size_t index) noexcept { return data_[index]; }
    deb_complex operator[](deb_size_t index) const noexcept {
        return data_[index];
    }
    deb_complex *data() noexcept { return data_.data(); }
    const deb_complex *data() const noexcept { return data_.data(); }
    deb_size_t size() const noexcept {
        return static_cast<deb_size_t>(data_.size());
    }

private:
    std::vector<deb_complex> data_;
};

class deb_coeff {
public:
    deb_coeff() = delete;
    explicit deb_coeff(const std::shared_ptr<Context> &context)
        : data_(context->get_degree()) {}
    explicit deb_coeff(const deb_size_t size) : data_(size) {}
    explicit deb_coeff(const deb_size_t size, const deb_real &init)
        : data_(size, init) {}
    explicit deb_coeff(const deb_size_t size, deb_real *array)
        : data_(array, array + size) {}
    explicit deb_coeff(std::vector<deb_real> data) : data_(std::move(data)) {}

    deb_real &operator[](deb_size_t index) noexcept { return data_[index]; }
    deb_real operator[](deb_size_t index) const noexcept {
        return data_[index];
    }
    deb_real *data() noexcept { return data_.data(); }
    const deb_real *data() const noexcept { return data_.data(); }
    deb_size_t size() const noexcept {
        return static_cast<deb_size_t>(data_.size());
    }

private:
    std::vector<deb_real> data_;
};

class deb_poly {
public:
    deb_poly() = delete;
    explicit deb_poly(const std::shared_ptr<deb::Context> &context,
                      const deb_size_t level)
        : prime_(context->get_primes()[level]), ntt_state_(false) {
#if DEB_ALINAS_LEN == 0
        data_ = std::shared_ptr<span<deb_u64>>(
            new span<deb_u64>(new deb_u64[context->get_degree()],
                              context->get_degree()),
            [](span<deb_u64> *p) { delete p; });
#else
        auto *buf = static_cast<deb_u64 *>(
            ::operator new[](sizeof(deb_u64) * context->get_degree(),
                             std::align_val_t(DEB_ALINAS_LEN)));
        data_ = std::shared_ptr<span<deb_u64>>(
            new span<deb_u64>(buf, context->get_degree()),
            [](span<deb_u64> *p) {
                ::operator delete[](p->data(),
                                    std::align_val_t(DEB_ALINAS_LEN));
                delete p;
            });
#endif
    }
    explicit deb_poly(deb_u64 prime, deb_size_t degree)
        : prime_(prime), ntt_state_(false) {
#if DEB_ALINAS_LEN == 0
        data_ = std::shared_ptr<span<deb_u64>>(
            new span<deb_u64>(new deb_u64[degree], degree),
            [](span<deb_u64> *p) { delete p; });
#else
        auto *buf = static_cast<deb_u64 *>(::operator new[](
            sizeof(deb_u64) * degree, std::align_val_t(DEB_ALINAS_LEN)));
        data_ = std::shared_ptr<span<deb_u64>>(
            new span<deb_u64>(buf, degree), [](span<deb_u64> *p) {
                ::operator delete[](p->data(),
                                    std::align_val_t(DEB_ALINAS_LEN));
                delete p;
            });
#endif
    }

    void set_prime(deb_u64 prime) noexcept { prime_ = prime; }
    deb_u64 &prime() noexcept { return prime_; }
    deb_u64 prime() const noexcept { return prime_; }
    void set_ntt(bool ntt_state) noexcept { ntt_state_ = ntt_state; }
    bool ntt_state() const noexcept { return ntt_state_; }
    bool is_ntt() const noexcept { return ntt_state_; }
    deb_size_t degree() const noexcept {
        return static_cast<deb_size_t>(data_->size());
    }
    deb_u64 &operator[](deb_size_t index) noexcept { return (*data_)[index]; }
    deb_u64 operator[](deb_size_t index) const noexcept {
        return (*data_)[index];
    }
    deb_u64 *data() noexcept { return data_->data(); }
    deb_u64 *data() const noexcept { return data_->data(); }
    // Set data pointer from outside of class
    // This method is for advanced users, with caution
    // The pointer should be allocated/deallocated outside of class
    void set_data(deb_u64 *new_data, deb_size_t size) {
        data_ =
            std::shared_ptr<span<deb_u64>>(new span<deb_u64>(new_data, size),
                                           [](span<deb_u64> *p) { delete p; });
    }

private:
    deb_u64 prime_;
    bool ntt_state_;
    std::shared_ptr<span<deb_u64>> data_;
};

class deb_bigpoly {
public:
    deb_bigpoly() = delete;
    explicit deb_bigpoly(std::shared_ptr<deb::Context> context,
                         const bool full_level = false) {
        deb_size_t num_poly = full_level ? context->get_num_p()
                                         : context->get_encryption_level() + 1;
        for (deb_size_t l = 0; l < num_poly; ++l) {
            data_.emplace_back(context, l);
        }
    }
    explicit deb_bigpoly(std::shared_ptr<deb::Context> context,
                         const deb_size_t custom_size) {
        for (deb_size_t l = 0; l < custom_size; ++l) {
            data_.emplace_back(context, l);
        }
    }
    explicit deb_bigpoly(const deb_bigpoly &other, deb_size_t others_idx,
                         deb_size_t custom_size = 1)
        : data_(&other.data_[others_idx],
                &other.data_[others_idx] + custom_size) {}

    void set_level(deb_preset_t preset, deb_size_t level) {
        resize(preset, level + 1);
    }
    void resize(deb_preset_t preset, deb_size_t size) {
        const auto context = getContext(preset);
        if (size <= this->size()) {
            data_.erase(data_.begin() + size, data_.end());
        } else {
            const auto max_len = context->get_num_p();
            for (deb_size_t l = this->size(); l < size; ++l) {
                data_.emplace_back(context->get_primes()[l % max_len],
                                   context->get_degree());
            }
        }
    }
    void set_ntt(bool ntt_state) noexcept {
        for (auto &poly : data_) {
            poly.set_ntt(ntt_state);
        }
    }
    deb_size_t size() const noexcept {
        return static_cast<deb_size_t>(data_.size());
    }
    deb_size_t level() const noexcept {
        return static_cast<deb_size_t>(data_.size());
    }
    deb_poly &operator[](size_t index) noexcept { return data_[index]; }
    const deb_poly &operator[](size_t index) const noexcept {
        return data_[index];
    }
    deb_poly *data() noexcept { return data_.data(); }
    const deb_poly *data() const noexcept { return data_.data(); }

private:
    std::vector<deb_poly> data_;
};

class deb_cipher {
public:
    deb_cipher() = delete;
    explicit deb_cipher(std::shared_ptr<deb::Context> context)
        : preset_(context->get_preset()), encoding_(DEB_ENCODING_SLOT) {
        const deb_size_t num_bigpolys =
            context->get_rank() * context->get_num_secret() + 1;
        for (deb_size_t i = 0; i < num_bigpolys; ++i) {
            data_.emplace_back(context);
        }
    }
    explicit deb_cipher(std::shared_ptr<deb::Context> context,
                        const deb_size_t level, const deb_size_t size = 0)
        : preset_(context->get_preset()), encoding_(DEB_ENCODING_UNKNOWN) {
        const auto num_bigpolys =
            size == 0 ? context->get_rank() * context->get_num_secret() + 1
                      : size;
        for (deb_size_t i = 0; i < num_bigpolys; ++i) {
            data_.emplace_back(context, level + 1);
        }
    }
    explicit deb_cipher(const deb_cipher &other, deb_size_t others_idx)
        : preset_(other.preset_), encoding_(other.encoding_),
          data_({other.data_[others_idx]}) {}

    void set_encoding(deb_encoding_t encoding) { this->encoding_ = encoding; }
    void set_ntt(bool ntt_state) {
        for (auto &bigpoly : data_) {
            bigpoly.set_ntt(ntt_state);
        }
    }
    deb_preset_t preset() const noexcept { return preset_; }
    deb_encoding_t &encoding() noexcept { return encoding_; }
    deb_encoding_t encoding() const noexcept { return encoding_; }
    bool is_slot() const noexcept { return encoding_ == DEB_ENCODING_SLOT; }
    bool is_coeff() const noexcept { return encoding_ == DEB_ENCODING_COEFF; }
    bool is_swk() const noexcept { return encoding_ == DEB_ENCODING_SWK; }
    void set_level(deb_size_t level) {
        std::for_each(data_.begin(), data_.end(), [this, level](auto &bigpoly) {
            bigpoly.set_level(preset_, level);
        });
    }
    void set_poly_size(deb_size_t size) {
        std::for_each(data_.begin(), data_.end(), [this, size](auto &bigpoly) {
            bigpoly.resize(preset_, size);
        });
    }
    deb_size_t size() const noexcept {
        return static_cast<deb_size_t>(data_.size());
    }
    deb_bigpoly &operator[](size_t index) noexcept { return data_[index]; }
    const deb_bigpoly &operator[](size_t index) const noexcept {
        return data_[index];
    }
    deb_bigpoly *data() noexcept { return data_.data(); }
    const deb_bigpoly *data() const noexcept { return data_.data(); }

private:
    deb_preset_t preset_;
    deb_encoding_t encoding_;
    std::vector<deb_bigpoly> data_;
};

class deb_sk {
public:
    deb_sk() = delete;
    explicit deb_sk(std::shared_ptr<deb::Context> context)
        : preset_(context->get_preset()),
          coeffs_(context->get_rank() * context->get_num_secret() *
                  context->get_degree()) {
        const deb_size_t num_bigpoly =
            context->get_rank() * context->get_num_secret();
        for (deb_size_t i = 0; i < num_bigpoly; ++i) {
            bigpolys_.emplace_back(context, true);
        }
    }

    deb_preset_t preset() const noexcept { return preset_; }
    bool check_preset(const deb_preset_t preset) const noexcept {
        return preset_ == preset;
    }
    deb_size_t coeffs_size() noexcept {
        return static_cast<deb_size_t>(coeffs_.size());
    }
    deb_size_t coeffs_size() const noexcept {
        return static_cast<deb_size_t>(coeffs_.size());
    }
    int8_t &coeff(deb_size_t index) noexcept { return coeffs_[index]; }
    int8_t coeff(deb_size_t index) const noexcept { return coeffs_[index]; }
    int8_t *coeffs() noexcept { return coeffs_.data(); }
    const int8_t *coeffs() const noexcept { return coeffs_.data(); }
    deb_size_t size() noexcept {
        return static_cast<deb_size_t>(bigpolys_.size());
    }
    deb_size_t size() const noexcept {
        return static_cast<deb_size_t>(bigpolys_.size());
    }
    deb_bigpoly &operator[](deb_size_t index) { return bigpolys_[index]; }
    const deb_bigpoly &operator[](deb_size_t index) const {
        return bigpolys_[index];
    }
    deb_bigpoly *data() noexcept { return bigpolys_.data(); }
    const deb_bigpoly *data() const noexcept { return bigpolys_.data(); }

private:
    deb_preset_t preset_;
    std::vector<int8_t> coeffs_;
    std::vector<deb_bigpoly> bigpolys_;
};

class deb_swk {
public:
    deb_swk() = delete;
    explicit deb_swk(const std::shared_ptr<deb::Context> &context,
                     const deb_swk_kind_t type,
                     const std::optional<deb_size_t> rot_idx = std::nullopt)
        : context_(context), type_(type), rot_idx_(rot_idx),
          dnum_(context->get_gadget_rank()) {}

    deb_preset_t preset() const noexcept { return context_->get_preset(); }
    deb_swk_kind_t &type() noexcept { return type_; }
    deb_swk_kind_t type() const noexcept { return type_; }
    void set_rot_idx(deb_size_t rot_idx) noexcept { rot_idx_.emplace(rot_idx); }
    deb_size_t rot_idx() const noexcept {
        if (rot_idx_)
            return rot_idx_.value();
        return static_cast<deb_size_t>(-1);
    }
    deb_size_t &dnum() noexcept { return dnum_; }
    deb_size_t dnum() const noexcept { return dnum_; }
    void add_ax(const deb_size_t poly_size, const deb_size_t size = 1,
                const bool ntt_state = false) {
        for (deb_size_t i = 0; i < size; ++i) {
            ax_.emplace_back(context_, poly_size);
        }
        set_ax_ntt(ntt_state);
    }
    void add_ax(const deb_bigpoly &poly) { ax_.push_back(poly); }
    void add_bx(const deb_size_t poly_size, const deb_size_t size = 0,
                const bool ntt_state = false) {
        const auto num_bigpoly =
            size == 0 ? dnum_ * context_->get_num_secret() : size;
        for (deb_size_t i = 0; i < num_bigpoly; ++i) {
            bx_.emplace_back(context_, poly_size);
        }
        set_bx_ntt(ntt_state);
    }
    void add_bx(const deb_bigpoly &poly) { bx_.push_back(poly); }
    void set_ax_ntt(bool ntt_state) noexcept {
        for (auto &bigpoly : ax_) {
            bigpoly.set_ntt(ntt_state);
        }
    }
    void set_bx_ntt(bool ntt_state) noexcept {
        for (auto &bigpoly : bx_) {
            bigpoly.set_ntt(ntt_state);
        }
    }
    deb_size_t ax_size() const noexcept {
        return static_cast<deb_size_t>(ax_.size());
    }
    deb_size_t bx_size() noexcept {
        return static_cast<deb_size_t>(bx_.size());
    }
    deb_size_t bx_size() const noexcept {
        return static_cast<deb_size_t>(bx_.size());
    }
    std::vector<deb_bigpoly> &get_ax() noexcept { return ax_; }
    const std::vector<deb_bigpoly> &get_ax() const noexcept { return ax_; }
    std::vector<deb_bigpoly> &get_bx() noexcept { return bx_; }
    const std::vector<deb_bigpoly> &get_bx() const noexcept { return bx_; }
    deb_bigpoly &ax(deb_size_t index = 0) noexcept { return ax_[index]; }
    const deb_bigpoly &ax(deb_size_t index = 0) const noexcept {
        return ax_[index];
    }
    deb_bigpoly &bx(deb_size_t index = 0) noexcept { return bx_[index]; }
    const deb_bigpoly &bx(deb_size_t index = 0) const noexcept {
        return bx_[index];
    }

private:
    std::shared_ptr<Context> context_;
    deb_swk_kind_t type_;
    std::optional<deb_size_t> rot_idx_;
    deb_size_t dnum_;
    std::vector<deb_bigpoly> ax_;
    std::vector<deb_bigpoly> bx_;
};

inline deb_u64 *get_data(const deb_cipher &cipher, const deb_size_t poly_idx,
                         const deb_size_t bigpoly_idx = 0) {
    if (bigpoly_idx >= cipher.size() ||
        poly_idx >= cipher[bigpoly_idx].size()) {
        throw std::out_of_range("Index out of range in get_data");
    }
    return cipher[bigpoly_idx][poly_idx].data();
}

inline deb_u64 *get_data(const deb_bigpoly &poly,
                         const deb_size_t poly_idx = 0) {
    if (poly_idx >= poly.size()) {
        throw std::out_of_range("Index out of range in get_data");
    }
    return poly[poly_idx].data();
}

inline deb_u64 get_data(const deb_u64 *data, const deb_size_t idx = 0) {
    return data[idx];
}

} // namespace deb
