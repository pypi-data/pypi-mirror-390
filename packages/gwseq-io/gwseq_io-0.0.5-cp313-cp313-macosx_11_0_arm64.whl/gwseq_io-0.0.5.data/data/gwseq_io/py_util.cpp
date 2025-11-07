#pragma once

#include "includes.cpp"


template<typename T>
ByteArray make_npy_header(const std::vector<T>& data, const std::vector<size_t>& shape) {
    // Determine dtype string based on type
    std::string dtype_str;
    if constexpr (std::is_same_v<T, float>) {
        dtype_str = "<f4";
    } else if constexpr (std::is_same_v<T, double>) {
        dtype_str = "<f8";
    } else if constexpr (std::is_same_v<T, int32_t>) {
        dtype_str = "<i4";
    } else if constexpr (std::is_same_v<T, uint32_t>) {
        dtype_str = "<u4";
    } else if constexpr (std::is_same_v<T, int64_t>) {
        dtype_str = "<i8";
    } else if constexpr (std::is_same_v<T, uint64_t>) {
        dtype_str = "<u8";
    } else {
        dtype_str = "|u1";
    }
    
    // Build shape string
    std::string shape_str = "(";
    for (size_t i = 0; i < shape.size(); ++i) {
        shape_str += std::to_string(shape[i]);
        if (i < shape.size() - 1) {
            shape_str += ", ";
        }
    }
    if (shape.size() == 1) shape_str += ",";
    shape_str += ")";
    
    // Build header dictionary
    std::string header_dict = "{'descr': '" + dtype_str + "', 'fortran_order': False, 'shape': " + shape_str + ", }";
    
    // Pad header to make total size (6 + 1 + 1 + 2 + header_len) divisible by 64
    int64_t base_size = 10;  // 6 (magic) + 1 (major) + 1 (minor) + 2 (header_len)
    int64_t header_len = header_dict.size() + 1;  // +1 for newline
    int64_t total_size = base_size + header_len;
    int64_t padding = (64 - (total_size % 64)) % 64;
    header_dict += std::string(padding, ' ') + '\n';
    header_len = header_dict.size();
    
    // Build .npy header
    std::vector<uint8_t> npy_header;
    npy_header.reserve(10 + header_len);
    
    // Magic string
    npy_header.insert(npy_header.end(), {0x93, 'N', 'U', 'M', 'P', 'Y'});
    
    // Version 1.0
    npy_header.push_back(0x01);
    npy_header.push_back(0x00);
    
    // Header length (little-endian uint16)
    uint16_t header_len_u16 = static_cast<uint16_t>(header_len);
    npy_header.push_back(header_len_u16 & 0xFF);
    npy_header.push_back((header_len_u16 >> 8) & 0xFF);
    
    // Header string
    npy_header.insert(npy_header.end(), header_dict.begin(), header_dict.end());
    
    return ByteArray(std::move(npy_header));
}


template<typename... Arrays>
void save_npz(
    const std::string& file_path,
    Arrays&&... arrays
) {
    auto writer = ZipWriter(file_path);

    // Process each array tuple: (name, data, shape)
    ([&](auto&& array) {
        auto& [name, data, shape] = array;
        
        // Create header
        auto header = make_npy_header(data, shape);
        
        // Create streams
        std::vector<ByteStream> streams;
        streams.push_back(ByteStream::from_bytes(std::move(header)));
        streams.push_back(ByteStream::from_iterable(std::move(data)));
        
        // Merge and add to zip
        auto stream = ByteStream::merge(std::move(streams));
        writer.add_entry(std::string(name) + ".npy", std::move(stream));
    }(std::forward<Arrays>(arrays)), ...);

    writer.close();
}


