#pragma once

#include "includes.cpp"


template<typename T>
struct Sparse2DArray {
    std::vector<T> values;
    std::vector<uint32_t> row;
    std::vector<uint32_t> col;
    std::array<uint32_t, 2> shape;
};


template<typename T>
std::vector<T> resize_2d_array(
    const std::vector<T>& data,
    const std::vector<int64_t>& shape,
    const std::vector<int64_t>& new_shape
) {
    if (shape.size() != 2 || new_shape.size() != 2) {
        throw std::invalid_argument("resize_2d_array: only 2D arrays are supported");
    }
    
    int64_t old_rows = shape[0];
    int64_t old_cols = shape[1];
    int64_t new_rows = new_shape[0];
    int64_t new_cols = new_shape[1];
    
    std::vector<T> new_data(new_rows * new_cols);
    
    // Calculate scaling factors
    double row_scale = static_cast<double>(old_rows - 1) / static_cast<double>(new_rows - 1);
    double col_scale = static_cast<double>(old_cols - 1) / static_cast<double>(new_cols - 1);
    
    // Handle edge case of single dimension
    if (new_rows == 1) row_scale = 0.0;
    if (new_cols == 1) col_scale = 0.0;
    
    for (int64_t i = 0; i < new_rows; i++) {
        for (int64_t j = 0; j < new_cols; j++) {
            // Calculate source coordinates
            double src_row = i * row_scale;
            double src_col = j * col_scale;
            
            // Get integer parts (floor)
            int64_t row0 = static_cast<int64_t>(src_row);
            int64_t col0 = static_cast<int64_t>(src_col);
            int64_t row1 = std::min(row0 + 1, old_rows - 1);
            int64_t col1 = std::min(col0 + 1, old_cols - 1);
            
            // Get fractional parts
            double row_frac = src_row - row0;
            double col_frac = src_col - col0;
            
            // Get the four corner values
            T top_left = data[row0 * old_cols + col0];
            T top_right = data[row0 * old_cols + col1];
            T bottom_left = data[row1 * old_cols + col0];
            T bottom_right = data[row1 * old_cols + col1];
            
            // Bilinear interpolation
            T top = top_left * (1.0 - col_frac) + top_right * col_frac;
            T bottom = bottom_left * (1.0 - col_frac) + bottom_right * col_frac;
            T result = top * (1.0 - row_frac) + bottom * row_frac;
            
            new_data[i * new_cols + j] = result;
        }
    }
    
    return new_data;
}


