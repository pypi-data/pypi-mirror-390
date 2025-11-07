#pragma once

#include <cassert>
#include <cstdint>
#include <stdexcept>

// https://gcc.gnu.org/onlinedocs/cpp/Common-Predefined-Macros.html
#define GCC_VERSION                                                            \
    (__GNUC__ * 10000 + __GNUC_MINOR__ * 100 + __GNUC_PATCHLEVEL__)

#if defined(__clang__)
#define DEB_LOOP_UNROLL_2 _Pragma("clang loop unroll_count(2)")
#define DEB_LOOP_UNROLL_4 _Pragma("clang loop unroll_count(4)")
#define DEB_LOOP_UNROLL_8 _Pragma("clang loop unroll_count(8)")
#elif defined(__GNUG__) && GCC_VERSION > 80000 && !defined(__NVCC__)
#define DEB_LOOP_UNROLL_2 _Pragma("GCC unroll 2")
#define DEB_LOOP_UNROLL_4 _Pragma("GCC unroll 4")
#define DEB_LOOP_UNROLL_8 _Pragma("GCC unroll 8")
#else
#define DEB_LOOP_UNROLL_2
#define DEB_LOOP_UNROLL_4
#define DEB_LOOP_UNROLL_8
#endif

#define STR(x) #x
#define STRINGIFY(x) STR(x)
#define CONCATENATE(X, Y) X(Y)
#if defined(_MSC_VER) && !defined(__INTEL_COMPILER)
#define PRAGMA(x) __pragma(x)
#else
#define PRAGMA(x) _Pragma(STRINGIFY(x))
#endif

#ifdef _MSC_VER
#define DEB_RESTRICT __restrict
#else
#define DEB_RESTRICT __restrict__
#endif

#ifdef DEB_RESOURCE_CHECK
#ifdef NDEBUG
#define deb_assert(condition, message)                                         \
    do {                                                                       \
        if (!(condition)) {                                                    \
            throw std::runtime_error((message));                               \
        }                                                                      \
    } while (0)
#else
#define deb_assert(condition, message)                                         \
    do {                                                                       \
        assert((condition) && (message));                                      \
    } while (0)
#endif
#else
#define deb_assert(condition, message)                                         \
    do {                                                                       \
    } while (0)
#endif
