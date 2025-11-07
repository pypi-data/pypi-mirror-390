#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include "json.hpp" // nlohmann/json (https://github.com/nlohmann/json)
using json = nlohmann::json;

static inline uint64_t bitWidth(uint64_t op) {
    uint64_t n = 64;
    uint64_t tmp = op >> 32;
    if (tmp != 0) {
        n = n - 32;
        op = tmp;
    }
    tmp = op >> 16;
    if (tmp != 0) {
        n = n - 16;
        op = tmp;
    }
    tmp = op >> 8;
    if (tmp != 0) {
        n = n - 8;
        op = tmp;
    }
    tmp = op >> 4;
    if (tmp != 0) {
        n = n - 4;
        op = tmp;
    }
    tmp = op >> 2;
    if (tmp != 0) {
        n = n - 2;
        op = tmp;
    }
    tmp = op >> 1;
    if (tmp != 0)
        return 62 - n;

    return UINT64_C(0);
}

static uint32_t get_u32(const json &j, const char *key, bool &has,
                        uint32_t def) {
    if (j.contains(key)) {
        has = true;
        return j.at(key).get<uint32_t>();
    }
    has = false;
    return def;
}
static std::string get_str(const json &j, const char *key, bool &has,
                           const std::string &def = {}) {
    if (j.contains(key)) {
        has = true;
        return j.at(key).get<std::string>();
    }
    has = false;
    return def;
}

struct RawPreset {
    // direct as read from JSON (optional)
    std::string NAME;
    std::string PARENT; // optional
    bool has_PARENT = false;

    uint32_t LOG_DEGREE = 0;
    bool has_LOG_DEGREE = false;
    uint32_t NUM_BASE = 1;
    bool has_NUM_BASE = false;
    uint32_t NUM_QP = 0;
    bool has_NUM_QP = false;
    uint32_t NUM_TP = 0;
    bool has_NUM_TP = false;
    uint32_t ENC_LEVEL = 0;
    bool has_ENC_LEVEL = false;
    uint32_t HWT = 0;
    bool has_HWT = false;

    uint32_t RANK = 1;
    bool has_RANK = false;
    uint32_t NUM_SECRET = 1;
    bool has_NUM_SECRET = false;
    uint32_t GADGET_RANK = 1;
    bool has_GADGET_RANK = false;

    std::vector<uint64_t> PRIMES;
    bool has_PRIMES = false;
    std::vector<double> SCALE_FACTORS;
    bool has_SCALE_FACTORS = false;
};

struct FinalPreset {
    // fully-resolved (after inheritance)
    std::string NAME;
    std::string PARENT; // may be empty (== self or none)
    uint32_t LOG_DEGREE = 0;
    uint32_t NUM_BASE = 1;
    uint32_t NUM_QP = 0;
    uint32_t NUM_TP = 0;
    uint32_t ENC_LEVEL = 0;
    uint32_t HWT = 0;
    uint32_t MAX_LEVEL = 0;
    uint32_t RANK = 1;
    uint32_t NUM_SECRET = 1;
    uint32_t GADGET_RANK = 1;
    std::vector<uint64_t> PRIMES;
    // precomputed values
    std::vector<double> SCALE_FACTORS;
    // FOR FFT
    std::vector<uint64_t> POWER_OF_FIVE;
    std::vector<uint64_t> ROOTS;
    std::vector<uint64_t> ROOTS_INV;
    std::vector<uint64_t> ROOTS_COMPLEX;
    // FOR NTT
    std::vector<uint64_t> DEGREE_INV;
    std::vector<uint64_t> DEGREE_INV_BARRETT;
    std::vector<uint64_t> DEGREE_INV_W;
    std::vector<uint64_t> DEGREE_INV_W_BARRETT;
    std::vector<std::vector<uint64_t>> NTT_PSI;
    std::vector<std::vector<uint64_t>> NTT_PSI_INV;
    std::vector<std::vector<uint64_t>> NTT_PSI_SHOUP;
    std::vector<std::vector<uint64_t>> NTT_PSI_INV_SHOUP;
    // FOR KEYGEN
    std::vector<uint64_t> P_MOP;
    std::vector<uint64_t> HAT_Q_MOD;
    std::vector<uint64_t> HAT_Q_INV_MOD;
    // FOR ModuloArithmetic
    std::vector<uint64_t> BARRETT_RATIO;
    std::vector<uint64_t> BARRETT_EXPT;
};