template<typename T>
Sparse2DArray<T> resize_2d_array(
    const Sparse2DArray<T>& data,
    const std::array<uint32_t, 2>& new_shape
) {
    uint32_t old_rows = data.shape[0];
    uint32_t old_cols = data.shape[1];
    uint32_t new_rows = new_shape[0];
    uint32_t new_cols = new_shape[1];
    
    Sparse2DArray<T> result;
    result.shape = new_shape;
    
    // Calculate scaling factors
    double row_scale = static_cast<double>(old_rows - 1) / static_cast<double>(new_rows - 1);
    double col_scale = static_cast<double>(old_cols - 1) / static_cast<double>(new_cols - 1);
    
    // Handle edge case of single dimension
    if (new_rows == 1) row_scale = 0.0;
    if (new_cols == 1) col_scale = 0.0;
    
    // Build a dense lookup map for the sparse input for efficient access
    std::unordered_map<uint64_t, T> sparse_map;
    for (size_t i = 0; i < data.values.size(); i++) {
        uint64_t key = (static_cast<uint64_t>(data.row[i]) << 32) | data.col[i];
        sparse_map[key] = data.values[i];
    }
    
    // Helper to get value from sparse map
    auto get_value = [&](uint32_t row, uint32_t col) -> T {
        uint64_t key = (static_cast<uint64_t>(row) << 32) | col;
        auto it = sparse_map.find(key);
        return (it != sparse_map.end()) ? it->second : T(0);
    };
    
    // Process each non-zero element in the input
    // For sparse arrays, we iterate through the non-zero values and their neighborhoods
    std::unordered_map<uint64_t, T> result_map;
    
    for (size_t idx = 0; idx < data.values.size(); idx++) {
        uint32_t src_row = data.row[idx];
        uint32_t src_col = data.col[idx];
        T value = data.values[idx];
        
        // Skip zero values
        if (value == T(0)) continue;
        
        // Calculate the range of output pixels influenced by this input pixel
        // Each input pixel can influence multiple output pixels
        uint32_t out_row_min = static_cast<uint32_t>(std::max(0.0, std::floor(src_row / row_scale - 1)));
        uint32_t out_row_max = static_cast<uint32_t>(std::min(static_cast<double>(new_rows - 1), 
                                                                std::ceil(src_row / row_scale + 1)));
        uint32_t out_col_min = static_cast<uint32_t>(std::max(0.0, std::floor(src_col / col_scale - 1)));
        uint32_t out_col_max = static_cast<uint32_t>(std::min(static_cast<double>(new_cols - 1), 
                                                                std::ceil(src_col / col_scale + 1)));
        
        for (uint32_t out_row = out_row_min; out_row <= out_row_max; out_row++) {
            for (uint32_t out_col = out_col_min; out_col <= out_col_max; out_col++) {
                // Calculate source coordinates for this output pixel
                double src_row_f = out_row * row_scale;
                double src_col_f = out_col * col_scale;
                
                // Get integer parts (floor)
                uint32_t row0 = static_cast<uint32_t>(src_row_f);
                uint32_t col0 = static_cast<uint32_t>(src_col_f);
                uint32_t row1 = std::min(row0 + 1, old_rows - 1);
                uint32_t col1 = std::min(col0 + 1, old_cols - 1);
                
                // Get fractional parts
                double row_frac = src_row_f - row0;
                double col_frac = src_col_f - col0;
                
                // Get the four corner values
                T top_left = get_value(row0, col0);
                T top_right = get_value(row0, col1);
                T bottom_left = get_value(row1, col0);
                T bottom_right = get_value(row1, col1);
                
                // Bilinear interpolation
                T top = top_left * (1.0 - col_frac) + top_right * col_frac;
                T bottom = bottom_left * (1.0 - col_frac) + bottom_right * col_frac;
                T interpolated = top * (1.0 - row_frac) + bottom * row_frac;
                
                // Store if non-zero
                if (interpolated != T(0)) {
                    uint64_t key = (static_cast<uint64_t>(out_row) << 32) | out_col;
                    result_map[key] = interpolated;
                }
            }
        }
    }
    
    // Convert map to sparse format
    result.values.reserve(result_map.size());
    result.row.reserve(result_map.size());
    result.col.reserve(result_map.size());
    
    for (const auto& [key, value] : result_map) {
        uint32_t row = static_cast<uint32_t>(key >> 32);
        uint32_t col = static_cast<uint32_t>(key & 0xFFFFFFFF);
        result.row.push_back(row);
        result.col.push_back(col);
        result.values.push_back(value);
    }
    
    return result;
}


template<typename T>
class NDArray {

    static int64_t get_size_from_shape(const std::vector<int64_t>& shape) {
        int64_t total_size = 1;
        for (int64_t dim_size : shape) {
            total_size *= dim_size;
        }
        return total_size;
    }

    // Helper to normalize and validate axis
    int64_t normalize_axis(int64_t axis, const std::string& method_name = "") const {
        size_t ndim = shape.size();
        if (axis < 0) {
            axis += static_cast<int64_t>(ndim);
        }
        if (axis < 0 || axis >= static_cast<int64_t>(ndim)) {
            throw std::invalid_argument((method_name.empty() ? "axis" : method_name) + ": axis out of bounds");
        }
        return axis;
    }

