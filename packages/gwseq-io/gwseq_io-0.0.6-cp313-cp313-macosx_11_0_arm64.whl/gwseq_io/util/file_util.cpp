#pragma once

#include "includes.cpp"


class File {
public:

    virtual ~File() = default;

    virtual void seek(int64_t offset, std::ios::seekdir dir = std::ios::beg) = 0;
    virtual int64_t tell() = 0;
    virtual int64_t get_file_size() = 0;
    virtual ByteArray read(int64_t size, int64_t offset, bool partial = false) = 0;
    virtual void write(const ByteArray& data, int64_t offset = -1) = 0;
    virtual void close() {};

    virtual void write_string(const std::string& input, int64_t offset = -1) {
        write(ByteArray::from_string(input), offset);
    }

    virtual ByteArray read_until(
        uint8_t delimiter,
        int64_t offset,
        bool include = false,
        bool partial = false,
        int64_t chunk_size = 4096,
        int64_t max_chunk_size = 1048576
    ) {
        ByteArray result;
        int64_t initial_offset = offset;
        while (true) {
            auto chunk = read(chunk_size, offset, true);
            if (chunk.size() == 0) {
                if (partial) return result;
                throw std::runtime_error("delimiter not found (end of file reached)");
            }
            auto index = chunk.find(delimiter, 0);
            if (index != -1) {
                if (include) index += 1;
                result.append(chunk.sliced(0, index));
                return result;
            }
            if (result.size() + chunk.size() > max_chunk_size) {
                throw std::runtime_error("delimiter not found (maximum size exceeded)");
            }
            result.append(chunk);
            offset += chunk.size();
        }
        seek(initial_offset + result.size() + (include ? 0 : 1));
        return result;
    }

    virtual ByteStream to_stream(int64_t offset = -1, int64_t chunk_size = 32768) {
        auto file_ptr = this;
        int64_t start_offset = (offset >= 0) ? offset : tell();
        auto state = std::make_shared<ByteStream::InputState<File*>>(ByteStream::InputState<File*>{
            file_ptr,
            start_offset,
            chunk_size
        });
        return ByteStream([state]() mutable -> ByteArray {
            auto result = state->input->read(state->chunk_size, state->offset, true);
            state->offset += result.size();
            return result;
        });
    }

    virtual void from_stream(ByteStream& stream, int64_t offset = -1) {
        if (offset >= 0) seek(offset);
        while (true) {
            auto chunk = stream.read_chunk();
            if (chunk.size() == 0) break;
            write(chunk);
        }
    }

};


class LocalFile : public File {
    std::string path;
    std::string mode;
    std::unique_ptr<std::fstream> file_handle;

public:
    LocalFile(const std::string& path, const std::string& mode = "r") : path(path), mode(mode) {
        std::ios::openmode flag = std::ios::binary;
        if (mode == "r") {
            flag |= std::ios::in;
        } else if (mode == "w") {
            flag |= std::ios::out;
        } else {
            throw std::runtime_error("file open mode " + mode + " not supported");
        }
        file_handle = std::make_unique<std::fstream>(path, flag);
        if (!file_handle->is_open()) {
            throw std::runtime_error("failed to open file " + path);
        }
    }

    ~LocalFile() {
        close();
    }

    void close() override {
        if (file_handle && file_handle->is_open()) {
            file_handle->flush();
            file_handle->close();
        }
    }

    void seek(int64_t offset, std::ios::seekdir dir = std::ios::beg) override {
        if (mode == "r") {
            file_handle->seekg(offset, dir);
        } else if (mode == "w") {
            file_handle->seekp(offset, dir);
        }
        if (file_handle->fail()) {
            throw std::runtime_error("failed to seek to " + std::to_string(offset) + " in file " + path);
        }
    }

    int64_t tell() override {
        int64_t offset = (mode == "r") ? file_handle->tellg() : file_handle->tellp();
        if (offset < 0) throw std::runtime_error("error determining cursor position in file " + path);
        return offset;
    }

