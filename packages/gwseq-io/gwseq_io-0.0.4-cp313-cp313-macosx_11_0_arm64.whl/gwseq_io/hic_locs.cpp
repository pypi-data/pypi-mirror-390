#pragma once


struct Loc2DLoc {
    ChrItem chr;
    int64_t start;
    int64_t end;
    int64_t binned_start;
    int64_t binned_end;
    int64_t bin_start;
    int64_t bin_end;
};


struct Loc2D {
    Loc2DLoc x;
    Loc2DLoc y;
    int64_t bin_size;
    bool reversed = false;
};


Loc2D parse_loc2d(
    const OrderedMap<std::string, ChrItem>& chr_map,
    const std::vector<std::int64_t>& available_bin_sizes,
    std::vector<std::string> chr_ids,
    std::vector<int64_t> starts,
    std::vector<int64_t> ends,
    int64_t bin_size = -1,
    int64_t bin_count = -1,
    bool full_bin = false
) {
    if (chr_ids.size() == 1) {
        chr_ids.push_back(chr_ids[0]);
    } else if (chr_ids.size() != 2) {
        throw std::runtime_error("1 or 2 chromosomes must be specified");
    }
    if (starts.size() == 1) {
        starts.push_back(starts[0]);
    } else if (starts.size() != 2) {
        throw std::runtime_error("1 or 2 start positions must be specified");
    }
    if (ends.size() == 1) {
        ends.push_back(ends[0]);
    } else if (ends.size() != 2) {
        throw std::runtime_error("1 or 2 end positions must be specified");
    }
    Loc2D loc;
    loc.x.chr = parse_chr(chr_ids[0], chr_map);
    loc.x.start = starts[0];
    loc.x.end = ends[0];
    loc.y.chr = parse_chr(chr_ids[1], chr_map);
    loc.y.start = starts[1];
    loc.y.end = ends[1];
    if (loc.x.chr.index > loc.y.chr.index) {
        std::swap(loc.x, loc.y);
        loc.reversed = true;
    }
    if (bin_count >= 0) {
        int64_t span = (loc.x.end - loc.x.start + loc.y.end - loc.y.start) / 2;
        int64_t requested_bin_size = (span + bin_count - 1) / bin_count;
        bin_size = available_bin_sizes[0];
        int64_t min_delta = std::abs(available_bin_sizes[0] - requested_bin_size);
        for (int64_t available : available_bin_sizes) {
            int64_t delta = std::abs(available - requested_bin_size);
            if (delta < min_delta) {
                min_delta = delta;
                bin_size = available;
            }
        }
    } else if (bin_size < 0) {
        bin_size = *std::min_element(available_bin_sizes.begin(), available_bin_sizes.end());
    }
    loc.x.binned_start = loc.x.start / bin_size * bin_size;
    loc.x.binned_end = full_bin
        ? ((loc.x.end + bin_size - 1) / bin_size * bin_size)
        : (loc.x.end / bin_size * bin_size);
    loc.y.binned_start = loc.y.start / bin_size * bin_size;
    loc.y.binned_end = full_bin
        ? ((loc.y.end + bin_size - 1) / bin_size * bin_size)
        : (loc.y.end / bin_size * bin_size);
    loc.x.bin_start = (loc.x.binned_start / bin_size);
    loc.x.bin_end = (loc.x.binned_end / bin_size);
    loc.y.bin_start = (loc.y.binned_start / bin_size);
    loc.y.bin_end = (loc.y.binned_end / bin_size);
    loc.bin_size = bin_size;
    return loc;
}
