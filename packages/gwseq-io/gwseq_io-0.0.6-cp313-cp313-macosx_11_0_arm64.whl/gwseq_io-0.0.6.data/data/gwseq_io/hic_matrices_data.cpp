#pragma once


int64_t get_distance_from_diagonal(int64_t x, int64_t y, const Loc2D& loc) {
    if (loc.x.chr.index == loc.y.chr.index) {
        return std::abs(y - x);
    } else {
        double a = static_cast<double>(loc.y.binned_end - loc.y.binned_start) /
            (loc.x.binned_end - loc.x.binned_start);
        double b = loc.y.binned_start - a * loc.x.binned_start;
        double vertical = std::abs(y - (a * x + b));
        double horizontal = std::abs(x - (y - b) / a);
        return static_cast<int64_t>(std::round(std::min(vertical, horizontal)));
    }
}


std::set<int64_t> get_blocks_numbers(
    const Loc2D& loc,
    int64_t block_bin_count,
    int64_t block_column_count,
    int64_t max_distance_from_diagonal,
    int64_t version
) {
    std::set<int64_t> blocks_set;
    if (version > 8 && loc.x.chr.index == loc.y.chr.index) {
        int64_t translated_lower_pad = (loc.x.bin_start + loc.y.bin_start) / 2 / block_bin_count;
        int64_t translated_higher_pad = (loc.x.bin_end + loc.y.bin_end) / 2 / block_bin_count + 1;
        int64_t translated_nearer_depth = static_cast<int64_t>(std::log2(
            1 + abs(loc.x.bin_start - loc.y.bin_end) / std::sqrt(2) / block_bin_count));
        int64_t translated_further_depth = static_cast<int64_t>(std::log2(
            1 + abs(loc.x.bin_end - loc.y.bin_start) / std::sqrt(2) / block_bin_count));
        int64_t nearer_depth = std::min(translated_nearer_depth, translated_further_depth);
        if ((loc.x.bin_start > loc.y.bin_end && loc.x.bin_end < loc.y.bin_start) ||
            (loc.x.bin_end > loc.y.bin_start && loc.x.bin_start < loc.y.bin_end)) {
            nearer_depth = 0;
        }
        int64_t further_depth = std::max(translated_nearer_depth, translated_further_depth) + 1;
        for (int64_t depth = nearer_depth; depth <= further_depth; depth++) {
            for (int64_t pad = translated_lower_pad; pad <= translated_higher_pad; pad++) {
                int64_t block_number = depth * block_column_count + pad;
                blocks_set.insert(block_number);
            }
        }
    } else {
        int64_t col1 = loc.x.bin_start / block_bin_count;
        int64_t col2 = loc.x.bin_end / block_bin_count;
        int64_t row1 = loc.y.bin_start / block_bin_count;
        int64_t row2 = loc.y.bin_end / block_bin_count;
        for (int64_t r = row1; r <= row2; r++) {
            for (int64_t c = col1; c <= col2; c++) {
                if (max_distance_from_diagonal >= 0) {
                    int64_t r_start = r * block_bin_count * loc.bin_size;
                    int64_t c_start = c * block_bin_count * loc.bin_size;
                    int64_t r_end = r_start + block_bin_count * loc.bin_size;
                    int64_t c_end = c_start + block_bin_count * loc.bin_size;
                    int64_t min_dist = std::min({ 
                        get_distance_from_diagonal(r_start, c_start, loc),
                        get_distance_from_diagonal(r_end, c_start, loc),
                        get_distance_from_diagonal(r_start, c_end, loc),
                        get_distance_from_diagonal(r_end, c_end, loc)
                    });
                    if (min_dist > max_distance_from_diagonal) continue;
                }
                int64_t block_number = r * block_column_count + c;
                blocks_set.insert(block_number);
            }
        }
        if (loc.x.chr.index == loc.y.chr.index) {
            for (int64_t r = col1; r <= col2; r++) {
                for (int64_t c = row1; c <= row2; c++) {
                    if (max_distance_from_diagonal >= 0) {
                        int64_t r_start = r * block_bin_count * loc.bin_size;
                        int64_t c_start = c * block_bin_count * loc.bin_size;
                        int64_t r_end = r_start + block_bin_count * loc.bin_size;
                        int64_t c_end = c_start + block_bin_count * loc.bin_size;
                        int64_t min_dist = std::min({ 
                            get_distance_from_diagonal(r_start, c_start, loc),
                            get_distance_from_diagonal(r_end, c_start, loc),
                            get_distance_from_diagonal(r_start, c_end, loc),
                            get_distance_from_diagonal(r_end, c_end, loc)
                        });
                        if (min_dist > max_distance_from_diagonal) continue;
                    }
                    int32_t block_number = r * block_column_count + c;
                    blocks_set.insert(block_number);
                }
            }
        }
    }
    return blocks_set;
}