    int64_t get_file_size() override {
        auto current_pos = tell();
        seek(0, std::ios::end);
        auto size = tell();
        seek(current_pos);
        return size;
    }

    ByteArray read(int64_t size = -1, int64_t offset = -1, bool partial = false) override {
        if (mode != "r") throw std::runtime_error("error reading file " + path + " (not in read mode)");
        if (size < 0) size = get_file_size();
        if (offset >= 0) seek(offset);
        std::vector<uint8_t> buffer(size);
        if (size == 0) return buffer;
        file_handle->read(reinterpret_cast<char*>(buffer.data()), size);
        std::streamsize bytes_read = file_handle->gcount();
        if (file_handle->bad() || file_handle->fail()) {
            if (file_handle->eof()) {
                if (partial) {
                    buffer.resize(bytes_read);
                } else {
                    std::string reason = " (end of file reached)";
                    throw std::runtime_error("error reading file " + path + reason);
                }
            } else {
                std::string reason = " (" + std::string(strerror(errno)) + ")";
                throw std::runtime_error("error reading file " + path + reason);
            }
        }
        return ByteArray(std::move(buffer));
    }

    void write(const ByteArray& data, int64_t offset = -1) override {
        if (mode != "w") throw std::runtime_error("error writing to file " + path + " (not in write mode)");
        if (offset >= 0) seek(offset);
        file_handle->write(reinterpret_cast<const char*>(data.data.data()), data.size());
        if (file_handle->bad() || file_handle->fail()) {
            std::string size = std::to_string(data.size());
            std::string reason = " (" + std::string(strerror(errno)) + ")";
            throw std::runtime_error("failed to write " + size + " bytes to file " + path + reason);
        }
    }

};


struct CurlWriteData {
    std::vector<uint8_t>* buffer;
    size_t expected_size;
};

static size_t custom_curl_write_callback(void* contents, size_t size, size_t nmemb, CurlWriteData* write_data) {
    size_t total_size = size * nmemb;
    uint8_t* data = static_cast<uint8_t*>(contents);
    
    write_data->buffer->insert(write_data->buffer->end(), data, data + total_size);
    return total_size;
}

class CurlGlobalManager {
private:
    std::mutex manager_lock;
    uint64_t ref_count;
    
    CurlGlobalManager() : ref_count(0) {}
    
public:
    CurlGlobalManager(const CurlGlobalManager&) = delete;
    CurlGlobalManager& operator=(const CurlGlobalManager&) = delete;
    
    static CurlGlobalManager& getInstance() {
        static CurlGlobalManager instance;
        return instance;
    }
    
    void initialize() {
        std::lock_guard<std::mutex> lock(manager_lock);
        if (ref_count == 0) curl_global_init(CURL_GLOBAL_DEFAULT);
        ref_count++;
    }
    
    void cleanup() {
        std::lock_guard<std::mutex> lock(manager_lock);
        ref_count--;
        if (ref_count == 0) curl_global_cleanup();
    }
    
    ~CurlGlobalManager() {
        if (ref_count > 0) curl_global_cleanup();
    }
};

class UrlFile : public File {
    std::string path;
    std::string mode;
    CURL* curl_handle;
    int64_t current_file_size = -1;
    int64_t current_offset = 0;
    bool closed = false;