static RawPreset parse_raw_preset(const json &j) {
    RawPreset r;
    if (j.contains("NAME")) {
        r.NAME = j.at("NAME").get<std::string>();
    }
    r.PARENT = get_str(j, "PARENT", r.has_PARENT);
    r.LOG_DEGREE = get_u32(j, "LOG_DEGREE", r.has_LOG_DEGREE, r.LOG_DEGREE);
    r.NUM_BASE = get_u32(j, "NUM_BASE", r.has_NUM_BASE, r.NUM_BASE);
    r.NUM_QP = get_u32(j, "NUM_QP", r.has_NUM_QP, r.NUM_QP);
    r.NUM_TP = get_u32(j, "NUM_TP", r.has_NUM_TP, r.NUM_TP);
    r.ENC_LEVEL = get_u32(j, "ENC_LEVEL", r.has_ENC_LEVEL, r.ENC_LEVEL);
    r.HWT = get_u32(j, "HWT", r.has_HWT, r.HWT);
    r.RANK = get_u32(j, "RANK", r.has_RANK, r.RANK);
    r.NUM_SECRET = get_u32(j, "NUM_SECRET", r.has_NUM_SECRET, r.NUM_SECRET);
    r.GADGET_RANK = get_u32(j, "GADGET_RANK", r.has_GADGET_RANK, r.GADGET_RANK);

    if (j.contains("PRIMES")) {
        r.has_PRIMES = true;
        for (const auto &v : j.at("PRIMES")) {
            // accept number (assumed fits uint64)
            r.PRIMES.push_back(v.get<uint64_t>());
        }
    }
    if (j.contains("SCALE_FACTORS")) {
        r.has_SCALE_FACTORS = true;
        for (const auto &v : j.at("SCALE_FACTORS")) {
            r.SCALE_FACTORS.push_back(v.get<double>());
        }
    }
    return r;
}

static std::vector<double>
compute_scale_factors(const size_t max_level, const size_t enc_level,
                      const std::vector<uint64_t> &primes) {
    std::vector<double> scale_factors;
    if (max_level > 0) {
        const uint64_t high_prime_bit = bitWidth(primes[enc_level + 1]);
        const uint64_t low_prime_bit = bitWidth(primes[enc_level]);

        scale_factors.resize(max_level + 1);
        scale_factors[max_level] =
            std::log2(primes[0]) +
            static_cast<double>(high_prime_bit - bitWidth(primes[0]));

        for (size_t i = max_level; i != 0; --i) {
            uint64_t shift = (i > enc_level)
                                 ? high_prime_bit - bitWidth(primes[i])
                                 : low_prime_bit - bitWidth(primes[i]);
            if (i == enc_level + 1)
                shift += high_prime_bit - low_prime_bit;

            scale_factors[i - 1] = 2 * scale_factors[i] - std::log2(primes[i]) -
                                   static_cast<double>(shift);
        }
    } else {
        scale_factors.push_back(std::log2(primes[primes.size() - 1]));
    }
    while (scale_factors.size() < primes.size()) {
        scale_factors.push_back(std::log2(primes[scale_factors.size()]));
    }
    return scale_factors;
}

