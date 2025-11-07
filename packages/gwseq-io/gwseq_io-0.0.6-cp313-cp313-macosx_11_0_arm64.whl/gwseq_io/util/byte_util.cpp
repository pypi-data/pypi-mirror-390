#pragma once

#include "includes.cpp"


class ByteArray {
public:
    std::vector<uint8_t> data;

    ByteArray() {}
    ByteArray(const std::vector<uint8_t>& data) : data(data) {}
    ByteArray(std::vector<uint8_t>&& data) : data(std::move(data)) {}

    static ByteArray from_string(const std::string& input) {
        std::vector<uint8_t> bytes(input.begin(), input.end());
        return ByteArray(std::move(bytes));
    }

    template<typename Container>
    static ByteArray from_iterable(const Container& input) {
        using T = typename Container::value_type;
        std::vector<uint8_t> bytes(input.size() * sizeof(T));
        if constexpr (std::is_same_v<Container, std::vector<T>> || std::is_array_v<Container>) {
            std::memcpy(bytes.data(), input.data(), bytes.size());
        } else {
            auto it = input.begin();
            for (size_t i = 0; i < input.size(); ++i, ++it) {
                std::memcpy(&bytes[i * sizeof(T)], &(*it), sizeof(T));
            }
        }
        return ByteArray(std::move(bytes));
    }

    auto begin() { return data.begin(); }
    auto end() { return data.end(); }
    auto begin() const { return data.begin(); }
    auto end() const { return data.end(); }

    bool empty() const {  return data.empty(); }
    int64_t size() const { return static_cast<int64_t>(data.size()); }

    uint8_t operator[](int64_t index) const { return data[index]; }
    uint8_t& operator[](int64_t index) { return data[index]; }

    void resize(int64_t new_size) {
        data.resize(new_size);
    }

    void reserve(int64_t new_capacity) {
        data.reserve(new_capacity);
    }

    void shrink_to_fit() {
        data.shrink_to_fit();
    }

    int8_t read_int8(int64_t offset) const {
        return static_cast<int8_t>(data[offset]);
    }

    uint8_t read_uint8(int64_t offset) const {
        return data[offset];
    }

    int16_t read_int16(int64_t offset) const {
        return *reinterpret_cast<const int16_t*>(&data[offset]);
    }

    uint16_t read_uint16(int64_t offset) const {
        return *reinterpret_cast<const uint16_t*>(&data[offset]);
    }

    int32_t read_int32(int64_t offset) const {
        return *reinterpret_cast<const int32_t*>(&data[offset]);
    }

    uint32_t read_uint32(int64_t offset) const {
        return *reinterpret_cast<const uint32_t*>(&data[offset]);
    }

    int64_t read_int64(int64_t offset) const {
        return *reinterpret_cast<const int64_t*>(&data[offset]);
    }

    uint64_t read_uint64(int64_t offset) const {
        return *reinterpret_cast<const uint64_t*>(&data[offset]);
    }

    float read_float(int64_t offset) const {
        return *reinterpret_cast<const float*>(&data[offset]);
    }

    double read_double(int64_t offset) const {
        return *reinterpret_cast<const double*>(&data[offset]);
    }

    template<typename T>
    std::vector<T> read_array(int64_t count, int64_t offset = 0) const {
        std::vector<T> values;
        values.reserve(count);
        int64_t type_size = sizeof(T);
        int64_t end_offset = offset + count * type_size;
        for (int64_t i = offset; i < end_offset; i += type_size) {
            values.push_back(*reinterpret_cast<const T*>(&data[i]));
        }
        return values;
    }

    std::string read_string(int64_t offset, int64_t length, bool trim_null = true) const {
        if (trim_null) {
            auto null_index = std::find(data.begin() + offset, data.begin() + offset + length, 0);
            return std::string(data.begin() + offset, null_index);
        }
        return std::string(data.begin() + offset, data.begin() + offset + length);
    }

    std::string to_string(bool trim_null = true) const {
        if (trim_null) {
            auto null_index = std::find(data.begin(), data.end(), 0);
            return std::string(data.begin(), null_index);
        }
        return std::string(data.begin(), data.end());
    }

    int64_t find(uint8_t byte, int64_t offset = 0) const {
        for (int64_t i = offset; i < size(); ++i) {
            if (data[i] == byte) return i;
        }
        return -1;
    }