    std::vector<uint8_t> read_all() {
        if (!curl_handle) throw std::runtime_error("curl_handle is not initialized");
        std::vector<uint8_t> buffer;
        CurlWriteData write_data;
        write_data.buffer = &buffer;
        write_data.expected_size = 0; // Not used for full read
        
        // Configure curl for this request
        curl_easy_setopt(curl_handle, CURLOPT_HTTPHEADER, nullptr); // No range header
        curl_easy_setopt(curl_handle, CURLOPT_WRITEFUNCTION, custom_curl_write_callback);
        curl_easy_setopt(curl_handle, CURLOPT_WRITEDATA, &write_data);
        curl_easy_setopt(curl_handle, CURLOPT_ACCEPT_ENCODING, ""); // All supported
        
        // Perform the request
        CURLcode res = curl_easy_perform(curl_handle);
        if (res != CURLE_OK) {
            std::string reason = " (curl request failed: " + std::string(curl_easy_strerror(res)) + ")";
            throw std::runtime_error("error reading " + path + reason);
        }
        
        // Check response code
        long response_code;
        curl_easy_getinfo(curl_handle, CURLINFO_RESPONSE_CODE, &response_code);
        if (response_code != 200) { // 200 = OK
            std::string reason = " (http request failed with code " + std::to_string(response_code) + ")";
            throw std::runtime_error("error reading " + path + reason);
        }
        seek(tell() + buffer.size());
        return buffer;
    }

public:
    UrlFile(const std::string& path, const std::string& mode = "r") : path(path), mode(mode), curl_handle(nullptr) {
        CurlGlobalManager::getInstance().initialize();
        curl_handle = curl_easy_init();
        if (!curl_handle) {
            CurlGlobalManager::getInstance().cleanup(); // Clean up on failure
            throw std::runtime_error("failed to initialize curl");
        }
        
        curl_easy_setopt(curl_handle, CURLOPT_URL, path.c_str());
        curl_easy_setopt(curl_handle, CURLOPT_FOLLOWLOCATION, 1L);
        curl_easy_setopt(curl_handle, CURLOPT_TIMEOUT, 30L);
        curl_easy_setopt(curl_handle, CURLOPT_CONNECTTIMEOUT, 10L);
        curl_easy_setopt(curl_handle, CURLOPT_USERAGENT, "UrlFile/1.0");
        curl_easy_setopt(curl_handle, CURLOPT_FAILONERROR, 1L);
        curl_easy_setopt(curl_handle, CURLOPT_ACCEPT_ENCODING, ""); // All supported
        curl_easy_setopt(curl_handle, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_2TLS);
    }
    
    ~UrlFile() {
        close();
    }

    void close() override {
        if (closed) return;
        if (curl_handle) curl_easy_cleanup(curl_handle);
        CurlGlobalManager::getInstance().cleanup();
        closed = true;
    }

    void seek(int64_t offset, std::ios::seekdir dir = std::ios::beg) override {
        if (dir == std::ios::beg) {
            current_offset = offset;
        } else if (dir == std::ios::cur) {
            current_offset += offset;
        } else if (dir == std::ios::end) {
            current_offset = get_file_size() + offset;
        } else {
            throw std::runtime_error("invalid seek direction");
        }
    }

    int64_t tell() override {
        return current_offset;
    }

    int64_t get_file_size() override {
        if (current_file_size >= 0) return current_file_size;
        if (!curl_handle) throw std::runtime_error("curl_handle is not initialized");
        double file_size = 0.0;
        curl_easy_setopt(curl_handle, CURLOPT_NOBODY, 1L);
        curl_easy_setopt(curl_handle, CURLOPT_HEADER, 0L);
        curl_easy_setopt(curl_handle, CURLOPT_FILETIME, 1L);
        CURLcode res = curl_easy_perform(curl_handle);
        if (res != CURLE_OK) {
            std::string reason = " (curl request failed: " + std::string(curl_easy_strerror(res)) + ")";
            throw std::runtime_error("error determining size of " + path + reason);
        }
        res = curl_easy_getinfo(curl_handle, CURLINFO_CONTENT_LENGTH_DOWNLOAD_T, &file_size);
        if (res != CURLE_OK || file_size < 0) {
            std::string reason = " (could not get content length)";
            throw std::runtime_error("error determining size of " + path + reason);
        }
        curl_easy_setopt(curl_handle, CURLOPT_NOBODY, 0L);
        curl_easy_setopt(curl_handle, CURLOPT_FILETIME, 0L);
        current_file_size = static_cast<int64_t>(file_size);
        return current_file_size;
    }

