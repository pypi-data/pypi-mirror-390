#include "fast_lsh.h"
#include <algorithm>
#include <stdexcept>
#include <cstring>

namespace fast_k_means {

// ==================== HadamardTransform Implementation ====================

int HadamardTransform::next_power_of_2(int n) {
    // Optimized using bit operations
    if (n <= 1) return 1;
    --n;
    n |= n >> 1;
    n |= n >> 2;
    n |= n >> 4;
    n |= n >> 8;
    n |= n >> 16;
    return n + 1;
}

void HadamardTransform::fht(std::vector<double>& data) {
    int n = data.size();

    // Verify n is power of 2
    if ((n & (n - 1)) != 0) {
        throw std::runtime_error("FHT requires size to be power of 2");
    }

    // In-place fast Hadamard transform
    for (int h = 1; h < n; h *= 2) {
        for (int i = 0; i < n; i += h * 2) {
            for (int j = i; j < i + h; j++) {
                double x = data[j];
                double y = data[j + h];
                data[j] = x + y;
                data[j + h] = x - y;
            }
        }
    }

    // Normalize by 1/sqrt(n) - precomputed for efficiency
    static thread_local std::unordered_map<int, double> norm_cache;
    auto it = norm_cache.find(n);
    double norm;
    if (it != norm_cache.end()) {
        norm = it->second;
    } else {
        norm = 1.0 / std::sqrt(static_cast<double>(n));
        norm_cache[n] = norm;
    }

    for (int i = 0; i < n; i++) {
        data[i] *= norm;
    }
}

void HadamardTransform::ifht(std::vector<double>& data) {
    // For normalized Hadamard, inverse is same as forward
    fht(data);
}

// ==================== FastLSH Implementation ====================

FastLSH::FastLSH(int L, int k, int d, double w)
    : L_(L), k_(k), d_(d), w_(w), num_points_(0), rng_(42) {

    // Pad dimension to power of 2 for Hadamard transform
    d_padded_ = HadamardTransform::next_power_of_2(d);

    // Initialize hash tables
    hash_tables_.resize(L);
    for (int i = 0; i < L; i++) {
        initialize_hash_table(i);
    }
}

void FastLSH::initialize_hash_table(int table_idx) {
    auto& table = hash_tables_[table_idx];

    // D: diagonal ±1 (random sign flips)
    table.D.resize(d_padded_);
    std::uniform_int_distribution<int> sign_dist(0, 1);
    for (int i = 0; i < d_padded_; i++) {
        table.D[i] = sign_dist(rng_) ? 1 : -1;
    }

    // M: random permutation
    table.M.resize(d_padded_);
    for (int i = 0; i < d_padded_; i++) {
        table.M[i] = i;
    }
    std::shuffle(table.M.begin(), table.M.end(), rng_);

    // G: Gaussian N(0,1)
    table.G.resize(d_padded_);
    std::normal_distribution<double> normal_dist(0.0, 1.0);
    for (int i = 0; i < d_padded_; i++) {
        table.G[i] = normal_dist(rng_);
    }

    // b: offset in [0, w]
    table.b.resize(d_padded_);
    std::uniform_real_distribution<double> offset_dist(0.0, w_);
    for (int i = 0; i < d_padded_; i++) {
        table.b[i] = offset_dist(rng_);
    }
}

std::vector<double> FastLSH::apply_transform(const std::vector<double>& point, int table_idx) {
    auto& table = hash_tables_[table_idx];

    // Use thread-local buffer to avoid repeated allocations
    static thread_local std::vector<double> x;
    static thread_local std::vector<double> x_perm;

    x.assign(d_padded_, 0.0);
    x_perm.resize(d_padded_);

    // Pad point to d_padded with zeros
    std::copy(point.begin(), point.begin() + d_, x.begin());

    // Step 1: D (diagonal sign flips) - combined with padding for efficiency
    for (int i = 0; i < d_; i++) {
        x[i] *= table.D[i];
    }
    // Apply D to padded zeros (no-op if D[i] is just sign)
    for (int i = d_; i < d_padded_; i++) {
        x[i] = 0.0;  // Already 0, but explicitly show the multiplication
    }

    // Step 2: H (first Hadamard transform)
    HadamardTransform::fht(x);

    // Step 3: M (permutation) - avoid temporary allocation
    for (int i = 0; i < d_padded_; i++) {
        x_perm[i] = x[table.M[i]];
    }
    std::swap(x, x_perm);

    // Step 4: G (Gaussian scaling)
    for (int i = 0; i < d_padded_; i++) {
        x[i] *= table.G[i];
    }

    // Step 5: H (second Hadamard transform)
    HadamardTransform::fht(x);

    // Step 6: Add offset b
    for (int i = 0; i < d_padded_; i++) {
        x[i] += table.b[i];
    }

    return x;
}

std::vector<std::vector<int>> FastLSH::compute_dhhash(const std::vector<double>& point) {
    std::vector<std::vector<int>> hashes(L_);

    for (int table_idx = 0; table_idx < L_; table_idx++) {
        // Apply transformation pipeline: D → H → M → G → H → +b
        std::vector<double> transformed = apply_transform(point, table_idx);

        // Compute hash values: ⌊transformed / w⌋
        // Reserve space upfront for efficiency
        hashes[table_idx].reserve(k_);

        // FIXED: Use proper sampling strategy based on k and d_padded relationship
        if (k_ <= d_padded_) {
            // Systematic sampling: evenly space indices across d_padded
            // Use floating-point step to handle non-divisible cases
            double step = static_cast<double>(d_padded_) / static_cast<double>(k_);
            for (int i = 0; i < k_; i++) {
                int idx = static_cast<int>(i * step);
                // Ensure idx is within bounds
                idx = std::min(idx, d_padded_ - 1);
                hashes[table_idx].push_back(static_cast<int>(std::floor(transformed[idx] / w_)));
            }
        } else {
            // k > d_padded: Use all dimensions, then wrap around with different offsets
            // This provides k distinct hash values even when k > d_padded
            for (int i = 0; i < k_; i++) {
                int idx = i % d_padded_;
                // Add small offset based on which "round" we're in to ensure diversity
                int round = i / d_padded_;
                double offset = round * 0.1 * w_;  // Small offset to differentiate wrapped indices
                hashes[table_idx].push_back(static_cast<int>(std::floor((transformed[idx] + offset) / w_)));
            }
        }
    }

    return hashes;
}

void FastLSH::InsertPoint(int point_id, const std::vector<double>& point) {
    if (point.size() != static_cast<size_t>(d_)) {
        throw std::runtime_error("Point dimension mismatch");
    }

    // Compute DHHash for this point
    auto hashes = compute_dhhash(point);

    // Insert into each hash table
    for (int table_idx = 0; table_idx < L_; table_idx++) {
        auto& table = hash_tables_[table_idx];
        const auto& hash_key = hashes[table_idx];

        // Add to bucket (or create if doesn't exist)
        table.buckets[hash_key].push_back(point_id);
    }

    num_points_++;
}

std::vector<int> FastLSH::QueryPoint(const std::vector<double>& point, int max_candidates) {
    if (point.size() != static_cast<size_t>(d_)) {
        throw std::runtime_error("Point dimension mismatch");
    }

    // Compute DHHash for query point
    auto hashes = compute_dhhash(point);

    // Collect candidates from all hash tables - use thread-local to avoid allocations
    static thread_local std::unordered_map<int, int> candidate_counts;
    candidate_counts.clear();

    for (int table_idx = 0; table_idx < L_; table_idx++) {
        auto& table = hash_tables_[table_idx];
        const auto& hash_key = hashes[table_idx];

        // Find bucket
        auto it = table.buckets.find(hash_key);
        if (it != table.buckets.end()) {
            // Add all points in this bucket as candidates
            for (int point_id : it->second) {
                candidate_counts[point_id]++;
            }
        }
    }

    // Early return if no candidates
    if (candidate_counts.empty()) {
        return std::vector<int>();
    }

    // Use partial_sort for efficiency when max_candidates < total_candidates
    static thread_local std::vector<std::pair<int, int>> candidates;
    candidates.clear();
    candidates.reserve(candidate_counts.size());

    for (const auto& pair : candidate_counts) {
        candidates.emplace_back(pair.second, pair.first);  // {count, point_id}
    }

    // Optimize: use partial_sort_copy if we only need top-k
    int limit = std::min(max_candidates, static_cast<int>(candidates.size()));

    if (limit < static_cast<int>(candidates.size()) / 2) {
        // Use nth_element + partial_sort for efficiency
        std::nth_element(candidates.begin(), candidates.begin() + limit, candidates.end(),
                        std::greater<std::pair<int, int>>());
        std::sort(candidates.begin(), candidates.begin() + limit,
                 std::greater<std::pair<int, int>>());
    } else {
        // Full sort
        std::sort(candidates.begin(), candidates.end(), std::greater<std::pair<int, int>>());
    }

    // Extract point IDs
    std::vector<int> result;
    result.reserve(limit);
    for (int i = 0; i < limit; i++) {
        result.push_back(candidates[i].second);
    }

    return result;
}

} // namespace fast_k_means
