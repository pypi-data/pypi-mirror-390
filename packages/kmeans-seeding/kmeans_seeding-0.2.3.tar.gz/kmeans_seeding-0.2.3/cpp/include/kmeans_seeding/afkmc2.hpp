#pragma once

#include <vector>
#include <string>
#include <memory>
#include <random>

// Forward declare FAISS types to avoid header dependency in public interface
namespace faiss {
    struct Index;
}

namespace rs_kmeans {

/**
 * AFK-MC²: Assumption-Free K-MC² (Fast k-means++ seeding using MCMC)
 *
 * This implements the algorithm from "Fast and Provably Good Seedings for k-Means"
 * by Bachem, Lucic, Hassani, and Krause (NIPS 2016).
 *
 * Key features:
 * - Uses Markov chain Monte Carlo to approximate D²-sampling
 * - Smart proposal distribution: q(x) = 0.5 * d(x,c1)²/Σd(x',c1)² + 0.5/n
 * - No assumptions on data distribution required
 * - O(nd) preprocessing, O(mk²d) main loop complexity
 * - Provably good: E[cost] ≤ 8(log²k + 2)·OPT_k + ε·Var(X)
 */
class AFKMC2 {
public:
    AFKMC2();
    ~AFKMC2();

    /**
     * Preprocess the dataset: compute proposal distribution
     *
     * @param data: Flattened row-major data (n × d)
     * @param n: Number of data points
     * @param d: Dimensionality
     *
     * After preprocessing:
     * - First center c1 is sampled uniformly
     * - Proposal distribution q(x|c1) is computed
     * - Ready for multiple cluster() calls
     */
    void preprocess(const std::vector<float>& data, int n, int d);

    /**
     * Perform AFK-MC² seeding using MCMC
     *
     * @param k: Number of clusters
     * @param m: Markov chain length per center (default: 200)
     * @param index_type: FAISS index type for label assignment ("Flat", "HNSW", "LSH")
     * @param index_params: Optional FAISS index parameters
     * @param random_seed: Random seed for reproducibility (default: 42)
     *
     * @return Pair of (centers, labels)
     *         - centers: k × d flattened row-major array
     *         - labels: n-element array of cluster assignments
     */
    std::pair<std::vector<float>, std::vector<int>>
    cluster(int k, int m = 200,
            const std::string& index_type = "Flat",
            const std::string& index_params = "",
            unsigned int random_seed = 42);

    // Getters for inspection
    int get_n() const { return n_; }
    int get_d() const { return d_; }
    bool is_preprocessed() const { return preprocessed_; }

private:
    // Data storage
    std::vector<float> data_;           // n × d, row-major (original data)
    std::vector<float> proposal_dist_;  // n-element proposal distribution q(x|c1)
    int c1_idx_;                        // Index of first center

    int n_;  // Number of points
    int d_;  // Dimensionality
    bool preprocessed_;

    // FAISS index for final label assignment
    std::unique_ptr<faiss::Index> center_index_;
    std::vector<int> selected_center_indices_;  // Indices into data_

    // Random number generation
    std::mt19937 rng_;
    std::discrete_distribution<int> proposal_sampler_;  // For sampling from q(x|c1)

    // Helper functions

    /**
     * Sample first center uniformly and compute proposal distribution
     * q(x|c1) = 0.5 * d(x,c1)²/Σd(x',c1)² + 0.5/n
     */
    void compute_proposal_distribution();

    /**
     * Initialize FAISS index for label assignment
     */
    void initialize_index(const std::string& index_type, const std::string& params);

    /**
     * Add centers to FAISS index for final label assignment
     */
    void build_center_index();

    /**
     * Compute d(x, C)² = min_{c∈C} ‖x - c‖²
     * @param point_idx: Index of point x
     * @param center_indices: Indices of current centers C
     */
    float compute_d_squared(int point_idx, const std::vector<int>& center_indices);

    /**
     * Sample next center using MCMC (Algorithm 1, lines 6-11)
     *
     * @param m: Markov chain length
     * @param center_indices: Indices of previously selected centers
     * @return Index of selected center
     */
    int sample_next_center_mcmc(int m, const std::vector<int>& center_indices);

    /**
     * Metropolis-Hastings acceptance probability
     * Accept y with probability: dy·q(x) / (dx·q(y))
     */
    bool metropolis_accept(int x_idx, int y_idx, float dx_sq, float dy_sq);

    /**
     * Assign each point to nearest center and return labels
     */
    std::vector<int> assign_labels();

    /**
     * Get pointer to data for point i
     */
    const float* get_point(int i) const {
        return &data_[i * d_];
    }

    /**
     * Compute squared Euclidean distance between two points
     */
    float squared_distance(int i, int j) const;
};

} // namespace rs_kmeans