    ByteArray read(int64_t size = -1, int64_t offset = -1, bool partial = false) override {
        if (mode != "r") throw std::runtime_error("error reading file " + path + " (not in read mode)");
        if (offset < 0) offset = tell();
        if (size < 0) {
            if (offset == 0) return read_all();
            size = get_file_size() - offset;
        }
        if (!curl_handle) throw std::runtime_error("curl_handle is not initialized");
        
        // Initialize buffer as empty, let curl callback fill it
        std::vector<uint8_t> buffer;
        buffer.reserve(size);
        CurlWriteData write_data;
        write_data.buffer = &buffer;
        write_data.expected_size = size;
        
        // Set up range request
        std::string range_header = "Range: bytes=" + std::to_string(offset) + "-" + std::to_string(offset + size - 1);
        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, range_header.c_str());
        
        // Configure curl for this request
        curl_easy_setopt(curl_handle, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl_handle, CURLOPT_WRITEFUNCTION, custom_curl_write_callback);
        curl_easy_setopt(curl_handle, CURLOPT_WRITEDATA, &write_data);
        curl_easy_setopt(curl_handle, CURLOPT_ACCEPT_ENCODING, "");  // All supported
        
        // DEBUG: Enable verbose output to see all headers
        //curl_easy_setopt(curl_handle, CURLOPT_VERBOSE, 1L);
        // Perform the request
        CURLcode res = curl_easy_perform(curl_handle);
        // DEBUG: Disable verbose output after request
        //curl_easy_setopt(curl_handle, CURLOPT_VERBOSE, 0L);
        //throw std::runtime_error("debug");
        
        // Clean up headers
        curl_slist_free_all(headers);
        
        if (res != CURLE_OK) {
            std::string reason = " (curl request failed: " + std::string(curl_easy_strerror(res)) + ")";
            throw std::runtime_error("error reading " + path + reason);
        }
        
        // Check response code
        long response_code;
        curl_easy_getinfo(curl_handle, CURLINFO_RESPONSE_CODE, &response_code);
        if (response_code != 206 && response_code != 200) { // 206 = Partial Content, 200 = OK
            std::string reason = " (http request failed with code " + std::to_string(response_code) + ")";
            throw std::runtime_error("error reading " + path + reason);
        }

        // Check size
        if (static_cast<int64_t>(buffer.size()) != size) {
            if (static_cast<int64_t>(buffer.size()) > size || partial) {
                buffer.resize(size);
            } else {
                std::string reason = " (end of file reached)";
                throw std::runtime_error("error reading " + path + reason);
            }
        }

        seek(offset + buffer.size());
        return ByteArray(std::move(buffer));
    }

    void write(const ByteArray& /* data */, int64_t /* offset */) override {
        if (mode != "w") throw std::runtime_error("error writing to file " + path + " (not in write mode)");
        throw std::runtime_error("writing to url not supported");
    }

};


std::shared_ptr<File> open_file(const std::string& path, const std::string& mode = "r") {
    if (path.substr(0, 6) == "ftp://" || path.substr(0, 7) == "http://" || path.substr(0, 8) == "https://") {
        return std::make_shared<UrlFile>(path, mode);
    } else {
        return std::make_shared<LocalFile>(path, mode);
    }
}


class FilePool {

    struct FilePoolBuffer {
        int64_t offset;
        int64_t length;
        std::promise<ByteArray> data_promise;
        std::shared_future<ByteArray> data_future;

        FilePoolBuffer(int64_t offset, int64_t length) : offset(offset), length(length) {
            data_promise = std::promise<ByteArray>();
            data_future = data_promise.get_future().share();
        }

        ByteArray extract(int64_t req_offset, int64_t req_length, bool partial) const {
            int64_t buffer_req_offset = req_offset - offset;
            const auto& data = data_future.get();
            if (!partial && buffer_req_offset + req_length > data.size()) {
                throw std::runtime_error("end of file reached");
            }
            return data.sliced(buffer_req_offset, req_length);
        }

    };

    struct FilePoolBufferArray {
        std::vector<std::shared_ptr<FilePoolBuffer>> buffers;
        std::vector<std::shared_ptr<FilePoolBuffer>> new_buffers;