    // Helper to iterate along an axis and apply operations (const version)
    template<typename OpFunc>
    void iterate_along_axis(int64_t axis, OpFunc op_func) const {
        axis = normalize_axis(axis);
        
        std::vector<int64_t> strides = get_strides();
        int64_t axis_size = shape[axis];
        
        // Calculate outer size (product of dimensions before axis)
        int64_t outer_size = 1;
        for (int64_t i = 0; i < axis; i++) {
            outer_size *= shape[i];
        }
        
        // Calculate inner size (product of dimensions after axis)
        int64_t inner_size = 1;
        for (size_t i = axis + 1; i < shape.size(); i++) {
            inner_size *= shape[i];
        }
        
        // Iterate and apply operation
        for (int64_t outer = 0; outer < outer_size; outer++) {
            for (int64_t inner = 0; inner < inner_size; inner++) {
                // Calculate flat indices for this slice along axis
                std::vector<int64_t> flat_indices(axis_size);
                for (int64_t axis_idx = 0; axis_idx < axis_size; axis_idx++) {
                    int64_t flat_idx = 0;
                    int64_t temp_outer = outer;
                    for (int64_t i = axis - 1; i >= 0; i--) {
                        flat_idx += (temp_outer % shape[i]) * strides[i];
                        temp_outer /= shape[i];
                    }
                    flat_idx += axis_idx * strides[axis];
                    flat_idx += inner;
                    flat_indices[axis_idx] = flat_idx;
                }
                
                // Apply operation to this slice
                op_func(flat_indices);
            }
        }
    }

    // Helper to iterate along an axis and apply operations (non-const version)
    template<typename OpFunc>
    void iterate_along_axis(int64_t axis, OpFunc op_func) {
        // Call const version with const_cast to avoid code duplication
        const_cast<const NDArray<T>*>(this)->iterate_along_axis(axis, op_func);
    }

    // Helper for reduction operations along an axis
    template<typename ReduceOp, typename FinalizeOp>
    NDArray<T> reduce_along_axis(
        int64_t axis,
        T initial_value,
        ReduceOp reduce_op,
        FinalizeOp finalize_op
    ) const {
        // Reduce all elements
        if (axis == -1) {
            T result = initial_value;
            for (const T& val : data) {
                result = reduce_op(result, val);
            }
            result = finalize_op(result, size());
            return NDArray<T>(std::vector<T>{result}, std::vector<int64_t>{1});
        }
        
        // Normalize and validate axis
        axis = normalize_axis(axis);
        
        // Calculate new shape (remove the axis dimension)
        std::vector<int64_t> new_shape;
        for (size_t i = 0; i < shape.size(); i++) {
            if (static_cast<int64_t>(i) != axis) {
                new_shape.push_back(shape[i]);
            }
        }
        
        // Handle case where result is scalar
        if (new_shape.empty()) {
            new_shape.push_back(1);
        }
        
        int64_t new_size = get_size_from_shape(new_shape);
        std::vector<T> new_data(new_size, initial_value);
        int64_t axis_size = shape[axis];
        
        // Reduce along axis using iterate_along_axis
        int64_t output_idx = 0;
        iterate_along_axis(axis, [&](const std::vector<int64_t>& indices) {
            T result = initial_value;
            for (int64_t flat_idx : indices) {
                result = reduce_op(result, data[flat_idx]);
            }
            new_data[output_idx++] = result;
        });
        
        // Apply finalization operation
        for (T& val : new_data) {
            val = finalize_op(val, axis_size);
        }
        
        return NDArray<T>(std::move(new_data), new_shape);
    }


public:
    std::vector<T> data;
    std::vector<int64_t> shape;

    NDArray(
        const std::vector<T>& data,
        const std::vector<int64_t>& shape
    ) : data(data), shape(shape) {}
    NDArray(
        std::vector<T>&& data,
        const std::vector<int64_t>& shape
    ) : data(std::move(data)), shape(shape) {}
    NDArray(
        const std::vector<int64_t>& shape,
        const T& initial_value = T()
    ) : shape(shape) {
        data.resize(get_size_from_shape(shape));
        fill(initial_value);
    }

    int64_t size() const {
        return static_cast<int64_t>(data.size());
    }

    const T& operator[](int64_t index) const {
        return data[index];
    }
    T& operator[](int64_t index) {
        return data[index];
    }

