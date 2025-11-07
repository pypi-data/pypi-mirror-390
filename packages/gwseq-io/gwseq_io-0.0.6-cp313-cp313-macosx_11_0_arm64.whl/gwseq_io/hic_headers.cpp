#pragma once


struct HiCHeader {
    int64_t version;
    int64_t footer_position;
    std::string genome_id;
    int64_t nvi_position;
    int64_t nvi_length;
    OrderedMap<std::string, std::string> attributes;
    OrderedMap<std::string, ChrItem> chr_map;
    std::vector<int64_t> bp_resolutions;
    std::vector<int64_t> frag_resolutions;
    std::vector<int64_t> sites;
};


struct HiCIndexItem {
    int64_t position;
    int64_t size;
};


struct ExpectedValueVector {
    std::string normalization;
    std::string unit;
    int64_t bin_size;
    std::vector<float> values;
    OrderedMap<int64_t, float> chr_scale_factors;
};


struct NormalizationVector {
    std::string normalization;
    int64_t chr_index;
    std::string unit;
    int64_t bin_size;
    int64_t position;
    int64_t byte_count;
};


struct HiCFooter {
    int64_t byte_count_v5;
    OrderedMap<std::string, std::string> attributes;
    OrderedMap<std::string, HiCIndexItem> master_index;
    OrderedMap<std::string, ExpectedValueVector> expected_value_vectors;
    OrderedMap<std::string, NormalizationVector> normalization_vectors;  
    std::set<std::string> normalizations;
    std::set<std::string> units;
};


std::string get_vector_key(
    const std::string& normalization,
    int64_t bin_size,
    const std::string& unit,
    int64_t chr_index = -1
) {
    std::string key = 
        "normalization=" + normalization + "|" +
        "bin_size=" + std::to_string(bin_size) + "|" +
        "unit=" + unit;
    if (chr_index != -1) key = "chr_index=" + std::to_string(chr_index) + "|" + key;
    return key;
}


HiCHeader read_hic_header(File& file) {
    ByteStream stream = file.to_stream();
    HiCHeader header;
    std::string magic = stream.read_string(4);
    if (magic != "HIC") throw std::runtime_error("not a hic file (magic: '" + magic + "')");
    header.version = static_cast<int64_t>(stream.read_int32());
    if (header.version < 6) throw std::runtime_error(
        "hic version " + std::to_string(header.version) +
        " unsupported (>= 6)"
    );
    header.footer_position = stream.read_int64();
    header.genome_id = stream.read_until('\0').to_string();
    if (header.version > 8) {
        header.nvi_position = stream.read_int64();
        header.nvi_length = stream.read_int64();
    }
    int32_t attribute_count = stream.read_int32();
    for (int32_t i = 0; i < attribute_count; ++i) {
        std::string key = stream.read_until('\0').to_string();
        std::string value = stream.read_until('\0').to_string();
        header.attributes.insert(key, value);
    }
    int32_t chr_count = stream.read_int32();
    for (int32_t i = 0; i < chr_count; ++i) {
        ChrItem chr_item;
        chr_item.id = stream.read_until('\0').to_string();
        chr_item.index = static_cast<int64_t>(i);
        if (header.version > 8) {
            chr_item.size = stream.read_int64();
        } else {
            chr_item.size = static_cast<int64_t>(stream.read_int32());
        }
        header.chr_map.insert(chr_item.id, chr_item);
    }
    int32_t bp_resolution_count = stream.read_int32();
    header.bp_resolutions.reserve(bp_resolution_count);
    for (int32_t i = 0; i < bp_resolution_count; ++i) {
        header.bp_resolutions.push_back(static_cast<int64_t>(stream.read_int32()));
    }
    int32_t frag_resolution_count = stream.read_int32();
    header.frag_resolutions.reserve(frag_resolution_count);
    for (int32_t i = 0; i < frag_resolution_count; ++i) {
        header.frag_resolutions.push_back(static_cast<int64_t>(stream.read_int32()));
    }
    int32_t site_count = stream.read_int32();
    header.sites.reserve(site_count);
    for (int32_t i = 0; i < site_count; ++i) {
        header.sites.push_back(static_cast<int64_t>(stream.read_int32()));
    }
    return header;
}