        ByteArray extract(int64_t req_offset, int64_t req_length, bool partial) const {
            if (buffers.size() == 1) return buffers[0]->extract(req_offset, req_length, partial);
            ByteArray result;
            result.reserve(req_length);
            int64_t remaining = req_length;
            for (const auto& buffer : buffers) {
                if (remaining <= 0) break;
                int64_t buffer_start = buffer->offset;
                int64_t buffer_end = buffer->offset + buffer->length;
                if (req_offset >= buffer_start && req_offset < buffer_end) {
                    int64_t extract_start = req_offset;
                    int64_t extract_length = std::min(remaining, buffer_end - req_offset);
                    result.append(buffer->extract(extract_start, extract_length, partial));
                    req_offset += extract_length;
                    remaining -= extract_length;
                }
            }
            result.shrink_to_fit();
            return result;
        }

    };

    class FilePoolPseudoFile : public File {
        FilePool* file_pool;
        int64_t current_offset = 0;

    public:
        FilePoolPseudoFile(FilePool* file_pool) : file_pool(file_pool) {}

        void seek(int64_t offset, std::ios::seekdir dir = std::ios::beg) override {
            if (dir == std::ios::beg) {
                current_offset = offset;
            } else if (dir == std::ios::cur) {
                current_offset += offset;
            } else if (dir == std::ios::end) {
                current_offset = file_pool->get_file_size().get() + offset;
            } else {
                throw std::runtime_error("invalid seek direction");
            }
        }

        int64_t tell() override {
            return current_offset;
        }

        int64_t get_file_size() override {
            return file_pool->get_file_size().get();
        }

        ByteArray read(int64_t size = -1, int64_t offset = -1, bool partial = false) override {
            if (offset < 0) offset = current_offset;
            auto data = file_pool->read(size, offset, partial).get();
            current_offset = offset + data.size();
            return data;
        }

        void write(const ByteArray& data, int64_t offset = -1) override {
            if (offset < 0) offset = current_offset;
            file_pool->write(data, offset).get();
            current_offset = offset + data.size();
        }

    };

    std::shared_ptr<File> get_file() {
        std::lock_guard<std::mutex> lock(pool_lock);
        if (file_pool.empty()) throw std::runtime_error("no available file handles in pool");
        auto file = file_pool.front();
        file_pool.pop();
        return file;
    }

    void put_file(std::shared_ptr<File> file) {
        std::lock_guard<std::mutex> lock(pool_lock);
        file_pool.push(file);
    }

    std::vector<std::tuple<int64_t, int64_t>> align_buffers(int64_t offset, int64_t length) const {
        std::vector<std::tuple<int64_t, int64_t>> buffers;
        int64_t current = offset;
        while (current < offset + length) {
            int64_t start = (current / buffer_size) * buffer_size;
            int64_t end = start + buffer_size;
            buffers.emplace_back(start, end - start);
            current = end;
        }
        return buffers;
    }

    FilePoolBufferArray get_buffers(int64_t offset, int64_t length) {
        auto buffers_bounds = align_buffers(offset, length);
        FilePoolBufferArray buffers;
        std::lock_guard<std::mutex> lock(buffer_pool_lock);
        for (const auto& [buffer_offset, buffer_length] : buffers_bounds) {
            auto it = buffer_pool.find(buffer_offset);
            if (it != buffer_pool.end()) {
                auto buffer = it->second;
                buffer_pool.erase(buffer_offset);
                if (buffer->length >= buffer_length) {
                    buffer_pool.insert(buffer_offset, buffer);
                }
                buffers.buffers.push_back(buffer);
                continue;
            }
            while (buffer_pool.size() >= max_buffer_count) {
                buffer_pool.pop_front();
            }
            auto buffer = std::make_shared<FilePoolBuffer>(buffer_offset, buffer_length);
            buffer_pool.insert(buffer_offset, buffer);
            buffers.buffers.push_back(buffer);
            buffers.new_buffers.push_back(buffer);
        }
        return buffers;
    }
    
