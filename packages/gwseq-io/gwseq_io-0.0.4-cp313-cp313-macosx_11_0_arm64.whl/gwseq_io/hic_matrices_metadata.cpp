#pragma once


struct MatrixMetadata {
    int64_t chr1_index;
    int64_t chr2_index;
    std::string unit;
    int64_t bin_size;
    float sum_counts;
    int64_t block_bin_count;
    int64_t block_column_count;
    OrderedMap<int64_t, HiCIndexItem> blocks;
};


std::string get_matrix_key(
    int64_t chr1_index,
    int64_t chr2_index,
    int64_t bin_size,
    const std::string& unit
) {
    std::string key = 
        "chr_index=" + std::to_string(chr1_index) + "_" + std::to_string(chr2_index) + "|" +
        "bin_size=" + std::to_string(bin_size) + "|" +
        "unit=" + unit;
    return key;
}


std::list<MatrixMetadata> get_matrix_metadata_from_file(
    File& file,
    int64_t position,
    int64_t chr1_index,
    int64_t chr2_index
) {
    ByteStream stream = file.to_stream(position);
    auto buffer_chr1_index = static_cast<int64_t>(stream.read_int32());
    auto buffer_chr2_index = static_cast<int64_t>(stream.read_int32());
    auto bin_size_count = static_cast<int64_t>(stream.read_int32());
    if (buffer_chr1_index != chr1_index || buffer_chr2_index != chr2_index) {
        throw std::runtime_error("matrix metadata chr indices mismatch");
    }
    std::list<MatrixMetadata> matrices;
    for (int64_t i = 0; i < bin_size_count; ++i) {
        MatrixMetadata matrix;
        matrix.chr1_index = buffer_chr1_index;
        matrix.chr2_index = buffer_chr2_index;
        matrix.unit = to_lowercase(stream.read_until('\0').to_string());
        (void)stream.read_int32(); // bin size index in header
        matrix.sum_counts = stream.read_float();
        (void)stream.read_int32(); // occupied cell count
        (void)stream.read_float(); // 5th percentile estimate of counts
        (void)stream.read_float(); // 95th percentile estimate of counts
        matrix.bin_size = static_cast<int64_t>(stream.read_int32());
        matrix.block_bin_count = static_cast<int64_t>(stream.read_int32());
        matrix.block_column_count = static_cast<int64_t>(stream.read_int32());
        int64_t block_count = static_cast<int64_t>(stream.read_int32());
        for (int64_t j = 0; j < block_count; ++j) {
            HiCIndexItem block;
            int64_t block_number = static_cast<int64_t>(stream.read_int32());
            block.position = stream.read_int64();
            block.size = static_cast<int64_t>(stream.read_int32());
            matrix.blocks.insert(block_number, block);
        }
        matrices.push_back(std::move(matrix));
    }
    return matrices;
}