    void fill(const T& value) {
        std::fill(data.begin(), data.end(), value);
    }
    
    NDArray<T> reshape(const std::vector<int64_t>& new_shape) const {
        int64_t new_total_size = 1;
        int64_t infer_dim_index = -1;
        for (size_t i = 0; i < new_shape.size(); i++) {
            if (new_shape[i] == -1) {
                if (infer_dim_index != -1) {
                    throw std::invalid_argument("can only specify one unknown dimension in reshape");
                }
                infer_dim_index = static_cast<int64_t>(i);
            } else if (new_shape[i] <= 0) {
                throw std::invalid_argument("shape dimensions must be positive or -1");
            } else {
                new_total_size *= new_shape[i];
            }
        }
        std::vector<int64_t> final_shape = new_shape;
        if (infer_dim_index != -1) {
            int64_t current_size = size();
            if (current_size % new_total_size != 0) {
                throw std::invalid_argument("reshape array: size mismatch with inferred dimension");
            }
            final_shape[infer_dim_index] = current_size / new_total_size;
            new_total_size = current_size;
        }
        if (new_total_size != size()) {
            throw std::invalid_argument("reshape array: total size must remain the same");
        }
        return NDArray<T>(data, final_shape);
    }

    std::vector<int64_t> get_strides(const std::vector<int64_t>* custom_shape = nullptr) const {
        const std::vector<int64_t>& shape_to_use = custom_shape ? *custom_shape : this->shape;
        size_t ndim = shape_to_use.size();
        if (ndim == 0) return {};
        std::vector<int64_t> strides(ndim);
        strides[ndim - 1] = 1;
        for (int64_t i = static_cast<int64_t>(ndim) - 2; i >= 0; i--) {
            strides[i] = strides[i + 1] * shape_to_use[i + 1];
        }
        return strides;
    }

    // Transpose the array in-place by permuting dimensions
    // If axes is empty, reverses the order of dimensions (default transpose)
    // Otherwise, permutes dimensions according to the axes vector
    void transpose(const std::vector<int64_t>& axes = {}) {
        size_t ndim = shape.size();
        
        // Determine the permutation order
        std::vector<int64_t> perm;
        if (axes.empty()) {
            // Default: reverse all dimensions
            perm.resize(ndim);
            for (size_t i = 0; i < ndim; i++) {
                perm[i] = static_cast<int64_t>(ndim - 1 - i);
            }
        } else {
            // Use provided axes
            if (axes.size() != ndim) {
                throw std::invalid_argument("transpose: axes length must match number of dimensions");
            }
            perm = axes;
            
            // Validate axes
            std::vector<bool> used(ndim, false);
            for (size_t i = 0; i < ndim; i++) {
                int64_t axis = perm[i];
                if (axis < 0 || axis >= static_cast<int64_t>(ndim)) {
                    throw std::invalid_argument("transpose: axis out of bounds");
                }
                if (used[axis]) {
                    throw std::invalid_argument("transpose: repeated axis");
                }
                used[axis] = true;
            }
        }
        
        // Calculate new shape
        std::vector<int64_t> new_shape(ndim);
        for (size_t i = 0; i < ndim; i++) {
            new_shape[i] = shape[perm[i]];
        }
        
        // Calculate strides for original and new shape
        std::vector<int64_t> old_strides = get_strides();
        std::vector<int64_t> new_strides = get_strides(&new_shape);
        
        // Create transposed data
        std::vector<T> new_data(data.size());
        std::vector<int64_t> indices(ndim, 0);
        
        for (int64_t flat_idx = 0; flat_idx < size(); flat_idx++) {
            // Calculate old multi-dimensional indices
            int64_t temp = flat_idx;
            for (size_t i = 0; i < ndim; i++) {
                indices[i] = temp / old_strides[i];
                temp %= old_strides[i];
            }
            
            // Permute indices
            std::vector<int64_t> new_indices(ndim);
            for (size_t i = 0; i < ndim; i++) {
                new_indices[i] = indices[perm[i]];
            }
            
            // Calculate new flat index
            int64_t new_flat_idx = 0;
            for (size_t i = 0; i < ndim; i++) {
                new_flat_idx += new_indices[i] * new_strides[i];
            }
            
            new_data[new_flat_idx] = data[flat_idx];
        }
        
        data = std::move(new_data);
        shape = new_shape;
    }