struct ContactRecord {
    int64_t x_bin;
    int64_t y_bin;
    float value;
};


bool process_record(
    ContactRecord& record,
    const Loc2D& loc,
    const std::string& normalization,
    const std::string& mode,
    const std::string& unit,
    const std::shared_ptr<std::vector<float>>& x_normalization_vector,
    const std::shared_ptr<std::vector<float>>& y_normalization_vector,
    const std::shared_ptr<std::vector<float>>& expected_values,
    float average_value,
    int64_t min_distance_from_diagonal,
    int64_t max_distance_from_diagonal
) {
    int64_t x = record.x_bin * loc.bin_size;
    int64_t y = record.y_bin * loc.bin_size;
    if (min_distance_from_diagonal >= 0 || max_distance_from_diagonal >= 0) {
        int64_t distance = get_distance_from_diagonal(x, y, loc);
        if (min_distance_from_diagonal >= 0 && distance < min_distance_from_diagonal) return false;
        if (max_distance_from_diagonal >= 0 && distance > max_distance_from_diagonal) return false;
    }
    if (!(((x >= loc.x.binned_start && x <= loc.x.binned_end &&
        y >= loc.y.binned_start && y <= loc.y.binned_end)) ||
        (loc.x.chr.index == loc.y.chr.index &&
        y >= loc.x.binned_start && y <= loc.x.binned_end && 
        x >= loc.y.binned_start && x <= loc.y.binned_end))) {
        return false;
    }
    if (normalization != "none") {
        float x_norm = (*x_normalization_vector)[record.x_bin];
        float y_norm = (*y_normalization_vector)[record.y_bin];
        record.value /= (x_norm * y_norm);
    }
    if (mode == "oe") {
        if (loc.x.chr.index == loc.y.chr.index) {
            size_t i = std::min(
                expected_values->size() - 1,
                static_cast<size_t>(std::abs(y - x) / loc.bin_size)
            );
            record.value /= (*expected_values)[i];
        } else {
            record.value /= average_value;
        }
    } else if (mode == "expected") {
        if (loc.x.chr.index == loc.y.chr.index) {
            size_t i = std::min(
                expected_values->size() - 1,
                static_cast<size_t>(std::abs(y - x) / loc.bin_size)
            );
            record.value = (*expected_values)[i];
        } else {
            record.value = average_value;
        }
    }
    return !(std::isnan(record.value) || std::isinf(record.value));
}


