#pragma once


const uint32_t BIGWIG_MAGIC = 0x888FFC26;
const uint32_t BIGBED_MAGIC = 0x8789F2EB;
const uint32_t BIGWIG_MAGIC_SWAPPED = 0x26FC8F88;
const uint32_t BIGBED_MAGIC_SWAPPED = 0xEBF28987;

const uint32_t CHR_TREE_MAGIC = 0x78CA8C91;
const uint32_t CHR_TREE_MAGIC_SWAPPED = 0x91CA8C78;

const uint16_t BBI_MIN_VERSION = 3;
const uint16_t BBI_OUTPUT_VERSION = 4;


struct BBIHeader {
    uint32_t magic;
    uint16_t version;
    int64_t zoom_levels;
    int64_t chr_tree_offset;
    int64_t full_data_offset;
    int64_t full_index_offset;
    int64_t field_count;
    int64_t defined_field_count;
    int64_t auto_sql_offset;
    int64_t total_summary_offset;
    int64_t uncompress_buffer_size;
    // uint64_t reserved;
};


struct ZoomHeader {
    int64_t reduction_level;
    // uint32_t reserved;
    int64_t data_offset;
    int64_t index_offset;
};


struct TotalSummary {
    int64_t bases_covered;
    double min_value;
    double max_value;
    double sum_data;
    double sum_squared;
};


struct ChrTreeHeader {
    uint32_t magic;
    int64_t block_size;
    int64_t key_size;
    int64_t value_size;
    int64_t item_count;
    // uint64_t reserved;
};


struct DataTreeHeader {
    uint32_t magic;
    int64_t block_size;
    int64_t item_count;
    int64_t start_chr_index;
    int64_t start_base;
    int64_t end_chr_index;
    int64_t end_base;
    int64_t end_file_offset;
    int64_t items_per_slot;
    // uint8_t reserved;
};


BBIHeader read_bbi_header(File& file) {
    ByteArray buffer = file.read(64, 0);
    BBIHeader header;
    header.magic = buffer.read_uint32(0);
    if (header.magic != BIGWIG_MAGIC && header.magic != BIGBED_MAGIC) {
        if (header.magic == BIGWIG_MAGIC_SWAPPED || header.magic == BIGBED_MAGIC_SWAPPED) {
            throw std::runtime_error("incompatible endianness");
        }
        throw std::runtime_error("not a bigwig or bigbed file");
    }
    header.version = buffer.read_uint16(4);
    if (header.version < BBI_MIN_VERSION) {
        throw std::runtime_error(
            "bigwig or bigbed version " + std::to_string(header.version) +
            " unsupported (>= " + std::to_string(BBI_MIN_VERSION) + ")"
        );
    }
    header.zoom_levels = static_cast<int64_t>(buffer.read_uint16(6));
    header.chr_tree_offset = static_cast<int64_t>(buffer.read_uint64(8));
    header.full_data_offset = static_cast<int64_t>(buffer.read_uint64(16));
    header.full_index_offset = static_cast<int64_t>(buffer.read_uint64(24));
    header.field_count = static_cast<int64_t>(buffer.read_uint16(32));
    header.defined_field_count = static_cast<int64_t>(buffer.read_uint16(34));
    header.auto_sql_offset = static_cast<int64_t>(buffer.read_uint64(36));
    header.total_summary_offset = static_cast<int64_t>(buffer.read_uint64(44));
    header.uncompress_buffer_size = static_cast<int64_t>(buffer.read_uint32(52));
    // header.reserved = buffer.read_uint64(56);
    return header;
}


std::vector<ZoomHeader> read_zoom_headers(File& file, int64_t zoom_levels) {
    std::vector<ZoomHeader> headers;
    if (zoom_levels == 0) return headers;
    ByteArray buffer = file.read(zoom_levels * 24, 64);
    for (int64_t i = 0; i < zoom_levels; ++i) {
        ZoomHeader header;
        header.reduction_level = static_cast<int64_t>(buffer.read_uint32(i * 24));
        // header.reserved = buffer.read_uint32(i * 24 + 4);
        header.data_offset = static_cast<int64_t>(buffer.read_uint64(i * 24 + 8));
        header.index_offset = static_cast<int64_t>(buffer.read_uint64(i * 24 + 16));
        headers.push_back(header);
    }
    return headers;
}