    // Transpose the array (returns new array)
    // If axes is empty, reverses the order of dimensions (default transpose)
    // Otherwise, permutes dimensions according to the axes vector
    NDArray<T> transposed(const std::vector<int64_t>& axes = {}) const {
        NDArray<T> result = *this;
        result.transpose(axes);
        return result;
    }    // Flatten the array to 1D
    // Returns a new NDArray with shape {size()}
    NDArray<T> flat() const {
        return NDArray<T>(data, std::vector<int64_t>{size()});
    }

    // Calculate mean along an optional axis
    // If axis is -1 (default), returns scalar mean of all elements
    // Otherwise, returns NDArray with reduced dimension along specified axis
    NDArray<T> mean(int64_t axis = -1) const {
        return reduce_along_axis(
            axis,
            T(),
            [](const T& a, const T& b) { return a + b; },
            [](const T& sum, int64_t count) { return sum / static_cast<T>(count); }
        );
    }

    // Calculate minimum along an optional axis
    // If axis is -1 (default), returns scalar minimum of all elements
    // Otherwise, returns NDArray with reduced dimension along specified axis
    NDArray<T> min(int64_t axis = -1) const {
        if (data.empty()) {
            throw std::invalid_argument("min: cannot compute minimum of empty array");
        }
        return reduce_along_axis(
            axis,
            std::numeric_limits<T>::max(),
            [](const T& a, const T& b) { return std::min(a, b); },
            [](const T& val, int64_t) { return val; }
        );
    }

    // Calculate maximum along an optional axis
    // If axis is -1 (default), returns scalar maximum of all elements
    // Otherwise, returns NDArray with reduced dimension along specified axis
    NDArray<T> max(int64_t axis = -1) const {
        if (data.empty()) {
            throw std::invalid_argument("max: cannot compute maximum of empty array");
        }
        return reduce_along_axis(
            axis,
            std::numeric_limits<T>::lowest(),
            [](const T& a, const T& b) { return std::max(a, b); },
            [](const T& val, int64_t) { return val; }
        );
    }

