#pragma once


class HiCReader {
    std::string path;
    int64_t parallel;
    FilePool file_pool;
    OrderedMap<std::string, std::shared_ptr<std::vector<float>>> cached_expected_values;
    OrderedMap<std::string, std::shared_ptr<std::vector<float>>> cached_normalization_vectors;
    OrderedMap<std::string, std::shared_ptr<MatrixMetadata>> cached_matrices_metadata;
    int64_t max_cached_expected_values_size = 32;
    int64_t max_cached_normalization_vectors_size = 32;
    int64_t max_cached_matrices_metadata_size = 64;

public:
    HiCHeader header;
    HiCFooter footer;
    
    HiCReader(
        const std::string& path,
        int64_t parallel = 24,
        int64_t file_buffer_size = 32768,
        int64_t max_file_buffer_count = 128
    ) : path(path), parallel(parallel),
        file_pool(path, "r", parallel, file_buffer_size, max_file_buffer_count)
    {
        auto file = file_pool.get_pseudo_file();
        header = read_hic_header(file);
        footer = read_hic_footer(file, header.version, header.footer_position);
    }

    std::shared_ptr<std::vector<float>> get_expected_values(
        int64_t chr_index,
        const std::string& normalization,
        int64_t bin_size,
        const std::string& unit
    ) {
        std::string key = get_vector_key(normalization, bin_size, unit, chr_index);
        auto it_vector = cached_expected_values.find(key);
        if (it_vector != cached_expected_values.end()) {
            return it_vector->second;
        }
        while (cached_expected_values.size() >= max_cached_expected_values_size) {
            cached_expected_values.pop_front();
        }
        auto vector = compute_expected_values(
            footer.expected_value_vectors,
            normalization, bin_size, unit, chr_index
        );
        auto vector_ptr = std::make_shared<std::vector<float>>(std::move(vector));
        cached_expected_values.insert(key, vector_ptr);
        return vector_ptr;
    }

    std::shared_ptr<std::vector<float>> get_normalization_vector(
        int64_t chr_index,
        const std::string& normalization,
        int64_t bin_size,
        const std::string& unit
    ) {
        std::string key = get_vector_key(normalization, bin_size, unit, chr_index);
        auto it_vector = cached_normalization_vectors.find(key);
        if (it_vector != cached_normalization_vectors.end()) {
            return it_vector->second;
        }
        while (cached_normalization_vectors.size() >= max_cached_normalization_vectors_size) {
            cached_normalization_vectors.pop_front();
        }
        auto file = file_pool.get_pseudo_file();
        auto vector = get_normalization_vector_from_file(
            file, header.version, footer.normalization_vectors,
            chr_index, normalization, bin_size, unit
        );
        auto vector_ptr = std::make_shared<std::vector<float>>(std::move(vector));
        cached_normalization_vectors.insert(key, vector_ptr);
        return vector_ptr;
    }

    std::shared_ptr<MatrixMetadata> get_matrix_metadata(
        int64_t chr1_index,
        int64_t chr2_index,
        int64_t bin_size,
        const std::string& unit
    ) {
        std::string key = get_matrix_key(chr1_index, chr2_index, bin_size, unit);
        auto it_matrix = cached_matrices_metadata.find(key);
        if (it_matrix != cached_matrices_metadata.end()) {
            return it_matrix->second;
        }
        while (cached_matrices_metadata.size() >= max_cached_matrices_metadata_size) {
            cached_matrices_metadata.pop_front();
        }
        std::string chr_key = std::to_string(chr1_index) + "_" + std::to_string(chr2_index);
        auto it_master_index = footer.master_index.find(chr_key);
        if (it_master_index == footer.master_index.end()) {
            throw std::runtime_error("no matrix metadata for " + chr_key);
        }
        auto file = file_pool.get_pseudo_file();
        auto position = it_master_index->second.position;
        for (auto matrix : get_matrix_metadata_from_file(file, position, chr1_index, chr2_index)) {
            auto matrix_key = get_matrix_key(matrix.chr1_index, matrix.chr2_index, matrix.bin_size, matrix.unit);
            auto matrix_ptr = std::make_shared<MatrixMetadata>(std::move(matrix));
            cached_matrices_metadata.insert(matrix_key, matrix_ptr);
        }
        it_matrix = cached_matrices_metadata.find(key);
        if (it_matrix == cached_matrices_metadata.end()) {
            throw std::runtime_error("no matrix metadata for " + key);
        }
        return it_matrix->second;
    }