    std::mutex pool_lock;
    Semaphore read_lock;
    std::mutex write_lock;
    std::queue<std::shared_ptr<File>> file_pool;
    ThreadPool<false> thread_pool;
    ThreadPool<false> buffer_thread_pool;
    OrderedMap<int64_t, std::shared_ptr<FilePoolBuffer>> buffer_pool;
    std::mutex buffer_pool_lock;
    int64_t buffer_size;
    int64_t max_buffer_count;

public:
    FilePool(
        const std::string& path,
        const std::string& mode = "r",
        int64_t parallel = 1,
        int64_t buffer_size = 32768,
        int64_t max_buffer_count = 128
    ) : read_lock(parallel), thread_pool(parallel), buffer_thread_pool(parallel * 2),
        buffer_size(buffer_size), max_buffer_count(max_buffer_count) {
        for (int64_t i = 0; i < parallel; ++i) {
            file_pool.push(open_file(path, mode));
        }
    }

    std::future<int64_t> get_file_size() {
        return thread_pool.enqueue([this]() {
            SemaphoreGuard guard(read_lock);
            auto file = get_file();
            try {
                auto size = file->get_file_size();
                put_file(file);
                return size;
            } catch (...) {
                put_file(file);
                throw;
            }
        });
    }

    std::future<ByteArray> read(int64_t size, int64_t offset, bool partial = false) {
        auto buffers = get_buffers(offset, size);
        for (auto& buffer : buffers.new_buffers) {
            thread_pool.enqueue([this, buffer]() {
                SemaphoreGuard guard(read_lock);
                auto file = get_file();
                try {
                    auto result = file->read(buffer->length, buffer->offset, true);
                    buffer->data_promise.set_value(std::move(result));
                    put_file(file);
                } catch (...) {
                    buffer->data_promise.set_exception(std::current_exception());
                    put_file(file);
                    throw;
                }
            });
        }
        return buffer_thread_pool.enqueue([buffers, offset, size, partial]() {
            return buffers.extract(offset, size, partial);
        });
    }

    std::future<void> write(const ByteArray& data, int64_t offset) {
        return thread_pool.enqueue([this, data, offset]() {
            std::lock_guard<std::mutex> lock(write_lock);
            auto file = get_file();
            try {
                file->write(data, offset);
                put_file(file);
            } catch (...) {
                put_file(file);
                throw;
            }
        });
    }

    FilePoolPseudoFile get_pseudo_file() {
        return FilePoolPseudoFile(this);
    }

    void close() {
        std::lock_guard<std::mutex> lock(pool_lock);
        while (!file_pool.empty()) {
            auto file = get_file();
            file->close();
        }
    }

};


class TemporaryDirectory {
    std::string path;
    bool cleanup_on_destroy = true;
    
    std::string find_random_suffix() {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(0, 15);
        std::string hex_chars = "0123456789abcdef";
        std::string random_suffix;
        for (int i = 0; i < 8; ++i) {
            random_suffix += hex_chars[dis(gen)];
        }
        return random_suffix;
    }

public:
    TemporaryDirectory(std::string parent, std::string prefix = "tmp.") {
        if (parent == "") parent = std::filesystem::temp_directory_path().string();
        path = parent + "/" + prefix + find_random_suffix();
        uint8_t counter = 0;
        while (std::filesystem::exists(path)) {
            path = parent + "/" + prefix + find_random_suffix();
            counter += 1;
            if (counter > 100) {
                throw std::runtime_error("failed to find a unique directory name in " + parent);
            }
        }
        std::error_code ec;
        if (!std::filesystem::create_directories(path, ec)) {
            throw std::runtime_error("failed to create temporary directory " +
                path + " (" + ec.message() + ")");
        }
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;
    TemporaryDirectory(TemporaryDirectory&& other) noexcept 
        : path(std::move(other.path)), cleanup_on_destroy(other.cleanup_on_destroy) {
        other.cleanup_on_destroy = false;
    }
    
    ~TemporaryDirectory() {
        if (cleanup_on_destroy) cleanup();
    }

    void cleanup() {
        if (std::filesystem::exists(path)) {
            std::error_code ec;
            std::filesystem::remove_all(path, ec);
            if (ec) {
                std::cerr << "WARNING: failed to remove temporary directory " 
                    << path << " (" << ec.message() << ")" << std::endl;
            }
        }
    }

    std::string file(const std::string& name) const {
        return path + "/" + name;
    }

};


class ZipWriter {
    struct ZipEntry {
        std::string name;
        uint32_t crc32;
        uint64_t compressed_size;
        uint64_t uncompressed_size;
        uint64_t local_header_offset;
        uint16_t compression_method;
    };
    
