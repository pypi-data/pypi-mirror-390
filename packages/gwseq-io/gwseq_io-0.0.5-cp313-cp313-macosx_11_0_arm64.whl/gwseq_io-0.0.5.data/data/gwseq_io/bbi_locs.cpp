#pragma once


struct ValueStats {
    float sum = 0;
    int64_t count = 0;
};


struct FullValueStats {
    float min = std::numeric_limits<float>::quiet_NaN();
    float max = std::numeric_limits<float>::quiet_NaN();
    float sum = 0;
    float sum_squared = 0;
    int64_t count = 0;
};


struct Loc {
    int64_t chr_index;
    int64_t start;
    int64_t end;
    int64_t binned_start;
    int64_t binned_end;
    double bin_size;
    int64_t output_start_index;
    int64_t output_end_index;
};


class Locs : public std::vector<Loc> {
public:
    int64_t bin_count;
    using std::vector<Loc>::vector;
};


struct LocsInterval {
    int64_t start;
    int64_t end;
};


class LocsIntervals : public std::vector<LocsInterval> {
public:
    using std::vector<LocsInterval>::vector;
};


Locs parse_locs(
    const OrderedMap<std::string, ChrItem>& chr_map,
    int64_t key_size,
    const std::vector<std::string>& chr_ids,
    const std::vector<int64_t>& starts,
    const std::vector<int64_t>& ends,
    double bin_size = 1.0,
    int64_t bin_count = -1,
    bool full_bin = false
) {
    if (chr_ids.size() != starts.size() || (!ends.empty() && chr_ids.size() != ends.size())) {
        throw std::runtime_error("length mismatch between chr_ids, starts or ends");
    }
    Locs locs(chr_ids.size());
    std::set<int64_t> binned_spans;
    for (int64_t i = 0; i < static_cast<int64_t>(chr_ids.size()); ++i) {
        Loc loc;
        loc.chr_index = parse_chr(chr_ids[i], chr_map, key_size).index;
        loc.start = starts[i];
        loc.end = ends[i];
        if (loc.start > loc.end) {
            throw std::runtime_error(fstring("loc {}:{}-{} at index {} invalid", chr_ids[i], loc.start, loc.end, i));
        }
        loc.binned_start = static_cast<int64_t>(std::floor(loc.start / bin_size) * bin_size);
        loc.binned_end = full_bin
            ? static_cast<int64_t>(std::ceil(loc.end / bin_size) * bin_size)
            : static_cast<int64_t>(std::floor(loc.end / bin_size) * bin_size);
        locs[i] = loc;
        binned_spans.insert(loc.binned_end - loc.binned_start);
    }
    if (bin_count < 0) bin_count = static_cast<int64_t>(std::floor(*binned_spans.rbegin() / bin_size));
    std::sort(locs.begin(), locs.end(), [](const Loc& a, const Loc& b) {
        return std::tie(a.chr_index, a.binned_start, a.binned_end) < std::tie(b.chr_index, b.binned_start, b.binned_end);
    });
    for (int64_t i = 0; i < static_cast<int64_t>(chr_ids.size()); ++i) {
        auto& loc = locs[i];
        loc.bin_size = static_cast<double>(loc.binned_end - loc.binned_start) / bin_count;
        loc.output_start_index = i * bin_count;
        loc.output_end_index = loc.output_start_index + bin_count;
    }
    locs.bin_count = bin_count;
    return locs;
}


int64_t get_locs_coverage(const Locs& locs) {
    int64_t coverage = 0;
    for (const auto& loc : locs) {
        coverage += (loc.binned_end - loc.binned_start);
    }
    return coverage;
}


std::tuple<LocsIntervals, int64_t> get_locs_batchs(
    const Locs& locs,
    int64_t parallel = 1
) {
    int64_t total_coverage = get_locs_coverage(locs);
    int64_t coverage_per_batch = total_coverage / parallel;
    LocsIntervals locs_batchs;
    if (locs.empty()) return {locs_batchs, 0};
    locs_batchs.push_back({0, 0});
    int64_t coverage = 0;
    for (int64_t i = 0 ; i < static_cast<int64_t>(locs.size()) - 1; ++i) {
        coverage += (locs[i].binned_end - locs[i].binned_start);
        if (coverage >= coverage_per_batch) {
            locs_batchs.back().end = i + 1;
            locs_batchs.push_back({i + 1, i + 1});
            coverage = 0;
        }
    }
    locs_batchs.back().end = locs.size();
    return {locs_batchs, total_coverage};
}