    int64_t find(const ByteArray& bytes, int64_t offset = 0) const {
        if (bytes.empty()) return -1;
        int64_t search_end = size() - bytes.size() + 1;
        for (int64_t i = offset; i < search_end; ++i) {
            bool match = true;
            for (int64_t j = 0; j < bytes.size(); ++j) {
                if (data[i + j] != bytes[j]) {
                    match = false;
                    break;
                }
            }
            if (match) return i;
        }
        return -1;
    }

    void slice(int64_t offset, int64_t length) {
        if (offset > size()) offset = size();
        if (offset + length > size()) length = size() - offset;
        data = std::vector<uint8_t>(data.begin() + offset, data.begin() + offset + length);
    }

    ByteArray sliced(int64_t offset, int64_t length) const {
        if (offset > size()) offset = size();
        if (offset + length > size()) length = size() - offset;
        std::vector<uint8_t> slice_data(data.begin() + offset, data.begin() + offset + length);
        return ByteArray(std::move(slice_data));
    }
    
    template<typename T>
    void slice_at(const T& delimiter, int64_t offset = 0, bool include = false, bool partial = false) {
        auto index = find(delimiter, offset);
        if (index == -1) {
            if (partial) {
                slice(offset, size() - offset);
            } else {
                throw std::runtime_error("delimiter not found");
            }
        } else if (include) {
            int64_t delimiter_length;
            if constexpr (std::is_same_v<T, uint8_t>) {
                delimiter_length = 1;
            } else {
                delimiter_length = delimiter.size();
            }
            slice(offset, index - offset + delimiter_length);
        } else {
            slice(offset, index - offset);
        }
    }

    template<typename T>
    ByteArray sliced_at(const T& delimiter, int64_t offset = 0, bool include = false, bool partial = false) const {
        auto index = find(delimiter, offset);
        if (index == -1) {
            if (partial) return sliced(offset, size() - offset);
            throw std::runtime_error("delimiter not found");
        } else if (include) {
            int64_t delimiter_length;
            if constexpr (std::is_same_v<T, uint8_t>) {
                delimiter_length = 1;
            } else {
                delimiter_length = delimiter.size();
            }
            return sliced(offset, index - offset + delimiter_length);
        } else {
            return sliced(offset, index - offset);
        }
    }

    void append(const ByteArray& other, int64_t offset = 0, int64_t length = -1) {
        if (length < 0) length = other.size() - offset;
        data.insert(data.end(), other.data.begin() + offset, other.data.begin() + offset + length);
    }

    void append(uint8_t byte) {
        data.push_back(byte);
    }

    ByteArray appended(const ByteArray& other, int64_t offset = 0, int64_t length = -1) const {
        std::vector<uint8_t> combined_data = data;
        if (length < 0) length = other.size() - offset;
        combined_data.insert(combined_data.end(), other.data.begin() + offset, other.data.begin() + offset + length);
        return ByteArray(std::move(combined_data));
    }

    ByteArray appended(uint8_t byte) const {
        std::vector<uint8_t> combined_data = data;
        combined_data.push_back(byte);
        return ByteArray(std::move(combined_data));
    }

    std::vector<std::string> read_lines() const {
        std::vector<std::string> lines;
        int64_t line_start = 0;
        for (int64_t i = 0; i < size(); ++i) {
            if (data[i] == '\n') {
                int64_t line_end = i;
                if (line_end > line_start && data[line_end - 1] == '\r') line_end -= 1;
                lines.emplace_back(data.begin() + line_start, data.begin() + line_end);
                line_start = i + 1;
            }
        }
        if (line_start < size()) {
            int64_t line_end = size();
            if (line_end > line_start && data[line_end - 1] == '\r') line_end -= 1;
            lines.emplace_back(data.begin() + line_start, data.begin() + line_end);
        }
        return lines;
    }