    // Calculate quantile along an optional axis
    // q: quantile value between 0 and 1 (e.g., 0.5 for median)
    // axis: axis along which to compute quantile (-1 for all elements)
    // If axis is -1 (default), returns scalar quantile of all elements
    // Otherwise, returns NDArray with reduced dimension along specified axis
    NDArray<T> quantile(double q, int64_t axis = -1) const {
        if (data.empty()) {
            throw std::invalid_argument("quantile: cannot compute quantile of empty array");
        }
        if (q < 0.0 || q > 1.0) {
            throw std::invalid_argument("quantile: q must be between 0 and 1");
        }
        
        size_t ndim = shape.size();
        
        // Compute quantile of all elements
        if (axis == -1) {
            std::vector<T> sorted_data = data;
            std::sort(sorted_data.begin(), sorted_data.end());
            
            double pos = q * (sorted_data.size() - 1);
            size_t lower_idx = static_cast<size_t>(std::floor(pos));
            size_t upper_idx = static_cast<size_t>(std::ceil(pos));
            
            T result;
            if (lower_idx == upper_idx) {
                result = sorted_data[lower_idx];
            } else {
                double weight = pos - lower_idx;
                result = sorted_data[lower_idx] * (1.0 - weight) + sorted_data[upper_idx] * weight;
            }
            
            return NDArray<T>(std::vector<T>{result}, std::vector<int64_t>{1});
        }
        
        // Normalize negative axis
        if (axis < 0) {
            axis += static_cast<int64_t>(ndim);
        }
        
        // Validate axis
        if (axis < 0 || axis >= static_cast<int64_t>(ndim)) {
            throw std::invalid_argument("quantile: axis out of bounds");
        }
        
        // Calculate new shape (remove the axis dimension)
        std::vector<int64_t> new_shape;
        for (size_t i = 0; i < ndim; i++) {
            if (static_cast<int64_t>(i) != axis) {
                new_shape.push_back(shape[i]);
            }
        }
        
        // Handle case where result is scalar
        if (new_shape.empty()) {
            new_shape.push_back(1);
        }
        
        int64_t new_size = get_size_from_shape(new_shape);
        std::vector<T> new_data(new_size);
        
        // Calculate strides
        std::vector<int64_t> strides = get_strides();
        int64_t axis_size = shape[axis];
        
        // For each output element, collect values along axis and compute quantile
        std::vector<int64_t> indices(ndim, 0);
        std::vector<T> temp_values;
        temp_values.reserve(axis_size);
        
        for (int64_t out_idx = 0; out_idx < new_size; out_idx++) {
            // Calculate the multi-dimensional index for this output element
            int64_t temp = out_idx;
            std::vector<int64_t> out_indices(new_shape.size());
            for (int64_t i = static_cast<int64_t>(new_shape.size()) - 1; i >= 0; i--) {
                out_indices[i] = temp % new_shape[i];
                temp /= new_shape[i];
            }
            
            // Map back to original indices (insert axis dimension)
            size_t out_dim_idx = 0;
            for (size_t i = 0; i < ndim; i++) {
                if (static_cast<int64_t>(i) == axis) {
                    indices[i] = 0; // Will iterate over this
                } else {
                    indices[i] = out_indices[out_dim_idx++];
                }
            }
            
            // Collect all values along the axis
            temp_values.clear();
            for (int64_t axis_idx = 0; axis_idx < axis_size; axis_idx++) {
                indices[axis] = axis_idx;
                
                // Calculate flat index
                int64_t flat_idx = 0;
                for (size_t i = 0; i < ndim; i++) {
                    flat_idx += indices[i] * strides[i];
                }
                
                temp_values.push_back(data[flat_idx]);
            }
            
            // Sort and compute quantile
            std::sort(temp_values.begin(), temp_values.end());
            
            double pos = q * (temp_values.size() - 1);
            size_t lower_idx = static_cast<size_t>(std::floor(pos));
            size_t upper_idx = static_cast<size_t>(std::ceil(pos));
            
            if (lower_idx == upper_idx) {
                new_data[out_idx] = temp_values[lower_idx];
            } else {
                double weight = pos - lower_idx;
                new_data[out_idx] = temp_values[lower_idx] * (1.0 - weight) + temp_values[upper_idx] * weight;
            }
        }
        
        return NDArray<T>(std::move(new_data), new_shape);
    }

    // Generic generator for iterating over slices along any axis
    class AxisIterator : public GeneratorBase<AxisIterator, NDArray<T>> {
        const NDArray<T>* array;
        int64_t axis;
        int64_t axis_size;
        int64_t current_slice;
        std::vector<int64_t> strides;
        int64_t outer_size;
        int64_t inner_size;
        std::vector<int64_t> slice_shape;

    public:
        AxisIterator(const NDArray<T>* arr, int64_t ax) 
            : array(arr), axis(ax), current_slice(0) {
            
            // Normalize and validate axis
            axis = array->normalize_axis(axis, "iter_axis");
            
            strides = array->get_strides();
            axis_size = array->shape[axis];
            
            // Calculate outer size (product of dimensions before axis)
            outer_size = 1;
            for (int64_t i = 0; i < axis; i++) {
                outer_size *= array->shape[i];
            }
            
            // Calculate inner size (product of dimensions after axis)
            inner_size = 1;
            for (size_t i = axis + 1; i < array->shape.size(); i++) {
                inner_size *= array->shape[i];
            }
            
            // Calculate slice shape (remove the iterated axis)
            for (size_t i = 0; i < array->shape.size(); i++) {
                if (static_cast<int64_t>(i) != axis) {
                    slice_shape.push_back(array->shape[i]);
                }
            }
            
            // Handle case where slice is scalar (1D array iterated)
            if (slice_shape.empty()) {
                slice_shape.push_back(1);
            }
        }