    std::shared_ptr<File> file;
    std::vector<ZipEntry> entries;
    int64_t current_offset = 0;
    bool closed = false;
    
    void write_bytes(const std::vector<uint8_t>& bytes) {
        file->write(ByteArray(bytes));
        current_offset += bytes.size();
    }

    template<typename T>
    void write_int_le(T value) {
        constexpr size_t num_bytes = sizeof(T);
        std::vector<uint8_t> bytes(num_bytes);
        for (size_t i = 0; i < num_bytes; ++i) {
            bytes[i] = static_cast<uint8_t>((value >> (i * 8)) & 0xFF);
        }
        write_bytes(std::move(bytes));
    }
    
public:
    ZipWriter(const std::string& path) {
        file = open_file(path, "w");
    }
    
    ~ZipWriter() {
        try {
            close();
        } catch (...) {
            // Suppress exceptions in destructor
        }
    }
    
    void add_entry(const std::string& name, ByteStream stream, int8_t compression_level = 1) {
        ZipEntry entry;
        entry.name = name;
        entry.local_header_offset = current_offset;
        entry.compression_method = 8; // 8=deflate
        
        // Write local file header with data descriptor flag
        write_int_le<uint32_t>(0x04034b50); // Local file header signature
        write_int_le<uint16_t>(45); // Version needed to extract (4.5 for ZIP64)
        write_int_le<uint16_t>(0x0008); // General purpose bit flag (bit 3 set = data descriptor)
        write_int_le<uint16_t>(entry.compression_method); // Compression method
        write_int_le<uint16_t>(0); // File last modification time (MS-DOS format)
        write_int_le<uint16_t>(0); // File last modification date (MS-DOS format)
        write_int_le<uint32_t>(0); // CRC-32 (set to 0, will be in data descriptor)
        write_int_le<uint32_t>(0); // Compressed size (set to 0, will be in data descriptor)
        write_int_le<uint32_t>(0); // Uncompressed size (set to 0, will be in data descriptor)
        write_int_le<uint16_t>(name.size()); // File name length
        write_int_le<uint16_t>(0); // Extra field length (no extra field in local header)
        
        // Write file name
        write_bytes(std::vector<uint8_t>(name.begin(), name.end()));
        
        // Create compression stream with CRC32 calculation enabled
        auto comp_stream = CompressionStream(
            std::move(stream),
            "deflate",
            compression_level,
            32768, // chunk_size
            32768, // buffer_size
            true   // compute_crc32
        );
        
        // Write compressed/uncompressed data
        while (true) {
            auto chunk = comp_stream.read_chunk();
            if (chunk.empty()) break;
            file->write(chunk);
            current_offset += chunk.size();
        }
        
        // Get CRC32 and sizes from CompressionStream
        entry.crc32 = comp_stream.crc32;
        entry.uncompressed_size = comp_stream.uncompressed_size;
        entry.compressed_size = comp_stream.compressed_size;
        
        // Write data descriptor (ZIP64)
        write_int_le<uint32_t>(0x08074b50); // Data descriptor signature
        write_int_le<uint32_t>(entry.crc32); // CRC-32
        write_int_le<uint64_t>(entry.compressed_size); // Compressed size
        write_int_le<uint64_t>(entry.uncompressed_size); // Uncompressed size
        
        entries.push_back(entry);
    }
    
