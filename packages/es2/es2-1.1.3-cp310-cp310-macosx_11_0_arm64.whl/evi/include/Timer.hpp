#pragma once

#include <chrono>
#include <iostream>
#include <mutex>
#include <optional>
#include <string>

namespace deb {
class DebTimer {
    std::string name_;
    std::chrono::high_resolution_clock::time_point start_;
    std::optional<double> elapsed_;
    static DebTimer *instance_;
    static std::mutex mtx_;
    DebTimer();

    void start_impl(const char *name);
    void end_impl();

public:
    // Singleton instance retrieval
    static DebTimer &get();
    static void start(const char *name);
    static void end();

    // Destructor for automatic end (rarely called due to singleton nature)
    ~DebTimer();
};
} // namespace deb