        typename GeneratorBase<AxisIterator, NDArray<T>>::NextResult next() {
            if (current_slice >= axis_size) {
                return {NDArray<T>({}, {}), true};
            }
            
            // Calculate total size of the slice
            int64_t slice_size = outer_size * inner_size;
            std::vector<T> slice_data;
            slice_data.reserve(slice_size);
            
            // Collect data for this slice
            for (int64_t outer = 0; outer < outer_size; outer++) {
                for (int64_t inner = 0; inner < inner_size; inner++) {
                    // Calculate flat index for this element
                    int64_t flat_idx = 0;
                    int64_t temp_outer = outer;
                    for (int64_t i = axis - 1; i >= 0; i--) {
                        flat_idx += (temp_outer % array->shape[i]) * strides[i];
                        temp_outer /= array->shape[i];
                    }
                    flat_idx += current_slice * strides[axis];
                    flat_idx += inner;
                    
                    slice_data.push_back(array->data[flat_idx]);
                }
            }
            
            current_slice++;
            return {NDArray<T>(std::move(slice_data), slice_shape), false};
        }
    };

    // Iterate over slices along any axis (returns generator)
    // For a 3D array with shape {3, 4, 5}:
    // - iter_axis(0) yields 3 slices of shape {4, 5}
    // - iter_axis(1) yields 4 slices of shape {3, 5}
    // - iter_axis(2) yields 5 slices of shape {3, 4}
    AxisIterator iter_axis(int64_t axis) const {
        return AxisIterator(this, axis);
    }

    // Iterate over rows (first dimension) - convenience method
    AxisIterator iter_rows() const {
        return iter_axis(0);
    }

    // Iterate over columns (second dimension) - convenience method
    // Only meaningful for 2D+ arrays
    AxisIterator iter_cols() const {
        if (shape.size() < 2) {
            throw std::invalid_argument("iter_cols: array must have at least 2 dimensions");
        }
        return iter_axis(1);
    }

    // Sort the array in-place
    // If axis is -1 (default), sorts the flattened array
    // Otherwise, sorts along the specified axis
    void sort(int64_t axis = -1) {
        // Sort flattened array
        if (axis == -1) {
            std::sort(data.begin(), data.end());
            return;
        }
        
        // Sort along axis using helper
        std::vector<T> temp_values(shape[axis]);
        iterate_along_axis(axis, [&](const std::vector<int64_t>& indices) {
            // Collect values
            for (size_t i = 0; i < indices.size(); i++) {
                temp_values[i] = data[indices[i]];
            }
            // Sort
            std::sort(temp_values.begin(), temp_values.end());
            // Write back
            for (size_t i = 0; i < indices.size(); i++) {
                data[indices[i]] = temp_values[i];
            }
        });
    }

    // Sort the array (returns new array)
    // If axis is -1 (default), sorts the flattened array
    // Otherwise, sorts along the specified axis
    NDArray<T> sorted(int64_t axis = -1) const {
        NDArray<T> result = *this;
        result.sort(axis);
        return result;
    }

    // Reverse the array in-place
    // If axis is -1 (default), reverses the flattened array
    // Otherwise, reverses along the specified axis
    void reverse(int64_t axis = -1) {
        // Reverse flattened array
        if (axis == -1) {
            std::reverse(data.begin(), data.end());
            return;
        }
        
        // Reverse along axis using helper
        iterate_along_axis(axis, [&](const std::vector<int64_t>& indices) {
            // Reverse by swapping from both ends
            size_t n = indices.size();
            for (size_t i = 0; i < n / 2; i++) {
                std::swap(data[indices[i]], data[indices[n - 1 - i]]);
            }
        });
    }

    // Reverse the array (returns new array)
    // If axis is -1 (default), reverses the flattened array
    // Otherwise, reverses along the specified axis
    NDArray<T> reversed(int64_t axis = -1) const {
        NDArray<T> result = *this;
        result.reverse(axis);
        return result;
    }

    




};
