#pragma once

#include "includes.cpp"


class ProgressTracker {
    int64_t total;
    int64_t current = 0;
    std::function<void(int64_t, int64_t)> callback;
    double report_interval;
    double last_reported = 0.0;
    std::mutex update_mutex;

public:
    ProgressTracker(
        int64_t total,
        std::function<void(int64_t, int64_t)> callback,
        double report_interval = 0.01
    ) : total(total), callback(callback), report_interval(report_interval) {}

    void add(int64_t value) {
        std::lock_guard<std::mutex> lock(update_mutex);
        current += value;
        double progress = (total > 0) ? static_cast<double>(current) / total : 0.0;
        if (callback && progress > last_reported + report_interval) {
            last_reported = progress;
            callback(current, total);
        }
    }

    void done() {
        std::lock_guard<std::mutex> lock(update_mutex);
        if (callback && last_reported < 1.0) {
            last_reported = 1.0;
            callback(total, total);
        }
    }

};


class ProgressCallback {
    std::chrono::steady_clock::time_point start_time;
    bool started = false;
    
public:
    void operator()(int64_t current, int64_t total) {
        if (!started) {
            start_time = std::chrono::steady_clock::now();
            started = true;
        }
        int64_t progress =  static_cast<int64_t>(static_cast<double>(current) / total * 100);
        auto now = std::chrono::steady_clock::now();
        double elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time).count() / 1000.0;
        char progress_str[5];
        snprintf(progress_str, sizeof(progress_str), "%3lld%%", progress);
        std::cerr << "Progress: " << progress_str;
        if (current > 0 && progress < 100 && elapsed > 0) {
            double rate = static_cast<double>(current) / elapsed;
            double remaining_items = total - current;
            std::cerr << " (ETA " << format_time(remaining_items / rate) << ")";
        } else if (progress == 100) {
            std::cerr << " (" << format_time(elapsed, 3) << ")";
        } else {
            std::cerr << "               ";
        }
        std::cerr << "  " << (current == total ? "\n" : "\r") << std::flush;
    }
};