    std::vector<int64_t> get_available_bin_sizes(const std::string& unit) {
        if (to_lowercase(unit) == "bp") {
            return header.bp_resolutions;
        } else if (to_lowercase(unit) == "frag") {
            return header.frag_resolutions;
        } else {
            throw std::runtime_error("unit " + unit + " invalid (bp or frag)");
        }
    }

    Loc2D parse_loc(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts = {},
        const std::vector<int64_t>& ends = {},
        const std::vector<int64_t>& centers = {},
        int64_t span = -1,
        int64_t bin_size = -1,
        int64_t bin_count = -1,
        bool full_bin = false,
        const std::string& unit = "bp"
    ) {
        auto [preparsed_starts, preparsed_ends] = preparse_locs(chr_ids, starts, ends, centers, span);
        return parse_loc2d(
            header.chr_map, get_available_bin_sizes(unit),
            chr_ids, preparsed_starts, preparsed_ends,
            bin_size, bin_count, full_bin
        );
    }

    ContactRecordGenerator iter_records(
        const Loc2D& loc,
        int64_t min_distance_from_diagonal = -1,
        int64_t max_distance_from_diagonal = -1,
        std::string normalization = "none",
        std::string mode = "observed",
        std::string unit = "bp"

    ) {
        normalization = to_lowercase(normalization);
        mode = to_lowercase(mode);
        unit = to_lowercase(unit);
        std::shared_ptr<std::vector<float>> x_normalization_vector = nullptr;
        std::shared_ptr<std::vector<float>> y_normalization_vector = nullptr;
        std::shared_ptr<std::vector<float>> expected_values = nullptr;
        if (normalization != "none") {
            x_normalization_vector = get_normalization_vector(
                loc.x.chr.index, normalization, loc.bin_size, unit
            );
            y_normalization_vector = get_normalization_vector(
                loc.y.chr.index, normalization, loc.bin_size, unit
            );
        }
        if ((mode == "oe" || mode == "expected") && loc.x.chr.index == loc.y.chr.index) {
            expected_values = get_expected_values(
                loc.x.chr.index, normalization, loc.bin_size, unit
            );
        }
        auto matrix_metadata = get_matrix_metadata(
            loc.x.chr.index, loc.y.chr.index, loc.bin_size, unit
        );
        float average_value = loc.x.chr.index == loc.y.chr.index
            ? std::numeric_limits<float>::quiet_NaN()
            : matrix_metadata->sum_counts / (loc.x.chr.size / loc.bin_size) / (loc.y.chr.size / loc.bin_size);
        auto block_numbers = get_blocks_numbers(
            loc,
            matrix_metadata->block_bin_count,
            matrix_metadata->block_column_count,
            max_distance_from_diagonal,
            header.version
        );
        std::vector<HiCIndexItem> blocks;
        blocks.reserve(block_numbers.size());
        for (const auto& block_number : block_numbers) {
            auto block_it = matrix_metadata->blocks.find(block_number);
            if (block_it == matrix_metadata->blocks.end()) continue;
            blocks.push_back(block_it->second);
        }
        blocks.shrink_to_fit();
        return ContactRecordGenerator(
            file_pool, header.version, parallel,
            blocks, loc,
            normalization, mode, unit,
            x_normalization_vector, y_normalization_vector,
            expected_values, average_value,
            min_distance_from_diagonal, max_distance_from_diagonal
        );
    }

    std::vector<float> read_signal(
        const Loc2D& loc,
        float def_value = 0.0f,
        bool triangle = false,
        int64_t min_distance_from_diagonal = -1,
        int64_t max_distance_from_diagonal = -1,
        const std::string& normalization = "none",
        const std::string& mode = "observed",
        const std::string& unit = "bp"
    ) {
        auto generator = iter_records(
            loc,
            min_distance_from_diagonal, max_distance_from_diagonal,
            normalization, mode, unit
        );
        int64_t row_count = loc.y.bin_end - loc.y.bin_start;
        int64_t col_count = loc.x.bin_end - loc.x.bin_start;
        std::vector<float> signal(row_count * col_count, def_value);
        for (const auto& records : generator) {
            for (const auto& record : records) {
                int64_t c = record.x_bin - loc.x.bin_start;
                int64_t r = record.y_bin - loc.y.bin_start;
                if (c >= 0 && c < col_count && r >= 0 && r < row_count) {
                    signal[r * col_count + c] = record.value;
                }
                if (loc.x.chr.index == loc.y.chr.index && !triangle) {
                    int64_t c_sym = record.y_bin - loc.x.bin_start;
                    int64_t r_sym = record.x_bin - loc.y.bin_start;
                    if (c_sym >= 0 && c_sym < col_count && r_sym >= 0 && r_sym < row_count) {
                        signal[r_sym * col_count + c_sym] = record.value;
                    }
                }
            }
        }
        if (loc.reversed) {
            std::vector<float> transposed_signal(signal.size());
            for (int64_t r = 0; r < row_count; ++r) {
                for (int64_t c = 0; c < col_count; ++c) {
                    transposed_signal[c * row_count + r] = signal[r * col_count + c];
                }
            }
            signal = std::move(transposed_signal);
        }
        return signal;
    }