    ByteArray decompressed(int64_t buffer_size = 32768, int64_t max_size = 1073741824) const {
        if (buffer_size < 1 || buffer_size > max_size) {
            throw std::runtime_error("buffer size " + std::to_string(buffer_size) + " invalid");
        }
        std::vector<uint8_t> decompressed_data;
        std::vector<uint8_t> buffer(buffer_size);
        z_stream stream{};
        stream.avail_in = static_cast<uInt>(data.size());
        stream.next_in = const_cast<Bytef*>(data.data());
        int init_result = inflateInit2(&stream, 15 + 32);
        if (init_result != Z_OK) {
            throw std::runtime_error("failed to initialize zlib for decompression: " + 
                std::string(stream.msg ? stream.msg : "unknown error"));
        }
        while (true) {
            stream.avail_out = static_cast<uInt>(buffer_size);
            stream.next_out = buffer.data();
            int ret = inflate(&stream, Z_NO_FLUSH);
            if (ret != Z_OK && ret != Z_STREAM_END) {
                std::string error_msg = "zlib decompression of " +
                    std::to_string(data.size()) + " bytes failed: ";
                if (ret == Z_STREAM_ERROR) {
                    error_msg += "invalid compression level";
                } else if (ret == Z_DATA_ERROR) {
                    error_msg += "invalid or incomplete deflate data";
                } else if (ret == Z_MEM_ERROR) {
                    error_msg += "out of memory";
                } else if (ret == Z_BUF_ERROR) {
                    error_msg += "no progress possible or output buffer too small";
                } else {
                    error_msg += "error code " + std::to_string(ret);
                }
                if (stream.msg) error_msg += " (" + std::string(stream.msg) + ")";
                inflateEnd(&stream);
                throw std::runtime_error(error_msg);
            }
            int64_t decompressed = buffer_size - stream.avail_out;
            if (decompressed_data.size() + decompressed > static_cast<uint64_t>(max_size)) {
                inflateEnd(&stream);
                throw std::runtime_error("decompressed data exceeds limit (" + std::to_string(max_size) + ")");
            }
            if (ret == Z_STREAM_END && decompressed_data.size() == 0 && decompressed == buffer_size) {
                decompressed_data = std::move(buffer);
                break;
            }
            decompressed_data.insert(decompressed_data.end(), buffer.begin(), buffer.begin() + decompressed);
            if (ret == Z_STREAM_END) break;
        }
        inflateEnd(&stream);
        return ByteArray(std::move(decompressed_data));
    }

    ByteArray compressed(std::string format = "gzip", int8_t compression_level = Z_DEFAULT_COMPRESSION) const {
        uLong compressed_size = compressBound(static_cast<uLong>(data.size()));
        std::vector<uint8_t> compressed_data(compressed_size);
        z_stream stream{};
        stream.avail_in = static_cast<uInt>(data.size());
        stream.next_in = const_cast<Bytef*>(data.data());
        stream.avail_out = static_cast<uInt>(compressed_size);
        stream.next_out = compressed_data.data();
        int window_bits = format == "gzip" ? (15 + 16) : (format == "zlib" ? 15 : -15); // -15 = raw deflate
        int init_result = deflateInit2(&stream, compression_level, Z_DEFLATED, window_bits, 8, Z_DEFAULT_STRATEGY);
        if (init_result != Z_OK) {
            throw std::runtime_error("failed to initialize zlib for compression: " + 
                std::string(stream.msg ? stream.msg : "unknown error"));
        }
        int ret = deflate(&stream, Z_FINISH);
        if (ret != Z_STREAM_END) {
            std::string error_msg = "zlib compression of " +
                std::to_string(data.size()) + " bytes failed: ";
            if (ret == Z_OK) {
                error_msg += "incomplete compression";
            } else if (ret == Z_STREAM_ERROR) {
                error_msg += "invalid compression level or parameters";
            } else if (ret == Z_BUF_ERROR) {
                error_msg += "no progress possible or output buffer too small";
            } else {
                error_msg += "error code " + std::to_string(ret);
            }
            if (stream.msg) error_msg += " (" + std::string(stream.msg) + ")";
            deflateEnd(&stream);
            throw std::runtime_error(error_msg);
        }
        compressed_data.resize(stream.total_out);
        deflateEnd(&stream);
        return ByteArray(std::move(compressed_data));
    }

};


class ByteStream {
    std::function<ByteArray()> input_function;
    ByteArray chunk;
    int64_t chunk_offset = 0;

public:
    ByteStream() = default;
    
    ByteStream(
        std::function<ByteArray()> input_function
    ) : input_function(input_function) {}
    
    ByteStream(
        std::shared_ptr<ByteStream> input_stream
    ) {
        throw std::runtime_error("not implemented (useless, use input_stream directly)");
    }

    virtual ~ByteStream() = default;

