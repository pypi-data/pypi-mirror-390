#pragma once

#include "includes.cpp"


// Helper to detect if a type is a container (vector-like)
template<typename T, typename = void>
struct is_container : std::false_type {};

template<typename T>
struct is_container<T, std::void_t<
    typename std::decay_t<T>::value_type,
    decltype(std::begin(std::declval<T>())),
    decltype(std::end(std::declval<T>()))
>> : std::true_type {};

// Helper to detect if a type supports operator<<
template<typename T, typename = void>
struct has_ostream_operator : std::false_type {};

template<typename T>
struct has_ostream_operator<T, std::void_t<
    decltype(std::declval<std::ostream&>() << std::declval<T>())
>> : std::true_type {};

template<typename T>
std::string fstring_tostr(T&& value) {
    using DecayT = std::decay_t<T>;
    if constexpr (std::is_same_v<DecayT, std::string>) {
        return std::forward<T>(value);
    } else if constexpr (std::is_same_v<DecayT, const char*>) {
        return std::string(value);
    } else if constexpr (std::is_arithmetic_v<DecayT>) {
        return std::to_string(std::forward<T>(value));
    } else if constexpr (is_container<T>::value && !std::is_same_v<DecayT, std::string>) {
        // Handle vector-like containers
        std::ostringstream oss;
        oss << "[";
        auto it = std::begin(value);
        auto end_it = std::end(value);
        if (it != end_it) {
            oss << fstring_tostr(*it);
            ++it;
            for (; it != end_it; ++it) {
                oss << ", " << fstring_tostr(*it);
            }
        }
        oss << "]";
        return oss.str();
    } else if constexpr (has_ostream_operator<T>::value) {
        std::ostringstream oss;
        oss << std::forward<T>(value);
        return oss.str();
    } else {
        // For types without operator<<, return type name
        return std::string("<") + typeid(DecayT).name() + ">";
    }
}

template<typename... Args>
std::string fstring(const std::string& fmt, Args&&... args) {
    if constexpr (sizeof...(args) == 0) {
        return fmt;
    } else {
        std::ostringstream result;
        std::vector<std::string> arg_strings = {fstring_tostr(std::forward<Args>(args))...};
        size_t arg_index = 0;
        size_t pos = 0;
        size_t found = 0;
        while ((found = fmt.find("{}", pos)) != std::string::npos) {
            if (arg_index >= arg_strings.size()) {
                throw std::runtime_error("not enough arguments for format string");
            }
            result << fmt.substr(pos, found - pos);
            result << arg_strings[arg_index++];
            pos = found + 2;
        }
        if (arg_index < arg_strings.size()) {
            throw std::runtime_error("too many arguments for format string");
        }
        result << fmt.substr(pos);
        return result.str();
    }
}


template<typename... Args>
void print(const std::string& fmt, Args&&... args) {
    std::string message = fstring(fmt, std::forward<Args>(args)...);
    std::cout << message << std::flush;
}


std::string to_lowercase(std::string input) {
    std::transform(
        input.begin(), input.end(), input.begin(),
        [](unsigned char c) { return std::tolower(c); }
    );
    return input;
}

std::string to_uppercase(std::string input) {
    std::transform(
        input.begin(), input.end(), input.begin(),
        [](unsigned char c) { return std::toupper(c); }
    );
    return input;
}


std::vector<std::string> split_string(const std::string& input, char delimiter) {
    std::vector<std::string> result;
    std::istringstream stream(input);
    std::string item;
    while (std::getline(stream, item, delimiter)) {
        result.push_back(item);
    }
    return result;
}


std::string format_time(double seconds, int64_t precision = 0) {
    int64_t total_seconds = static_cast<int64_t>(seconds);
    int64_t hours = total_seconds / 3600;
    int64_t minutes = (total_seconds % 3600) / 60;
    double secs = seconds - (hours * 3600 + minutes * 60);
    char buffer[32];
    if (precision > 0) {
        snprintf(buffer, sizeof(buffer), "%02lld:%02lld:%0*.*f", 
                 hours, minutes, (int)precision + 3, (int)precision, secs);
    } else {
        snprintf(buffer, sizeof(buffer), "%02lld:%02lld:%02.0f", 
                 hours, minutes, secs);
    }
    return std::string(buffer);
}