    Sparse2DArray<float> read_sparse_signal(
        const Loc2D& loc,
        bool triangle = false,
        int64_t min_distance_from_diagonal = -1,
        int64_t max_distance_from_diagonal = -1,
        const std::string& normalization = "none",
        const std::string& mode = "observed",
        const std::string& unit = "bp"
    ) {
        auto generator = iter_records(
            loc,
            min_distance_from_diagonal, max_distance_from_diagonal,
            normalization, mode, unit
        );
        int64_t row_count = loc.y.bin_end - loc.y.bin_start;
        int64_t col_count = loc.x.bin_end - loc.x.bin_start;
        Sparse2DArray<float> signal;
        signal.shape = {static_cast<uint32_t>(row_count), static_cast<uint32_t>(col_count)};
        for (const auto& records : generator) {
            std::vector<float> batch_signal;
            std::vector<uint32_t> batch_row;
            std::vector<uint32_t> batch_col;
            batch_signal.reserve(records.size());
            batch_row.reserve(records.size());
            batch_col.reserve(records.size());
            for (const auto& record : records) {
                int64_t c = record.x_bin - loc.x.bin_start;
                int64_t r = record.y_bin - loc.y.bin_start;
                if (c >= 0 && c < col_count && r >= 0 && r < row_count) {
                    batch_signal.push_back(record.value);
                    batch_row.push_back(static_cast<uint32_t>(r));
                    batch_col.push_back(static_cast<uint32_t>(c));
                }
                if (loc.x.chr.index == loc.y.chr.index && !triangle) {
                    int64_t c_sym = record.y_bin - loc.x.bin_start;
                    int64_t r_sym = record.x_bin - loc.y.bin_start;
                    if (c_sym >= 0 && c_sym < col_count && r_sym >= 0 && r_sym < row_count) {
                        batch_signal.push_back(record.value);
                        batch_row.push_back(static_cast<uint32_t>(r_sym));
                        batch_col.push_back(static_cast<uint32_t>(c_sym));
                    }
                }
            }
            signal.values.insert(signal.values.end(), batch_signal.begin(), batch_signal.end());
            signal.row.insert(signal.row.end(), batch_row.begin(), batch_row.end());
            signal.col.insert(signal.col.end(), batch_col.begin(), batch_col.end());
        }
        // Sort sparse matrix entries by row index first, then by column index
        if (!signal.values.empty()) {
            std::vector<size_t> indices(signal.values.size());
            std::iota(indices.begin(), indices.end(), 0);
            std::sort(indices.begin(), indices.end(),
                [&signal](size_t i1, size_t i2) {
                    if (signal.row[i1] != signal.row[i2]) {
                        return signal.row[i1] < signal.row[i2];
                    } else {
                        return signal.col[i1] < signal.col[i2];
                    }
                }
            );
            std::vector<float> sorted_values(signal.values.size());
            std::vector<uint32_t> sorted_row(signal.row.size());
            std::vector<uint32_t> sorted_col(signal.col.size());
            for (size_t i = 0; i < indices.size(); ++i) {
                sorted_values[i] = signal.values[indices[i]];
                sorted_row[i] = signal.row[indices[i]];
                sorted_col[i] = signal.col[indices[i]];
            }
            signal.values = std::move(sorted_values);
            signal.row = std::move(sorted_row);
            signal.col = std::move(sorted_col);
        }
        if (loc.reversed) {
            std::vector<uint32_t> transposed_row = signal.col;
            std::vector<uint32_t> transposed_col = signal.row;
            signal.row = std::move(transposed_row);
            signal.col = std::move(transposed_col);
            signal.shape = {signal.shape[1], signal.shape[0]};
        }
        return signal;
    }

};