std::vector<ContactRecord> read_block(
    File& file,
    int64_t version,
    HiCIndexItem block,
    const Loc2D& loc,
    const std::string& normalization,
    const std::string& mode,
    const std::string& unit,
    const std::shared_ptr<std::vector<float>>& x_normalization_vector,
    const std::shared_ptr<std::vector<float>>& y_normalization_vector,
    const std::shared_ptr<std::vector<float>>& expected_values,
    float average_value,
    int64_t min_distance_from_diagonal,
    int64_t max_distance_from_diagonal
) {
    ByteArray buffer = file.read(block.size, block.position).decompressed();
    std::vector<ContactRecord> records;
    int64_t record_count = static_cast<int64_t>(buffer.read_int32(0));
    records.reserve(record_count);
    int64_t offset = 4;
    if (version < 7) {
        for (int64_t i = 0; i < record_count; ++i) {
            ContactRecord record;
            record.x_bin = static_cast<int64_t>(buffer.read_int32(offset));
            record.y_bin = static_cast<int64_t>(buffer.read_int32(offset + 4));
            record.value = buffer.read_float(offset + 8);
            bool include = process_record(
                record, loc, normalization, mode, unit,
                x_normalization_vector, y_normalization_vector,
                expected_values, average_value,
                min_distance_from_diagonal, max_distance_from_diagonal
            );
            if (include) records.push_back(record);
            offset += 12;
        }
        records.shrink_to_fit();
        return records;
    }
    int64_t bin_column_offset = static_cast<int64_t>(buffer.read_int32(offset));
    int64_t bin_row_offset = static_cast<int64_t>(buffer.read_int32(offset + 4));
    bool use_float = (buffer.read_uint8(offset + 8) == 1);
    bool use_int_x_pos = false;
    bool use_int_y_pos = false;
    if (version > 8) {
        use_int_x_pos = (buffer.read_uint8(offset + 9) == 1);
        use_int_y_pos = (buffer.read_uint8(offset + 10) == 1);
        offset += 11;
    } else {
        offset += 9;
    }
    uint8_t matrix_type = buffer.read_uint8(offset);
    offset += 1;
    if (matrix_type == 1) {
        int64_t x_advance = use_int_x_pos ? 4 : 2;
        int64_t y_advance = use_int_y_pos ? 4 : 2;
        int64_t value_advance = use_float ? 4 : 2;
        int64_t row_count = use_int_y_pos
            ? static_cast<int64_t>(buffer.read_int32(offset))
            : static_cast<int64_t>(buffer.read_int16(offset));
        offset += y_advance;
        for (int64_t i = 0; i < row_count; ++i) {
            int64_t row_number = use_int_y_pos
                ? static_cast<int64_t>(buffer.read_int32(offset))
                : static_cast<int64_t>(buffer.read_int16(offset));
            offset += y_advance;
            int64_t col_count = use_int_x_pos
                ? static_cast<int64_t>(buffer.read_int32(offset))
                : static_cast<int64_t>(buffer.read_int16(offset));
            offset += x_advance;
            int64_t y_bin = bin_row_offset + row_number;
            for (int64_t j = 0; j < col_count; ++j) {
                int64_t col_number = use_int_x_pos
                    ? static_cast<int64_t>(buffer.read_int32(offset))
                    : static_cast<int64_t>(buffer.read_int16(offset));
                offset += x_advance;
                int64_t x_bin = bin_column_offset + col_number;
                float value = use_float
                    ? buffer.read_float(offset)
                    : static_cast<float>(buffer.read_int16(offset));
                offset += value_advance;
                ContactRecord record;
                record.x_bin = x_bin;
                record.y_bin = y_bin;
                record.value = value;
                bool include = process_record(
                    record, loc, normalization, mode, unit,
                    x_normalization_vector, y_normalization_vector,
                    expected_values, average_value,
                    min_distance_from_diagonal, max_distance_from_diagonal
                );
                if (include) records.push_back(record);
            }
        }
    } else if (matrix_type == 2) {
        int64_t count = static_cast<int64_t>(buffer.read_int32(offset));
        int64_t width = static_cast<int64_t>(buffer.read_int16(offset + 4));
        offset += 6;
        for (int64_t i = 0; i < count; ++i) {
            int64_t row = i / width;
            int64_t col = i - row * width;
            int64_t x_bin = bin_column_offset + col;
            int64_t y_bin = bin_row_offset + row;
            float value;
            if (use_float) {
                value = buffer.read_float(offset);
                offset += 4;
                if (std::isnan(value)) continue;
            } else {
                int16_t short_value = buffer.read_int16(offset);
                offset += 2;
                if (short_value == -32768) continue;
                value = static_cast<float>(short_value);
            }
            ContactRecord record;
            record.x_bin = x_bin;
            record.y_bin = y_bin;
            record.value = value;
            bool include = process_record(
                record, loc, normalization, mode, unit,
                x_normalization_vector, y_normalization_vector,
                expected_values, average_value,
                min_distance_from_diagonal, max_distance_from_diagonal
            );
            if (include) records.push_back(record);
        }
    } else {
        throw std::runtime_error("matrix type " + std::to_string(matrix_type) + " invalid");
    }
    records.shrink_to_fit();
    return records;
}


class ContactRecordGenerator : public GeneratorBase<ContactRecordGenerator, std::vector<ContactRecord>> {
    std::shared_ptr<ThreadPoolManager<std::vector<ContactRecord>, true>> thread_pool_manager;

public:
    ContactRecordGenerator(const ContactRecordGenerator&) = delete;
    ContactRecordGenerator& operator=(const ContactRecordGenerator&) = delete;
    ContactRecordGenerator(ContactRecordGenerator&&) = default;
    ContactRecordGenerator& operator=(ContactRecordGenerator&&) = default;

    ContactRecordGenerator(
        FilePool& file_pool,
        int64_t version,
        int64_t parallel,
        const std::vector<HiCIndexItem>& blocks,
        const Loc2D& loc,
        const std::string& normalization,
        const std::string& mode,
        const std::string& unit,
        const std::shared_ptr<std::vector<float>>& x_normalization_vector,
        const std::shared_ptr<std::vector<float>>& y_normalization_vector,
        const std::shared_ptr<std::vector<float>>& expected_values,
        float average_value,
        int64_t min_distance_from_diagonal,
        int64_t max_distance_from_diagonal
    ) : thread_pool_manager(std::make_shared<ThreadPoolManager<std::vector<ContactRecord>, true>>(parallel)) {
        for (const auto& block : blocks) {
            thread_pool_manager->enqueue(
                [&file_pool, version, block, loc, normalization, mode, unit,
                 x_normalization_vector, y_normalization_vector, expected_values,
                 average_value, min_distance_from_diagonal, max_distance_from_diagonal]() {
                    auto file = file_pool.get_pseudo_file();
                    return read_block(
                        file, version, block, loc,
                        normalization, mode, unit,
                        x_normalization_vector, y_normalization_vector,
                        expected_values, average_value,
                        min_distance_from_diagonal, max_distance_from_diagonal
                    );
                }
            );
        }
    }

    NextResult next() {
        auto [value, done] = thread_pool_manager->next();
        return {std::move(value), done};
    }

};