    void close() {
        if (closed) return; // Already closed
        
        // Write central directory
        int64_t central_dir_start = current_offset;
        
        for (const auto& entry : entries) {
            write_int_le<uint32_t>(0x02014b50); // Central directory file header signature
            write_int_le<uint16_t>(45); // Version made by (4.5 for ZIP64)
            write_int_le<uint16_t>(45); // Version needed to extract
            write_int_le<uint16_t>(0); // General purpose bit flag
            write_int_le<uint16_t>(entry.compression_method); // Compression method
            write_int_le<uint16_t>(0); // File last modification time
            write_int_le<uint16_t>(0); // File last modification date
            write_int_le<uint32_t>(entry.crc32); // CRC-32
            write_int_le<uint32_t>(0xFFFFFFFF); // Compressed size (ZIP64)
            write_int_le<uint32_t>(0xFFFFFFFF); // Uncompressed size (ZIP64)
            write_int_le<uint16_t>(entry.name.size()); // File name length
            write_int_le<uint16_t>(28); // Extra field length
            write_int_le<uint16_t>(0); // File comment length
            write_int_le<uint16_t>(0); // Disk number start
            write_int_le<uint16_t>(0); // Internal file attributes
            write_int_le<uint32_t>(0); // External file attributes
            write_int_le<uint32_t>(0xFFFFFFFF); // Relative offset of local header (ZIP64)
            
            // Write file name
            write_bytes(std::vector<uint8_t>(entry.name.begin(), entry.name.end()));
            
            // Write ZIP64 extra field
            write_int_le<uint16_t>(0x0001); // ZIP64 extended information extra field tag
            write_int_le<uint16_t>(24); // Size of this extra block
            write_int_le<uint64_t>(entry.uncompressed_size); // Uncompressed size
            write_int_le<uint64_t>(entry.compressed_size); // Compressed size
            write_int_le<uint64_t>(entry.local_header_offset); // Relative offset of local header
        }
        
        int64_t central_dir_size = current_offset - central_dir_start;
        
        // Write ZIP64 end of central directory record
        write_int_le<uint32_t>(0x06064b50); // ZIP64 end of central directory signature
        write_int_le<uint64_t>(44); // Size of ZIP64 end of central directory record
        write_int_le<uint16_t>(45); // Version made by
        write_int_le<uint16_t>(45); // Version needed to extract
        write_int_le<uint32_t>(0); // Number of this disk
        write_int_le<uint32_t>(0); // Disk where central directory starts
        write_int_le<uint64_t>(entries.size()); // Number of central directory records on this disk
        write_int_le<uint64_t>(entries.size()); // Total number of central directory records
        write_int_le<uint64_t>(central_dir_size); // Size of central directory
        write_int_le<uint64_t>(central_dir_start); // Offset of start of central directory
        
        // Write ZIP64 end of central directory locator
        write_int_le<uint32_t>(0x07064b50); // ZIP64 end of central directory locator signature
        write_int_le<uint32_t>(0); // Number of the disk with the start of the ZIP64 end of central directory
        write_int_le<uint64_t>(current_offset - 56); // Relative offset of the ZIP64 end of central directory record
        write_int_le<uint32_t>(1); // Total number of disks
        
        // Write end of central directory record
        write_int_le<uint32_t>(0x06054b50); // End of central directory signature
        write_int_le<uint16_t>(0xFFFF); // Number of this disk
        write_int_le<uint16_t>(0xFFFF); // Disk where central directory starts
        write_int_le<uint16_t>(0xFFFF); // Number of central directory records on this disk
        write_int_le<uint16_t>(0xFFFF); // Total number of central directory records
        write_int_le<uint32_t>(0xFFFFFFFF); // Size of central directory
        write_int_le<uint32_t>(0xFFFFFFFF); // Offset of start of central directory
        write_int_le<uint16_t>(0); // ZIP file comment length
        
        file->close();
        closed = true;
    }
};
