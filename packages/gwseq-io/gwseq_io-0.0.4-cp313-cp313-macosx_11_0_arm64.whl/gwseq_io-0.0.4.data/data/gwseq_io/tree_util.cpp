#pragma once

#include "includes.cpp"


// B+ Tree implementation
// All data is stored in leaf nodes
// Internal nodes only contain keys for navigation
template<typename K, typename V, int64_t ORDER = 4>
class BPlusTree {
private:
    struct Node;
    using NodePtr = std::shared_ptr<Node>;

    struct Node {
        bool is_leaf;
        std::vector<K> keys;
        std::vector<V> values;          // Only used in leaf nodes
        std::vector<NodePtr> children;  // Only used in internal nodes
        NodePtr next;                   // Only used in leaf nodes (for range queries)
        NodePtr parent;

        Node(bool leaf = false) : is_leaf(leaf) {}

        bool is_full() const {
            return keys.size() >= ORDER - 1;
        }

        bool is_underflow() const {
            return keys.size() < (ORDER / 2);
        }
    };

    NodePtr root;
    NodePtr first_leaf;  // Points to leftmost leaf for range queries
    int64_t size_;

    // Find the leaf node where key should be inserted/found
    NodePtr find_leaf(const K& key) const {
        if (!root) return nullptr;
        
        NodePtr current = root;
        while (!current->is_leaf) {
            size_t i = 0;
            while (i < current->keys.size() && key >= current->keys[i]) {
                i++;
            }
            current = current->children[i];
        }
        return current;
    }

    // Split a full node
    std::pair<K, NodePtr> split_node(NodePtr node) {
        size_t mid = node->keys.size() / 2;
        NodePtr new_node = std::make_shared<Node>(node->is_leaf);
        
        if (node->is_leaf) {
            // Split leaf node - copy mid key up to parent
            K split_key = node->keys[mid];
            
            // Move keys and values to new node
            new_node->keys.assign(node->keys.begin() + mid, node->keys.end());
            new_node->values.assign(node->values.begin() + mid, node->values.end());
            
            node->keys.erase(node->keys.begin() + mid, node->keys.end());
            node->values.erase(node->values.begin() + mid, node->values.end());
            
            // Update linked list
            new_node->next = node->next;
            node->next = new_node;
            
            return {split_key, new_node};
        } else {
            // Split internal node - move mid key up to parent
            K split_key = node->keys[mid];
            
            // Move keys and children to new node
            new_node->keys.assign(node->keys.begin() + mid + 1, node->keys.end());
            new_node->children.assign(node->children.begin() + mid + 1, node->children.end());
            
            node->keys.erase(node->keys.begin() + mid, node->keys.end());
            node->children.erase(node->children.begin() + mid + 1, node->children.end());
            
            // Update parent pointers
            for (auto& child : new_node->children) {
                child->parent = new_node;
            }
            
            return {split_key, new_node};
        }
    }

    // Insert into a non-full node
    void insert_non_full(NodePtr node, const K& key, const V& value) {
        if (node->is_leaf) {
            // Find insertion position
            auto it = std::lower_bound(node->keys.begin(), node->keys.end(), key);
            size_t pos = it - node->keys.begin();
            
            // Check if key already exists (update value)
            if (it != node->keys.end() && *it == key) {
                node->values[pos] = value;
                return;
            }
            
            // Insert key and value
            node->keys.insert(it, key);
            node->values.insert(node->values.begin() + pos, value);
            size_++;
        } else {
            // Find child to descend to
            size_t i = 0;
            while (i < node->keys.size() && key >= node->keys[i]) {
                i++;
            }
            
            NodePtr child = node->children[i];
            
            // If child is full, split it first
            if (child->is_full()) {
                auto [split_key, new_child] = split_node(child);
                
                // Insert split key into current node
                node->keys.insert(node->keys.begin() + i, split_key);
                node->children.insert(node->children.begin() + i + 1, new_child);
                new_child->parent = node;
                
                // Decide which child to descend to
                if (key >= split_key) {
                    i++;
                    child = new_child;
                }
            }
            
            insert_non_full(child, key, value);
        }
    }

public:
    BPlusTree() : root(nullptr), first_leaf(nullptr), size_(0) {}

    // Insert key-value pair
    void insert(const K& key, const V& value) {
        if (!root) {
            // Create root as leaf node
            root = std::make_shared<Node>(true);
            first_leaf = root;
        }
        
        if (root->is_full()) {
            // Split root
            auto [split_key, new_child] = split_node(root);
            
            // Create new root
            NodePtr new_root = std::make_shared<Node>(false);
            new_root->keys.push_back(split_key);
            new_root->children.push_back(root);
            new_root->children.push_back(new_child);
            
            root->parent = new_root;
            new_child->parent = new_root;
            
            root = new_root;
        }
        
        insert_non_full(root, key, value);
    }

