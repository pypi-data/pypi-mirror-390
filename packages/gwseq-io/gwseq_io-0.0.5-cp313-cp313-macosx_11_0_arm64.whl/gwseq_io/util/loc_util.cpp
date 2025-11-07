#pragma once

#include "includes.cpp"


struct ChrItem {
    std::string id;
    int64_t index;
    int64_t size;
};


std::tuple<std::vector<int64_t>, std::vector<int64_t>> preparse_locs(
    const std::vector<std::string>& chr_ids,
    const std::vector<int64_t>& starts={},
    const std::vector<int64_t>& ends={},
    const std::vector<int64_t>& centers={},
    int64_t span = -1
) {
    std::vector<int64_t> preparsed_starts;
    std::vector<int64_t> preparsed_ends;
    if (span >= 0) {
        uint8_t starts_specified = starts.empty() ? 0 : 1;
        uint8_t ends_specified = ends.empty() ? 0 : 1;
        uint8_t centers_specified = centers.empty() ? 0 : 1;
        if (starts_specified + ends_specified + centers_specified != 1) {
            throw std::runtime_error("either starts/ends/centers must be specified when using span");
        } else if (starts_specified != 0) {
            preparsed_starts = starts;
            preparsed_ends.resize(starts.size());
            for (uint64_t i = 0; i < starts.size(); ++i) {
                preparsed_ends[i] = starts[i] + span;
            }
        } else if (ends_specified != 0) {
            preparsed_ends = ends;
            preparsed_starts.resize(ends.size());
            for (uint64_t i = 0; i < ends.size(); ++i) {
                preparsed_starts[i] = ends[i] - span;
            }
        } else {
            preparsed_starts.resize(centers.size());
            preparsed_ends.resize(centers.size());
            for (uint64_t i = 0; i < centers.size(); ++i) {
                preparsed_starts[i] = centers[i] - span / 2;
                preparsed_ends[i] = centers[i] + (span + 1) / 2;
            }
        }
    } else if (starts.empty() || ends.empty()) {
        throw std::runtime_error("either starts+ends or starts/ends/centers+span must be specified");
    } else {
        preparsed_starts = starts;
        preparsed_ends = ends;
    }
    if (chr_ids.size() != preparsed_starts.size() || chr_ids.size() != preparsed_ends.size()) {
        throw std::runtime_error("length mismatch between chr_ids and starts/ends/centers");
    }
    return {preparsed_starts, preparsed_ends};
}


ChrItem parse_chr(
    const std::string& chr_id,
    const OrderedMap<std::string, ChrItem>& chr_map,
    int64_t key_size = -1
) {
    std::string chr_key = chr_id;
    if (key_size >= 0) chr_key = chr_key.substr(0, key_size);
    auto it = chr_map.find(chr_key);
    if (it != chr_map.end()) return it->second;
    it = chr_map.find(to_lowercase(chr_key));
    if (it != chr_map.end()) return it->second;
    it = chr_map.find(to_uppercase(chr_key));
    if (it != chr_map.end()) return it->second;
    if (to_lowercase(chr_id.substr(0, 3)) == "chr") {
        chr_key = chr_id.substr(3);
        if (key_size >= 0) chr_key = chr_key.substr(0, key_size);
    } else {
        chr_key = ("chr" + chr_id);
        if (key_size >= 0) chr_key = chr_key.substr(0, key_size);
    }
    it = chr_map.find(chr_key);
    if (it != chr_map.end()) return it->second;
    it = chr_map.find(to_lowercase(chr_key));
    if (it != chr_map.end()) return it->second;
    it = chr_map.find(to_uppercase(chr_key));
    if (it != chr_map.end()) return it->second;
    std::string available;
    for (const auto& entry : chr_map) {
        if (!available.empty()) available += ", ";
        available += entry.first;
    }
    throw std::runtime_error(fstring("chromosome {} missing ({})", chr_id, available));
}