    // Delete copy constructor and copy assignment (move-only semantics)
    ByteStream(const ByteStream&) = delete;
    ByteStream& operator=(const ByteStream&) = delete;
    
    // Default move constructor and move assignment
    ByteStream(ByteStream&&) = default;
    ByteStream& operator=(ByteStream&&) = default;

    template<typename T>
    struct InputState {
        T input;
        int64_t offset = 0;
        int64_t chunk_size;
    };

    static ByteStream from_bytes(
        ByteArray&& input,
        int64_t chunk_size = 8192
    ) {
        auto state = std::make_shared<InputState<ByteArray>>(InputState<ByteArray>{
            std::move(input),
            0,
            chunk_size
        });
        return ByteStream(
            [state]() mutable -> ByteArray {
                if (state->offset >= state->input.size()) return ByteArray();
                int64_t length = std::min(state->chunk_size, state->input.size() - state->offset);
                auto result = state->input.sliced(state->offset, length);
                state->offset += length;
                return result;
            }
        );
    }

    template<typename Container>
    static ByteStream from_iterable(
        Container&& input,
        int64_t chunk_size = 8192
    ) {
        using T = typename std::decay_t<Container>::value_type;
        auto state = std::make_shared<InputState<std::decay_t<Container>>>(InputState<std::decay_t<Container>>{
            std::move(input),
            0,
            static_cast<int64_t>(((chunk_size + sizeof(T) - 1) / sizeof(T)) * sizeof(T))
        });
        return ByteStream(
            [state]() mutable -> ByteArray {
                int64_t item_count = state->chunk_size / sizeof(T);
                int64_t item_offset = state->offset / sizeof(T);
                if (item_offset >= static_cast<int64_t>(state->input.size())) return ByteArray();
                int64_t length = std::min(item_count, static_cast<int64_t>(state->input.size()) - item_offset);
                auto start = state->input.begin() + item_offset;
                auto end = start + length;
                auto result = ByteArray::from_iterable(std::vector<T>(start, end));
                state->offset += length * sizeof(T);
                return result;
            }
        );
    }

    static ByteStream merge(
        std::vector<ByteStream>&& streams
    ) {
        struct MergeState {
            std::vector<ByteStream> streams;
            size_t current_index = 0;
        };
        auto state = std::make_shared<MergeState>();
        state->streams = std::move(streams);
        return ByteStream(
            [state]() mutable -> ByteArray {
                while (state->current_index < state->streams.size()) {
                    auto chunk = state->streams[state->current_index].read_chunk();
                    if (chunk.empty()) {
                        state->current_index++;
                        continue;
                    }
                    return chunk;
                }
                return ByteArray();
            }
        );
    }

    virtual ByteArray read_chunk() {
        if (chunk_offset < chunk.size()) {
            if (chunk_offset == 0) {
                chunk_offset = chunk.size();
                return std::move(chunk);
            }
            ByteArray result = chunk.sliced(chunk_offset, chunk.size() - chunk_offset);
            chunk_offset = chunk.size();
            return result;
        }
        chunk = input_function();
        chunk_offset = chunk.size();
        return std::move(chunk);
    }

    ByteArray read(int64_t length, bool partial = false) {
        int64_t available = chunk.size() - chunk_offset;
        if (length == available) {
            return read_chunk();
        } else if (length < available) {
            ByteArray result = chunk.sliced(chunk_offset, length);
            chunk_offset += length;
            return result;
        } else {
            ByteArray result;
            result.reserve(length);
            while (length > 0) {
                if (chunk_offset < chunk.size()) {
                    int64_t cut = std::min(length, chunk.size() - chunk_offset);
                    result.append(chunk, chunk_offset, cut);
                    chunk_offset += cut;
                    length -= cut;
                } else {
                    chunk = read_chunk();
                    if (chunk.size() == 0) {
                        if (!partial) {
                            std::string message = "end of stream reached (" +
                                std::to_string(length) + " bytes missing)";
                            throw std::runtime_error(message);
                        }
                        return result;
                    }
                    chunk_offset -= chunk.size();
                }
            }
            return result;
        }
    }