    // Find value by key (throws std::out_of_range if not found)
    V& find(const K& key) {
        NodePtr leaf = find_leaf(key);
        if (!leaf) {
            throw std::out_of_range("Key not found in B+ tree");
        }
        
        auto it = std::lower_bound(leaf->keys.begin(), leaf->keys.end(), key);
        if (it != leaf->keys.end() && *it == key) {
            size_t pos = it - leaf->keys.begin();
            return leaf->values[pos];
        }
        throw std::out_of_range("Key not found in B+ tree");
    }

    // Find value by key (const version)
    const V& find(const K& key) const {
        NodePtr leaf = find_leaf(key);
        if (!leaf) {
            throw std::out_of_range("Key not found in B+ tree");
        }
        
        auto it = std::lower_bound(leaf->keys.begin(), leaf->keys.end(), key);
        if (it != leaf->keys.end() && *it == key) {
            size_t pos = it - leaf->keys.begin();
            return leaf->values[pos];
        }
        throw std::out_of_range("Key not found in B+ tree");
    }

    // Check if key exists
    bool contains(const K& key) const {
        NodePtr leaf = find_leaf(key);
        if (!leaf) return false;
        
        auto it = std::lower_bound(leaf->keys.begin(), leaf->keys.end(), key);
        return (it != leaf->keys.end() && *it == key);
    }

    // Operator[] for convenient access (creates entry if doesn't exist)
    V& operator[](const K& key) {
        try {
            return find(key);
        } catch (const std::out_of_range&) {
            insert(key, V());
            return find(key);
        }
    }

    // Remove key from tree
    bool remove(const K& key) {
        if (!root) return false;
        
        NodePtr leaf = find_leaf(key);
        if (!leaf) return false;
        
        auto it = std::lower_bound(leaf->keys.begin(), leaf->keys.end(), key);
        if (it == leaf->keys.end() || *it != key) {
            return false;  // Key not found
        }
        
        size_t pos = it - leaf->keys.begin();
        leaf->keys.erase(it);
        leaf->values.erase(leaf->values.begin() + pos);
        size_--;
        
        // Handle underflow
        if (leaf != root && leaf->is_underflow()) {
            handle_underflow(leaf);
        }
        
        // If root is empty after deletion
        if (root->keys.empty()) {
            if (root->is_leaf) {
                // Tree is now empty
                root = nullptr;
                first_leaf = nullptr;
            } else if (root->children.size() == 1) {
                // Make the only child the new root
                root = root->children[0];
                root->parent = nullptr;
            }
        }
        
        return true;
    }

private:
    // Get sibling node (prefer left sibling)
    std::pair<NodePtr, int64_t> get_sibling(NodePtr node) {
        NodePtr parent = node->parent;
        if (!parent) return {nullptr, 0};
        
        // Find node's position in parent
        size_t pos = 0;
        for (; pos < parent->children.size(); pos++) {
            if (parent->children[pos] == node) break;
        }
        
        // Try left sibling first
        if (pos > 0) {
            return {parent->children[pos - 1], pos - 1};
        }
        // Otherwise use right sibling
        if (pos + 1 < parent->children.size()) {
            return {parent->children[pos + 1], pos};
        }
        
        return {nullptr, 0};
    }
    
    // Merge node with sibling
    void merge_nodes(NodePtr left, NodePtr right, NodePtr parent, int64_t parent_key_idx) {
        if (left->is_leaf) {
            // Merge leaf nodes
            left->keys.insert(left->keys.end(), right->keys.begin(), right->keys.end());
            left->values.insert(left->values.end(), right->values.begin(), right->values.end());
            left->next = right->next;
            
            // Remove key and child from parent
            parent->keys.erase(parent->keys.begin() + parent_key_idx);
            parent->children.erase(parent->children.begin() + parent_key_idx + 1);
        } else {
            // Merge internal nodes
            // Pull down the parent key
            left->keys.push_back(parent->keys[parent_key_idx]);
            left->keys.insert(left->keys.end(), right->keys.begin(), right->keys.end());
            left->children.insert(left->children.end(), right->children.begin(), right->children.end());
            
            // Update parent pointers
            for (auto& child : right->children) {
                child->parent = left;
            }
            
            // Remove key and child from parent
            parent->keys.erase(parent->keys.begin() + parent_key_idx);
            parent->children.erase(parent->children.begin() + parent_key_idx + 1);
        }
        
        // Recursively handle parent underflow
        if (parent != root && parent->is_underflow()) {
            handle_underflow(parent);
        }
    }
    