// Resolve inheritance with DFS + memoization
static FinalPreset
resolve_one(const std::string &name,
            const std::unordered_map<std::string, RawPreset> &raw,
            std::unordered_map<std::string, FinalPreset> &memo,
            std::unordered_set<std::string> &visiting) {
    if (memo.count(name))
        return memo[name];
    if (!raw.count(name))
        throw std::runtime_error("Unknown preset name: " + name);

    if (visiting.count(name))
        throw std::runtime_error("Cyclic PARENT detected at: " + name);
    visiting.insert(name);

    const RawPreset &r = raw.at(name);
    FinalPreset out;

    // Base case: parent = self or not present -> no parent apply
    bool has_parent = r.has_PARENT && !r.PARENT.empty() && r.PARENT != name;
    FinalPreset base;
    if (has_parent) {
        base = resolve_one(r.PARENT, raw, memo, visiting);
    } else {
        // sensible defaults already in FinalPreset ctor
    }

    // Merge: start from base (if any), override with r if present
    auto pick_u32 = [](bool has, uint32_t v, uint32_t basev) {
        return has ? v : basev;
    };
    auto pick_str = [](bool has, const std::string &v,
                       const std::string &basev) { return has ? v : basev; };

    out.NAME = r.NAME.empty() ? base.NAME : r.NAME;
    out.PARENT =
        has_parent ? r.PARENT : (r.has_PARENT ? r.PARENT : base.PARENT);
    out.LOG_DEGREE = pick_u32(r.has_LOG_DEGREE, r.LOG_DEGREE, base.LOG_DEGREE);
    out.NUM_BASE = pick_u32(r.has_NUM_BASE, r.NUM_BASE, base.NUM_BASE);
    out.NUM_QP = pick_u32(r.has_NUM_QP, r.NUM_QP, base.NUM_QP);
    out.NUM_TP = pick_u32(r.has_NUM_TP, r.NUM_TP, base.NUM_TP);
    out.ENC_LEVEL = pick_u32(r.has_ENC_LEVEL, r.ENC_LEVEL, base.ENC_LEVEL);
    out.HWT = pick_u32(r.has_HWT, r.HWT, base.HWT);
    out.RANK = pick_u32(r.has_RANK, r.RANK, base.RANK);
    out.NUM_SECRET = pick_u32(r.has_NUM_SECRET, r.NUM_SECRET, base.NUM_SECRET);
    out.GADGET_RANK =
        pick_u32(r.has_GADGET_RANK, r.GADGET_RANK, base.GADGET_RANK);

    if (r.has_PRIMES)
        out.PRIMES = r.PRIMES;
    else
        out.PRIMES = base.PRIMES;

    if (r.has_SCALE_FACTORS)
        out.SCALE_FACTORS = r.SCALE_FACTORS;
    else
        out.SCALE_FACTORS = base.SCALE_FACTORS;

    out.MAX_LEVEL = out.SCALE_FACTORS.size() - 1;

    // out.SCALE_FACTORS = compute_scale_factors(out.NUM_BASE + out.NUM_QP - 1,
    //                                           out.ENC_LEVEL, out.PRIMES);

    visiting.erase(name);
    memo[name] = out;
    return memo[name];
}