    ByteArray read_until(
        uint8_t delimiter,
        bool include = false,
        bool partial = false,
        int64_t max_size = 1048576
    ) {
        ByteArray result;
        while (result.size() < max_size) {
            if (chunk_offset < chunk.size()) {
                int64_t index = chunk.find(delimiter, chunk_offset);
                if (index != -1) {
                    int64_t cut = include ? index - chunk_offset + 1 : index - chunk_offset;
                    result.append(chunk, chunk_offset, cut);
                    chunk_offset = index + 1;
                    return result;
                }
                result.append(chunk, chunk_offset, chunk.size() - chunk_offset);
                chunk_offset = chunk.size();
            } else {
                chunk = read_chunk();
                if (chunk.size() == 0) {
                    if (!partial) throw std::runtime_error("delimiter not found (end of stream reached)");
                    return result;
                }
                chunk_offset -= chunk.size();
            }
        }
        throw std::runtime_error("delimiter not found (maximum size exceeded)");
    }

    void skip(int64_t length, bool partial = false) {
        while (length > 0) {
            if (chunk_offset < chunk.size()) {
                int64_t cut = std::min(length, chunk.size() - chunk_offset);
                chunk_offset += cut;
                length -= cut;
            } else {
                chunk = read_chunk();
                if (chunk.size() == 0) {
                    if (!partial) {
                        std::string message = "end of stream reached (" +
                            std::to_string(length) + " bytes missing)";
                        throw std::runtime_error(message);
                    }
                    return;
                }
                chunk_offset -= chunk.size();
            }
        }
    }

    int8_t read_int8() {
        return static_cast<int8_t>(read(1)[0]);
    }

    uint8_t read_uint8() {
        return read(1)[0];
    }

    int16_t read_int16() {
        return read(2).read_int16(0);
    }

    uint16_t read_uint16() {
        return read(2).read_uint16(0);
    }

    int32_t read_int32() {
        return read(4).read_int32(0);
    }

    uint32_t read_uint32() {
        return read(4).read_uint32(0);
    }

    int64_t read_int64() {
        return read(8).read_int64(0);
    }

    uint64_t read_uint64() {
        return read(8).read_uint64(0);
    }

    float read_float() {
        return read(4).read_float(0);
    }

    double read_double() {
        return read(8).read_double(0);
    }

    template<typename T>
    std::vector<T> read_array(int64_t count) {
        return read(sizeof(T) * count).read_array<T>(count);
    }

    std::string read_string(int64_t length, bool trim_null = true) {
        return read(length).to_string(trim_null);
    }

};


class CompressionStream : public ByteStream {
    ByteStream input_stream;
    z_stream stream;
    bool initialized = false;
    bool finished = false;
    int64_t chunk_size;
    int64_t buffer_size;
    bool compute_crc32;
    ByteArray current_input_chunk; // Keep input buffer alive

public:
    uint32_t crc32;
    int64_t uncompressed_size;
    int64_t compressed_size;

    CompressionStream(
        ByteStream input_stream,
        std::string format = "gzip",
        int8_t compression_level = Z_DEFAULT_COMPRESSION,
        int64_t chunk_size = 8192,
        int64_t buffer_size = 32768,
        bool compute_crc32 = false
    ) : input_stream(std::move(input_stream)), chunk_size(chunk_size), buffer_size(buffer_size),
        compute_crc32(compute_crc32), crc32(0), uncompressed_size(0), compressed_size(0) {
        stream = z_stream{};
        int window_bits = format == "gzip" ? (15 + 16) : (format == "zlib" ? 15 : -15);
        int ret = deflateInit2(&stream, compression_level, Z_DEFLATED, window_bits, 8, Z_DEFAULT_STRATEGY);
        if (ret != Z_OK) {
            throw std::runtime_error("failed to initialize zlib for compression: " + 
                std::string(stream.msg ? stream.msg : "unknown error"));
        }
        initialized = true;
    }

    ~CompressionStream() {
        if (initialized) deflateEnd(&stream);
    }