    // Borrow from sibling
    void borrow_from_sibling(NodePtr node, NodePtr sibling, NodePtr parent, int64_t parent_key_idx, bool from_left) {
        if (node->is_leaf) {
            if (from_left) {
                // Borrow from left sibling (take rightmost)
                node->keys.insert(node->keys.begin(), sibling->keys.back());
                node->values.insert(node->values.begin(), sibling->values.back());
                sibling->keys.pop_back();
                sibling->values.pop_back();
                
                // Update parent key
                parent->keys[parent_key_idx] = node->keys[0];
            } else {
                // Borrow from right sibling (take leftmost)
                node->keys.push_back(sibling->keys[0]);
                node->values.push_back(sibling->values[0]);
                sibling->keys.erase(sibling->keys.begin());
                sibling->values.erase(sibling->values.begin());
                
                // Update parent key
                parent->keys[parent_key_idx] = sibling->keys[0];
            }
        } else {
            if (from_left) {
                // Borrow from left sibling (take rightmost)
                node->keys.insert(node->keys.begin(), parent->keys[parent_key_idx]);
                node->children.insert(node->children.begin(), sibling->children.back());
                sibling->children.back()->parent = node;
                
                parent->keys[parent_key_idx] = sibling->keys.back();
                
                sibling->keys.pop_back();
                sibling->children.pop_back();
            } else {
                // Borrow from right sibling (take leftmost)
                node->keys.push_back(parent->keys[parent_key_idx]);
                node->children.push_back(sibling->children[0]);
                sibling->children[0]->parent = node;
                
                parent->keys[parent_key_idx] = sibling->keys[0];
                
                sibling->keys.erase(sibling->keys.begin());
                sibling->children.erase(sibling->children.begin());
            }
        }
    }
    
    // Handle node underflow after deletion
    void handle_underflow(NodePtr node) {
        NodePtr parent = node->parent;
        if (!parent) return;  // Root node
        
        auto [sibling, sibling_pos] = get_sibling(node);
        if (!sibling) return;
        
        // Find node position in parent
        size_t node_pos = 0;
        for (; node_pos < parent->children.size(); node_pos++) {
            if (parent->children[node_pos] == node) break;
        }
        
        bool sibling_is_left = (sibling_pos < static_cast<int64_t>(node_pos));
        int64_t parent_key_idx = sibling_is_left ? node_pos - 1 : node_pos;
        
        // Try to borrow from sibling
        if (sibling->keys.size() > (ORDER / 2)) {
            borrow_from_sibling(node, sibling, parent, parent_key_idx, sibling_is_left);
        } else {
            // Merge with sibling
            if (sibling_is_left) {
                merge_nodes(sibling, node, parent, parent_key_idx);
            } else {
                merge_nodes(node, sibling, parent, parent_key_idx);
            }
        }
    }

public:
    // Range query: get all key-value pairs in [start_key, end_key]
    std::vector<std::pair<K, V>> range(const K& start_key, const K& end_key) const {
        std::vector<std::pair<K, V>> result;
        
        NodePtr leaf = find_leaf(start_key);
        if (!leaf) return result;
        
        // Find starting position
        auto it = std::lower_bound(leaf->keys.begin(), leaf->keys.end(), start_key);
        size_t pos = it - leaf->keys.begin();
        
        // Traverse leaf nodes
        while (leaf) {
            for (; pos < leaf->keys.size(); pos++) {
                if (leaf->keys[pos] > end_key) {
                    return result;
                }
                result.emplace_back(leaf->keys[pos], leaf->values[pos]);
            }
            leaf = leaf->next;
            pos = 0;
        }
        
        return result;
    }

    // Get all key-value pairs (in sorted order)
    std::vector<std::pair<K, V>> all() const {
        std::vector<std::pair<K, V>> result;
        
        NodePtr leaf = first_leaf;
        while (leaf) {
            for (size_t i = 0; i < leaf->keys.size(); i++) {
                result.emplace_back(leaf->keys[i], leaf->values[i]);
            }
            leaf = leaf->next;
        }
        
        return result;
    }

    // Get number of key-value pairs
    int64_t size() const {
        return size_;
    }

    // Check if tree is empty
    bool empty() const {
        return size_ == 0;
    }

    // Clear the tree
    void clear() {
        root = nullptr;
        first_leaf = nullptr;
        size_ = 0;
    }

    // Print tree structure (for debugging)
    void print() const {
        if (!root) {
            std::cout << "Empty tree" << std::endl;
            return;
        }
        print_node(root, 0);
    }

private:
    void print_node(NodePtr node, int64_t depth) const {
        std::string indent(depth * 2, ' ');
        
        if (node->is_leaf) {
            std::cout << indent << "Leaf: ";
            for (size_t i = 0; i < node->keys.size(); i++) {
                std::cout << "(" << node->keys[i] << ":" << node->values[i] << ") ";
            }
            std::cout << std::endl;
        } else {
            std::cout << indent << "Internal: ";
            for (const auto& key : node->keys) {
                std::cout << key << " ";
            }
            std::cout << std::endl;
            
            for (const auto& child : node->children) {
                print_node(child, depth + 1);
            }
        }
    }
};
