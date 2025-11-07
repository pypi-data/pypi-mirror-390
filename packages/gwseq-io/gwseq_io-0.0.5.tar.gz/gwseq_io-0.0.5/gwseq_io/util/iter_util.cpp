#pragma once

#include "includes.cpp"


template <typename Derived, typename Value>
class GeneratorBase {
public:
    struct NextResult {
        Value value;
        bool done;
    };

    class Iterator {
        Derived* gen;
        NextResult state;

    public:
        using iterator_category = std::input_iterator_tag;
        using value_type = Value;
        using reference = const Value&;
        using pointer = const Value*;
        using difference_type = std::ptrdiff_t;

        Iterator(Derived* g, bool at_end = false) : gen(g) {
            if (at_end) {
                state = {Value{}, true};
            } else {
                state = gen->next();
            }
        }

        reference operator*() const { return state.value; }
        pointer operator->() const { return &state.value; }

        Iterator& operator++() {
            state = gen->next();
            return *this;
        }

        bool operator!=(const Iterator& other) const {
            return state.done != other.state.done;
        }
    };

    Iterator begin() { return Iterator(static_cast<Derived*>(this), false); }
    Iterator end() { return Iterator(static_cast<Derived*>(this), true); }

    std::vector<Value> to_vector() {
        std::vector<Value> values;
        for (auto& value : *this) {
            values.push_back(value);
        }
        return values;
    }
};


template<typename T, typename Container>
bool is_in(const T& value, const Container& container) {
    return std::find(container.begin(), container.end(), value) != container.end();
}