HiCFooter read_hic_footer(
    File& file,
    int64_t version,
    int64_t footer_position
) {
    ByteStream stream = file.to_stream(footer_position);
    HiCFooter footer;
    if (version > 8) {
        footer.byte_count_v5 = stream.read_int64();
    } else {
        footer.byte_count_v5 = static_cast<int64_t>(stream.read_int32());
    }
    int32_t master_index_count = stream.read_int32();
    for (int32_t i = 0; i < master_index_count; ++i) {
        HiCIndexItem item;
        std::string key = stream.read_until('\0').to_string();
        item.position = stream.read_int64();
        item.size = static_cast<int64_t>(stream.read_int32());
        footer.master_index.insert(key, item);
    }
    for (auto is_normalized : {false, true}) {
        int32_t expected_value_vector_count = stream.read_int32();
        for (int32_t i = 0; i < expected_value_vector_count; ++i) {
            ExpectedValueVector vector;
            vector.normalization = is_normalized
                ? to_lowercase(stream.read_until('\0').to_string())
                : "none";
            footer.normalizations.insert(vector.normalization);
            vector.unit = to_lowercase(stream.read_until('\0').to_string());
            footer.units.insert(vector.unit);
            vector.bin_size = static_cast<int64_t>(stream.read_int32());
            if (version > 8) {
                int64_t value_count = stream.read_int64();
                vector.values = stream.read_array<float>(value_count);
            } else {
                int32_t value_count = stream.read_int32();
                std::vector<double> values = stream.read_array<double>(value_count);
                vector.values = std::vector<float>(values.begin(), values.end());
            }
            int32_t chr_scale_factor_count = stream.read_int32();
            for (int32_t j = 0; j < chr_scale_factor_count; ++j) {
                int64_t chr_index = static_cast<int64_t>(stream.read_int32());
                float scale_factor = (version > 8)
                    ? stream.read_float()
                    : static_cast<float>(stream.read_double());
                vector.chr_scale_factors.insert(chr_index, scale_factor);
            }
            auto key = get_vector_key(vector.normalization, vector.bin_size, vector.unit);
            footer.expected_value_vectors.insert(key, vector);
        }
    }
    int32_t normalization_vector_count = stream.read_int32();
    for (int32_t i = 0; i < normalization_vector_count; ++i) {
        NormalizationVector vector;
        vector.normalization = to_lowercase(stream.read_until('\0').to_string());
        footer.normalizations.insert(vector.normalization);
        vector.chr_index = static_cast<int64_t>(stream.read_int32());
        vector.unit = to_lowercase(stream.read_until('\0').to_string());
        footer.units.insert(vector.unit);
        vector.bin_size = static_cast<int64_t>(stream.read_int32());
        vector.position = stream.read_int64();
        vector.byte_count = (version > 8)
            ? stream.read_int64()
            : static_cast<int64_t>(stream.read_int32());
        auto key = get_vector_key(vector.normalization, vector.bin_size, vector.unit, vector.chr_index);
        footer.normalization_vectors.insert(key, vector);
    }
    return footer;
}


std::vector<float> compute_expected_values(
    const OrderedMap<std::string, ExpectedValueVector>& expected_value_vectors,
    const std::string& normalization,
    int64_t bin_size,
    const std::string& unit,
    int64_t chr_index
) {
    auto key = get_vector_key(normalization, bin_size, unit);
    auto it_vector = expected_value_vectors.find(key);
    if (it_vector == expected_value_vectors.end()) {
        throw std::runtime_error("expected value vector " + key + " not found");
    }
    const ExpectedValueVector& vector = it_vector->second;
    auto it_factor = vector.chr_scale_factors.find(chr_index);
    if (it_factor == vector.chr_scale_factors.end()) {
        key = get_vector_key(normalization, bin_size, unit, chr_index);
        throw std::runtime_error("expected value vector " + key + " not found");
    }
    float scale_factor = 1.0f / it_factor->second;
    std::vector<float> expected_values;
    expected_values.reserve(vector.values.size());
    for (float value : vector.values) {
        expected_values.push_back(value * scale_factor);
    }
    return expected_values;
}


std::vector<float> get_normalization_vector_from_file(
    File& file,
    int64_t version,
    const OrderedMap<std::string, NormalizationVector>& normalization_vectors,
    int64_t chr_index,
    const std::string& normalization,
    int64_t bin_size,
    const std::string& unit
) {
    auto key = get_vector_key(normalization, bin_size, unit, chr_index);
    auto it_vector = normalization_vectors.find(key);
    if (it_vector == normalization_vectors.end()) {
        throw std::runtime_error("normalization vector " + key + " not found");
    }
    const NormalizationVector& vector = it_vector->second;
    ByteArray buffer = file.read(vector.byte_count, vector.position);
    if (version > 8) {
        int64_t value_count = buffer.read_int64(0);
        return buffer.read_array<float>(value_count, 8);
    } else {
        int32_t value_count = buffer.read_int32(0);
        std::vector<double> values = buffer.read_array<double>(value_count, 4);
        return std::vector<float>(values.begin(), values.end());
    }
}
