#pragma once

#include <vector>
#include <string>
#include <memory>
#include <random>

// Forward declare FAISS types (only if FAISS is available)
#ifdef HAS_FAISS
namespace faiss {
    struct Index;
}
#endif

// Forward declare Google LSH types (always available)
namespace fast_k_means {
    class LSHDataStructure;
    class FastLSH;
}

namespace rs_kmeans {

/**
 * RS-k-means++: Rejection Sampling based k-means++ seeding
 *
 * This implements the algorithm from "A New Rejection Sampling Approach to k-means++"
 * by Shah, Agrawal, and Jaiswal (2025).
 *
 * Key features:
 * - Uses FAISS for approximate nearest neighbor queries over selected centers
 * - Implements rejection sampling for D² distribution
 * - O(nnz(X)) preprocessing, O(mk²d) clustering time
 */
class RSkMeans {
public:
    RSkMeans();
    ~RSkMeans();

    /**
     * Preprocess the dataset: center the data and compute norms
     *
     * @param data: Flattened row-major data (n × d)
     * @param n: Number of data points
     * @param d: Dimensionality
     *
     * After preprocessing:
     * - Data is centered (mean subtracted)
     * - Norms and squared norms are cached
     * - Ready for multiple cluster() calls
     */
    void preprocess(const std::vector<float>& data, int n, int d);

    /**
     * Perform RS-k-means++ seeding using rejection sampling
     *
     * @param k: Number of clusters
     * @param m: Maximum rejection sampling iterations per center (default: inf)
     * @param index_type: Index type ("Flat", "IVFFlat", "HNSW", "LSH", "GoogleLSH", "FastLSH")
     * @param index_params: Optional index parameters (e.g., "nprobe=10" for FAISS, "bucket_size=100,nb_bins=10" for GoogleLSH, "L=10,k=5,w=4.0" for FastLSH)
     * @param random_seed: Random seed for reproducibility (default: 42)
     *
     * @return Pair of (centers, labels)
     *         - centers: k × d flattened row-major array (in original coordinates, not centered)
     *         - labels: n-element array of cluster assignments
     */
    std::pair<std::vector<float>, std::vector<int>>
    cluster(int k, int m = -1,
            const std::string& index_type = "Flat",
            const std::string& index_params = "",
            unsigned int random_seed = 42);

    // Getters for inspection
    int get_n() const { return n_; }
    int get_d() const { return d_; }
    bool is_preprocessed() const { return preprocessed_; }

private:
    // Data storage
    std::vector<float> centered_data_;  // n × d, row-major
    std::vector<float> mean_;           // d-dimensional mean
    std::vector<float> norms_sq_;       // n squared norms (‖x‖²)
    float data_norm_sq_;                // ‖X‖² = sum of all squared norms

    int n_;  // Number of points
    int d_;  // Dimensionality
    bool preprocessed_;

    // Index for selected centers (incremental)
#ifdef HAS_FAISS
    std::unique_ptr<faiss::Index> center_index_;  // FAISS index (only if available)
#endif
    std::unique_ptr<fast_k_means::LSHDataStructure> google_lsh_index_;  // Google LSH index
    std::unique_ptr<fast_k_means::FastLSH> fast_lsh_index_;  // Fast LSH index (DHHash)
    std::vector<int> selected_center_indices_;  // Indices into centered_data_
    std::string current_index_type_;  // Track which index type is being used

    // Random number generation
    std::mt19937 rng_;
    std::discrete_distribution<int> norm_dist_;  // For sampling from D_X (norms)

    // Helper functions

    /**
     * Initialize FAISS index based on index_type string
     */
    void initialize_index(const std::string& index_type, const std::string& params);

    /**
     * Add a center to the FAISS index
     */
    void add_center_to_index(int point_idx);

    /**
     * Compute Δ(x, S) = min_{c∈S} ‖x - c‖² using FAISS
     * Returns exact value for first center, approximate for subsequent
     */
    float compute_delta(int point_idx);

    /**
     * Sample next center using rejection sampling (Algorithm D²-sample)
     *
     * @param m: Max rejection sampling iterations
     * @param c1_norm_sq: ‖c₁‖² (first center norm squared)
     * @return Index of selected center
     */
    int sample_next_center(int m, float c1_norm_sq);

    /**
     * Sample from proposal distribution D₂ in O(1) time (Lemma 4.11)
     * Uses efficient sampling from norm distribution
     */
    int sample_from_proposal(float c1_norm_sq);

    /**
     * Sample from D_X (distribution proportional to squared norms) in O(log n) time
     */
    int sample_from_norm_distribution();

    /**
     * Assign each point to nearest center and return labels
     */
    std::vector<int> assign_labels();

    /**
     * Get pointer to centered data for point i
     */
    const float* get_point(int i) const {
        return &centered_data_[i * d_];
    }

    /**
     * Compute squared Euclidean distance between two points
     */
    float squared_distance(int i, int j) const;
};

} // namespace rs_kmeans