static void write_header(const std::string &out_path,
                         const std::vector<FinalPreset> &finals) {
    std::ofstream os(out_path);
    if (!os)
        throw std::runtime_error("Failed to open output: " + out_path);

    os << "// Auto-generated by DebGenParam.cpp — DO NOT EDIT\n";
    os << "#pragma once\n\n";
    os << "#include <cstdint>\n";
    os << "#include <cinttypes>\n";
    os << "#include <vector>\n";
    os << "#include <string>\n";
    os << "#include <unordered_map>\n";
    os << "\n";
    os << "#include \"deb/deb_type.h\"\n";
    os << "#define DEB_PRESET_LIST";
    for (const auto &final : finals) {
        os << " ";
        os << "X(" << final.NAME << ")";
    }
    os << "\nnamespace deb {\n\n";

    auto emit_u64_vec = [&](const std::vector<uint64_t> &v) {
        std::ostringstream ss;
        ss << "{\n";
        for (size_t i = 0; i < v.size(); ++i) {
            ss << "\tUINT64_C(" << v[i] << "),  // " << i << "\n";
        }
        ss << "}";
        return ss.str();
    };
    auto emit_double_vec = [&](const std::vector<double> &v) {
        std::ostringstream ss;
        ss << std::setprecision(17);
        ss << "{\n";
        for (size_t i = 0; i < v.size(); ++i) {
            ss << "\t" << v[i] << ", // " << i << "\n";
        }
        ss << "}";
        return ss.str();
    };

    auto emit_constexpr_var = [&](const std::string &var_name,
                                  const std::string &val,
                                  const std::string &type = "deb_size_t") {
        std::ostringstream ss;
        ss << "inline static constexpr " << type << " " << var_name << " = "
           << val << ";\n";
        return ss.str();
    };
    FinalPreset empty_preset;
    empty_preset.NAME = empty_preset.PARENT = "EMPTY";
    std::vector<FinalPreset> finals_copy = finals;
    finals_copy.push_back(std::move(empty_preset));
    for (const auto &p : finals_copy) {
        os << "struct " << p.NAME << " { \n"
           << emit_constexpr_var("preset", "DEB_PRESET_" + p.NAME,
                                 "deb_preset_t")
           << emit_constexpr_var("parent", "DEB_PRESET_" + p.PARENT,
                                 "deb_preset_t")
           << emit_constexpr_var("preset_name", "\"" + p.NAME + "\"",
                                 "const char*")
           << emit_constexpr_var("rank", std::to_string(p.RANK))
           << emit_constexpr_var("num_secret", std::to_string(p.NUM_SECRET))
           << emit_constexpr_var("log_degree", std::to_string(p.LOG_DEGREE))
           << emit_constexpr_var("degree", std::to_string(1u << p.LOG_DEGREE))
           << emit_constexpr_var("num_slots",
                                 std::to_string((1u << p.LOG_DEGREE) / 2))
           << emit_constexpr_var("gadget_rank", std::to_string(p.GADGET_RANK))
           << emit_constexpr_var("num_base", std::to_string(p.NUM_BASE))
           << emit_constexpr_var("num_qp", std::to_string(p.NUM_QP))
           << emit_constexpr_var("num_tp", std::to_string(p.NUM_TP))
           << emit_constexpr_var(
                  "num_p", std::to_string(p.NUM_BASE + p.NUM_TP + p.NUM_QP))
           << emit_constexpr_var("encryption_level",
                                 std::to_string(p.ENC_LEVEL))
           << emit_constexpr_var("max_level", std::to_string(p.MAX_LEVEL))
           << emit_constexpr_var("hamming_weight", std::to_string(p.HWT))
           << emit_constexpr_var("gaussian_error_stdev", "3.2", "deb_real_t")
           << emit_constexpr_var("primes[]", emit_u64_vec(p.PRIMES),
                                 "deb_u64_t")
           << emit_constexpr_var("scale_factors[]",
                                 emit_double_vec(p.SCALE_FACTORS), "deb_real_t")
           << "};\n\n";
    }

    os << "} // namespace deb\n";
    os.close();
}

static bool replace_codegen_block(const std::string &file_path,
                                  const std::string &begin_marker,
                                  const std::string &end_marker,
                                  const std::string &insert_text) {
    std::ifstream in(file_path);
    if (!in) {
        std::cerr << "Cannot open file: " << file_path << '\n';
        return false;
    }

    std::ostringstream buf;
    buf << in.rdbuf();
    std::string content = buf.str();
    in.close();

    // find marker
    size_t begin_pos = content.find(begin_marker);
    if (begin_pos == std::string::npos) {
        std::cerr << "Begin marker not found.\n";
        return false;
    }

    size_t end_pos = content.find(end_marker, begin_pos);
    if (end_pos == std::string::npos) {
        std::cerr << "End marker not found.\n";
        return false;
    }

    // construct replacement string (including markers)
    std::ostringstream replacement;
    replacement << begin_marker;
    replacement << insert_text;
    replacement << end_marker;

    // replace content between markers
    end_pos += end_marker.size();
    content.replace(begin_pos, end_pos - begin_pos, replacement.str());

    // check if content has changed
    {
        std::ifstream check_in(file_path, std::ios::binary);
        std::ostringstream old_buf;
        old_buf << check_in.rdbuf();
        if (old_buf.str() == content) {
            std::cout << "No change in file.\n";
            return true;
        }
    }

    // atomic write to file
    std::string tmp_path = file_path + ".tmp";
    {
        std::ofstream out(tmp_path, std::ios::binary);
        out << content;
    }
    std::remove(file_path.c_str());
    std::rename(tmp_path.c_str(), file_path.c_str());

    std::cout << "Updated file: " << file_path << '\n';
    return true;
}