OrderedMap<std::string, std::string> read_auto_sql(File& file, int64_t offset, int64_t field_count) {
    if (offset == 0) return {};
    std::string sql_string = file.read_until('\0', offset).to_string(false);
    OrderedMap<std::string, std::string> fields;
    std::regex re(R"(\s*(\S+)\s+([^;]+);)");
    std::smatch match;
    std::istringstream iss(sql_string);
    std::string line;
    while (std::getline(iss, line)) {
        if (std::regex_search(line, match, re)) {
            std::string type = match[1];
            std::string field_list = match[2];
            std::regex field_re(R"(\s*(\S+)\s*(?:,|$))");
            std::sregex_iterator iter(field_list.begin(), field_list.end(), field_re);
            std::sregex_iterator end;
            for (; iter != end; ++iter) {
                std::string name = (*iter)[1].str();
                if (!name.empty()) {
                    fields.insert(name, type);
                }
            }
        }
    }
    if (fields.size() < 3
    || !std::regex_match(fields.key_at_index(0), std::regex(R"(^chr(?:om)_?(?:id|name)?$)", std::regex_constants::icase))
    || !std::regex_match(fields.key_at_index(1), std::regex(R"(^(?:chr(?:om)?_?)?start$)", std::regex_constants::icase))
    || !std::regex_match(fields.key_at_index(2), std::regex(R"(^(?:chr(?:om)?_?)?end$)", std::regex_constants::icase))) {
        throw std::runtime_error("missing or misplaced chr, start or end in autosql");
    }
    if (fields.size() != field_count) {
        throw std::runtime_error(fstring("field count {} does not match autosql field count {}", field_count, fields.size()));
    }
    return fields;
}


TotalSummary read_total_summary(File& file, int64_t offset) {
    ByteArray buffer = file.read(40, offset);
    TotalSummary summary;
    summary.bases_covered = static_cast<int64_t>(buffer.read_uint64(0));
    summary.min_value = buffer.read_double(8);
    summary.max_value = buffer.read_double(16);
    summary.sum_data = buffer.read_double(24);
    summary.sum_squared = buffer.read_double(32);
    return summary;
}


ChrTreeHeader read_chr_tree_header(File& file, int64_t offset) {
    ByteArray buffer = file.read(32, offset);
    ChrTreeHeader header;
    header.magic = buffer.read_uint32(0);
    if (header.magic != CHR_TREE_MAGIC) {
        if (header.magic == CHR_TREE_MAGIC_SWAPPED) {
            throw std::runtime_error("incompatible endianness (chromosome tree)");
        }
        throw std::runtime_error("invalid chr tree magic number");
    }
    header.block_size = static_cast<int64_t>(buffer.read_uint32(4));
    header.key_size = static_cast<int64_t>(buffer.read_uint16(8));
    header.value_size = static_cast<int64_t>(buffer.read_uint16(10));
    header.item_count = static_cast<int64_t>(buffer.read_uint64(16));
    // header.reserved = buffer.read_uint64(24);
    return header;
}


std::vector<ChrItem> read_chr_list(File& file, int64_t offset, int64_t key_size) {
    std::vector<ChrItem> items;
    ByteArray header_buffer = file.read(4, offset);
    uint8_t is_leaf = header_buffer.read_uint8(0);
    // uint8_t reserved = header_buffer.read_uint8(1);
    int64_t count = static_cast<int64_t>(header_buffer.read_uint16(2));
    ByteArray buffer = file.read(count * (key_size + 8), offset + 4);
    for (int64_t i = 0; i < count; i += 1) {
        int64_t buffer_index = i * (key_size + 8);
        if (is_leaf) {
            ChrItem item;
            item.id = buffer.read_string(buffer_index, key_size);
            item.index = static_cast<int64_t>(buffer.read_uint32(buffer_index + key_size));
            item.size = static_cast<int64_t>(buffer.read_uint32(buffer_index + key_size + 4));
            items.push_back(item);
        } else {
            // std::string key = buffer.read_string(buffer_index, key_size);
            uint64_t child_offset = buffer.read_uint64(buffer_index + key_size);
            auto child_items = read_chr_list(file, child_offset, key_size);
            items.insert(items.end(), child_items.begin(), child_items.end());
        }
    }
    std::sort(items.begin(), items.end(), [](const ChrItem& a, const ChrItem& b) {
        return a.index < b.index;
    });
    return items;
}
