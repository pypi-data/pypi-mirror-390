// Fast LSH using DHHash (Double Hadamard Hash) from "Fast Locality-Sensitive Hashing"
// Algorithm: ζ = ⌊(H·G·M·H·D·x + b) / w⌋
// Complexity: O(d log d + kL) instead of O(dkL)

#ifndef FAST_LSH_H
#define FAST_LSH_H

#include <vector>
#include <random>
#include <cmath>
#include <memory>
#include <unordered_map>

namespace fast_k_means {

// Fast Walsh-Hadamard Transform implementation
class HadamardTransform {
public:
    // In-place fast Hadamard transform in O(d log d)
    static void fht(std::vector<double>& data);

    // Inverse transform (same as forward for normalized Hadamard)
    static void ifht(std::vector<double>& data);

    // Get next power of 2
    static int next_power_of_2(int n);
};

// DHHash-based Fast LSH Data Structure
class FastLSH {
public:
    // Constructor
    // L: number of hash tables
    // k: number of hash functions per table
    // d: dimensionality
    // w: bucket width
    FastLSH(int L, int k, int d, double w = 4.0);

    // Insert a point into the data structure
    void InsertPoint(int point_id, const std::vector<double>& point);

    // Query for approximate nearest neighbors
    // Returns point IDs in candidate buckets
    std::vector<int> QueryPoint(const std::vector<double>& point, int max_candidates = 100);

    // Get number of points stored
    int Size() const { return num_points_; }

private:
    // Compute DHHash for a point
    // Returns hash values (k values per table, L tables total)
    std::vector<std::vector<int>> compute_dhhash(const std::vector<double>& point);

    // Apply transformation pipeline: D → H → M → G → H
    std::vector<double> apply_transform(const std::vector<double>& point, int table_idx);

    // Parameters
    int L_;  // Number of hash tables
    int k_;  // Number of hash functions per table
    int d_;  // Original dimensionality
    int d_padded_;  // Padded to power of 2 for Hadamard
    double w_;  // Bucket width

    // Hash function for vector<int> keys
    struct VectorHash {
        size_t operator()(const std::vector<int>& v) const {
            size_t hash = 0;
            for (int i : v) {
                hash ^= std::hash<int>()(i) + 0x9e3779b9 + (hash << 6) + (hash >> 2);
            }
            return hash;
        }
    };

    // Random components for each hash table
    struct HashTable {
        std::vector<int> D;  // Diagonal ±1 (size d_padded)
        std::vector<int> M;  // Permutation (size d_padded)
        std::vector<double> G;  // Gaussian N(0,1) (size d_padded)
        std::vector<double> b;  // Offset (size d_padded)
        std::unordered_map<std::vector<int>, std::vector<int>, VectorHash> buckets;  // Hash buckets
    };

    std::vector<HashTable> hash_tables_;

    // Bookkeeping
    int num_points_;
    std::mt19937 rng_;

    // Initialize hash table parameters
    void initialize_hash_table(int table_idx);
};

} // namespace fast_k_means

#endif // FAST_LSH_H
