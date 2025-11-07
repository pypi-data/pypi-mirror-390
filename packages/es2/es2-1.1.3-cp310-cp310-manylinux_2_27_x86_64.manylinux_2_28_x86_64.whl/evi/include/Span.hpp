#pragma once

#include <array>
#include <cstdint>
#include <vector>

namespace deb {
template <typename T> class span {
public:
    constexpr span(const T *ptr, std::size_t size) noexcept
        : ptr_(ptr), size_(size) {}

    constexpr span(const T *ptr) : ptr_(ptr), size_(1) {}

    constexpr span(const std::vector<T> &vec)
        : ptr_(vec.data()), size_(vec.size()) {}

    template <uint32_t N>
    constexpr span(const std::array<T, N> &arr) noexcept
        : ptr_(arr.data()), size_(N) {}

    constexpr const T *begin() const noexcept { return ptr_; }
    constexpr const T *end() const noexcept { return ptr_ + size_; }

    constexpr T *begin() noexcept { return const_cast<T *>(ptr_); }
    constexpr T *end() noexcept { return const_cast<T *>(ptr_ + size_); }

    constexpr std::size_t size() const noexcept { return size_; }

    constexpr T &operator[](std::size_t index) {
        return const_cast<T &>(ptr_[index]);
    }

    const T &operator[](std::size_t index) const { return ptr_[index]; }

    constexpr T *data() const noexcept { return const_cast<T *>(ptr_); }

    constexpr span<T>
    subspan(std::size_t offset,
            std::size_t count = static_cast<std::size_t>(-1)) const {
        if (offset >= size_)
            return span<T>(ptr_, 0);
        std::size_t new_size =
            (count == static_cast<std::size_t>(-1)) ? (size_ - offset) : count;
        return span<T>(ptr_ + offset, std::min(new_size, size_ - offset));
    }

private:
    const T *ptr_;
    const std::size_t size_;
};
} // namespace deb
