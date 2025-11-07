
#pragma once

#include "deb/deb_type.h"

#include "DebParam.hpp"
#include "Macro.h"
#include "Span.hpp"

#include <memory>
#include <variant>

// Define preset values and precomputed values from preset values.
#define CONST_LIST                                                             \
    CV(deb_preset_t, preset)                                                   \
    CV(deb_preset_t, parent)                                                   \
    CV(const char *, preset_name)                                              \
    CV(deb_size_t, rank)                                                       \
    CV(deb_size_t, num_secret)                                                 \
    CV(deb_size_t, log_degree)                                                 \
    CV(deb_size_t, degree)                                                     \
    CV(deb_size_t, num_slots)                                                  \
    CV(deb_size_t, gadget_rank)                                                \
    CV(deb_size_t, num_base)                                                   \
    CV(deb_size_t, num_qp)                                                     \
    CV(deb_size_t, num_tp)                                                     \
    CV(deb_size_t, num_p)                                                      \
    CV(deb_size_t, encryption_level)                                           \
    CV(deb_size_t, max_level)                                                  \
    CV(deb_size_t, hamming_weight)                                             \
    CV(deb_real, gaussian_error_stdev)                                         \
    CV(const deb_u64 *, primes)                                                \
    CV(const deb_real *, scale_factors)

namespace deb {

using deb_real = deb_real_t;
using deb_i32 = deb_i32_t;
using deb_i64 = deb_i64_t;
using deb_u32 = deb_u32_t;
using deb_u64 = deb_u64_t;

// Define the base Context struct
template <typename PRESET> struct ContextT : public PRESET {
#define CV(type, var_name)                                                     \
    static constexpr type get_##var_name() { return PRESET::var_name; }
    CONST_LIST
#undef CV
};

// Define VariantCtx using std::variant for all presets
using VariantCtx = std::variant<
#define X(PRESET) ContextT<PRESET>,
    DEB_PRESET_LIST
#undef X
        ContextT<EMPTY>>;

// Define the unified Context struct
struct Context {
    VariantCtx v;
#define CV(type, var_name)                                                     \
    constexpr type get_##var_name() const {                                    \
        return std::visit(                                                     \
            [](auto &&ctx) -> type { return ctx.get_##var_name(); }, v);       \
    }
    CONST_LIST
#undef CV
};

// Singleton ContextPool to manage Context instances
class ContextPool {
public:
    static ContextPool &getInstance() {
        static ContextPool instance;
        return instance;
    }

    std::shared_ptr<Context> get(deb_preset_t preset) {
        if (auto it = map_.find(preset); it != map_.end()) {
            return it->second;
        }
        throw std::runtime_error("Preset not found in ContextPool");
    }

private:
    ContextPool() {
#define X(PRESET)                                                              \
    map_[DEB_PRESET_##PRESET] =                                                \
        std::make_shared<Context>(Context{VariantCtx{ContextT<PRESET>{}}});
        DEB_PRESET_LIST
#undef X
    }
    std::unordered_map<deb_preset_t, std::shared_ptr<Context>> map_;
};

// Mapping from preset enum to preset struct
std::shared_ptr<Context> getContext(deb_preset_t preset);

// Check if the preset is valid
bool isValidPreset(deb_preset_t preset);

void setOmpThreadLimit(int max_threads);
void unsetOmpThreadLimit();

} // namespace deb