    ByteArray read_chunk() override {
        if (finished) return ByteArray();
        std::vector<uint8_t> output_buffer(buffer_size);
        stream.avail_out = static_cast<uInt>(buffer_size);
        stream.next_out = output_buffer.data();
        bool input_exhausted = false;
        while (stream.avail_out > 0) {
            if (stream.avail_in == 0 && !input_exhausted) {
                current_input_chunk = input_stream.read_chunk();
                if (current_input_chunk.empty()) {
                    input_exhausted = true;
                } else {
                    if (compute_crc32) {
                        crc32 = ::crc32(crc32, current_input_chunk.data.data(), static_cast<uInt>(current_input_chunk.size()));
                    }
                    uncompressed_size += current_input_chunk.size();
                    stream.avail_in = static_cast<uInt>(current_input_chunk.size());
                    stream.next_in = const_cast<Bytef*>(current_input_chunk.data.data());
                }
            }
            int flush_mode = input_exhausted ? Z_FINISH : Z_NO_FLUSH;
            int ret = deflate(&stream, flush_mode);
            if (ret == Z_STREAM_END) {
                finished = true;
                break;
            } else if (ret != Z_OK) {
                std::string error_msg = "zlib compression error: ";
                if (ret == Z_STREAM_ERROR) {
                    error_msg += "invalid compression level or parameters";
                } else if (ret == Z_BUF_ERROR) {
                    error_msg += "no progress possible or output buffer too small";
                } else {
                    error_msg += "error code " + std::to_string(ret);
                }
                if (stream.msg) error_msg += " (" + std::string(stream.msg) + ")";
                throw std::runtime_error(error_msg);
            }
            int64_t bytes_written = buffer_size - stream.avail_out;
            if (bytes_written >= chunk_size || stream.avail_out == 0 || input_exhausted) {
                break;
            }
        }
        int64_t bytes_written = buffer_size - stream.avail_out;
        if (bytes_written == 0) return ByteArray();
        compressed_size += bytes_written;
        output_buffer.resize(bytes_written);
        return ByteArray(std::move(output_buffer));
    }
};


class DecompressionStream : public ByteStream {
    ByteStream input_stream;
    z_stream stream;
    bool initialized = false;
    bool finished = false;
    int64_t chunk_size;
    int64_t buffer_size;
    ByteArray current_input_chunk; // Keep input buffer alive

public:
    DecompressionStream(
        ByteStream input_stream,
        int64_t chunk_size = 8192,
        int64_t buffer_size = 32768
    ) : input_stream(std::move(input_stream)), chunk_size(chunk_size), buffer_size(buffer_size) {
        stream = z_stream{};
        int ret = inflateInit2(&stream, 15 + 32); // Auto-detect gzip/zlib format
        if (ret != Z_OK) {
            throw std::runtime_error("failed to initialize zlib for decompression: " + 
                std::string(stream.msg ? stream.msg : "unknown error"));
        }
        initialized = true;
    }

    ~DecompressionStream() {
        if (initialized) inflateEnd(&stream);
    }

    ByteArray read_chunk() override {
        if (finished) return ByteArray();
        std::vector<uint8_t> output_buffer(buffer_size);
        stream.avail_out = static_cast<uInt>(buffer_size);
        stream.next_out = output_buffer.data();
        bool input_exhausted = false;
        while (stream.avail_out > 0) {
            if (stream.avail_in == 0 && !input_exhausted) {
                current_input_chunk = input_stream.read_chunk();
                if (current_input_chunk.empty()) {
                    input_exhausted = true;
                } else {
                    stream.avail_in = static_cast<uInt>(current_input_chunk.size());
                    stream.next_in = const_cast<Bytef*>(current_input_chunk.data.data());
                }
            }
            if (input_exhausted && stream.avail_in == 0) {
                break;
            }
            int ret = inflate(&stream, Z_NO_FLUSH);
            if (ret == Z_STREAM_END) {
                finished = true;
                break;
            } else if (ret != Z_OK) {
                std::string error_msg = "zlib decompression error: ";
                if (ret == Z_STREAM_ERROR) {
                    error_msg += "invalid compression level";
                } else if (ret == Z_DATA_ERROR) {
                    error_msg += "invalid or incomplete deflate data";
                } else if (ret == Z_MEM_ERROR) {
                    error_msg += "out of memory";
                } else if (ret == Z_BUF_ERROR) {
                    error_msg += "no progress possible";
                } else {
                    error_msg += "error code " + std::to_string(ret);
                }
                if (stream.msg) error_msg += " (" + std::string(stream.msg) + ")";
                throw std::runtime_error(error_msg);
            }
            int64_t bytes_written = buffer_size - stream.avail_out;
            if (bytes_written >= chunk_size || stream.avail_out == 0 || input_exhausted) {
                break;
            }
        }
        int64_t bytes_written = buffer_size - stream.avail_out;
        if (bytes_written == 0) return ByteArray();
        output_buffer.resize(bytes_written);
        return ByteArray(std::move(output_buffer));
    }
};
