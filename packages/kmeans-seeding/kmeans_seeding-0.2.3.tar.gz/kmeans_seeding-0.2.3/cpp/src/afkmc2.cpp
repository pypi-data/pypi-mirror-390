
#include "afkmc2.hpp"
#include <faiss/IndexFlat.h>
#include <faiss/index_factory.h>
#include <faiss/IndexIVFFlat.h>
#include <faiss/IndexHNSW.h>
#include <faiss/IndexLSH.h>
#include <numeric>
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <limits>
#include <iostream>

namespace rs_kmeans {

AFKMC2::AFKMC2()
    : n_(0), d_(0), preprocessed_(false), c1_idx_(-1) {}

AFKMC2::~AFKMC2() = default;

void AFKMC2::preprocess(const std::vector<float>& data, int n, int d) {
    if (data.size() != static_cast<size_t>(n * d)) {
        throw std::invalid_argument("Data size mismatch");
    }

    n_ = n;
    d_ = d;
    data_ = data;

    // Compute proposal distribution
    compute_proposal_distribution();

    preprocessed_ = true;

    std::cout << "AFK-MC² Preprocessed: n=" << n_ << ", d=" << d_
              << ", c1_idx=" << c1_idx_ << std::endl;
}

void AFKMC2::compute_proposal_distribution() {
    // Algorithm 1, Line 1: c1 ← Point uniformly sampled from X
    std::random_device rd;
    std::mt19937 temp_rng(rd());
    std::uniform_int_distribution<int> uniform_dist(0, n_ - 1);
    c1_idx_ = uniform_dist(temp_rng);

    // Algorithm 1, Lines 2-3: Compute q(x) for all x ∈ X
    // q(x) = 1/2 · d(x, c1)²/Σ_{x'∈X} d(x', c1)² + 1/(2n)

    std::vector<float> d_squared(n_);
    double total_d_squared = 0.0;

    // Compute d(x, c1)² for all x
    for (int i = 0; i < n_; ++i) {
        float dist_sq = squared_distance(i, c1_idx_);
        d_squared[i] = dist_sq;
        total_d_squared += dist_sq;
    }

    // Compute proposal distribution q(x)
    proposal_dist_.resize(n_);
    for (int i = 0; i < n_; ++i) {
        float term_A = 0.5f * (d_squared[i] / total_d_squared);
        float term_B = 0.5f / n_;
        proposal_dist_[i] = term_A + term_B;
    }

    // Initialize proposal sampler
    proposal_sampler_ = std::discrete_distribution<int>(
        proposal_dist_.begin(), proposal_dist_.end()
    );
}

float AFKMC2::compute_d_squared(int point_idx, const std::vector<int>& center_indices) {
    // Compute d(x, C)² = min_{c∈C} ||x - c||²
    // Pure brute force, no FAISS

    if (center_indices.empty()) {
        return std::numeric_limits<float>::max();
    }

    float min_dist_sq = std::numeric_limits<float>::max();

    for (int center_idx : center_indices) {
        float dist_sq = squared_distance(point_idx, center_idx);
        min_dist_sq = std::min(min_dist_sq, dist_sq);
    }

    return min_dist_sq;
}

int AFKMC2::sample_next_center_mcmc(int m, const std::vector<int>& center_indices) {
    // Algorithm 1, Lines 6-11: MCMC sampling (no FAISS)

    // Line 6: x ← Point sampled from X using q(x)
    int x = proposal_sampler_(rng_);

    // Line 7: dx ← d(x, C_{i-1})²
    float dx = compute_d_squared(x, center_indices);

    // Lines 8-11: for j = 2, 3, ..., m do
    std::uniform_real_distribution<float> uniform(0.0f, 1.0f);

    for (int j = 2; j <= m; ++j) {
        // Line 9: y ← Point sampled from X using q(y)
        int y = proposal_sampler_(rng_);

        // Line 10: dy ← d(y, C_{i-1})²
        float dy = compute_d_squared(y, center_indices);

        // Line 11: if dy·q(x) / (dx·q(y)) > Unif(0,1) then x ← y, dx ← dy
        float q_x = proposal_dist_[x];
        float q_y = proposal_dist_[y];

        // Avoid division by zero
        if (dx > 0.0f && q_y > 0.0f) {
            float acceptance_ratio = (dy * q_x) / (dx * q_y);
            if (acceptance_ratio > uniform(rng_)) {
                x = y;
                dx = dy;
            }
        } else {
            // If dx = 0, always accept
            x = y;
            dx = dy;
        }
    }

    return x;
}

void AFKMC2::initialize_index(const std::string& index_type, const std::string& params) {
    // Initialize FAISS index for label assignment (same as RS-k-means++)
    if (index_type == "Flat") {
        center_index_.reset(new faiss::IndexFlatL2(d_));
    }
    else if (index_type == "LSH") {
        int nbits = 8 * d_;
        center_index_.reset(new faiss::IndexLSH(d_, nbits));
    }
    else if (index_type == "IVFFlat") {
        int nlist = std::max(1, static_cast<int>(std::sqrt(selected_center_indices_.size())));
        auto quantizer = new faiss::IndexFlatL2(d_);
        auto ivf = new faiss::IndexIVFFlat(quantizer, d_, nlist);
        ivf->nprobe = 10;
        center_index_.reset(ivf);
    }
    else if (index_type == "HNSW") {
        int M = 32;
        center_index_.reset(new faiss::IndexHNSWFlat(d_, M));
    }
    else {
        try {
            center_index_.reset(faiss::index_factory(d_, index_type.c_str()));
        } catch (const std::exception& e) {
            throw std::invalid_argument("Invalid index_type: " + index_type);
        }
    }
}

void AFKMC2::build_center_index() {
    // Build FAISS index for label assignment (same as RS-k-means++)
    std::vector<float> centers_data;
    centers_data.reserve(selected_center_indices_.size() * d_);

    for (int idx : selected_center_indices_) {
        const float* point = get_point(idx);
        centers_data.insert(centers_data.end(), point, point + d_);
    }

    // Train if needed
    if (auto* ivf = dynamic_cast<faiss::IndexIVFFlat*>(center_index_.get())) {
        if (!ivf->is_trained && selected_center_indices_.size() >= static_cast<size_t>(ivf->nlist)) {
            ivf->train(selected_center_indices_.size(), centers_data.data());
        }
    }

    center_index_->add(selected_center_indices_.size(), centers_data.data());
}

std::vector<int> AFKMC2::assign_labels() {
    // Assign labels using FAISS (same as RS-k-means++)
    std::vector<int> labels(n_);

    #pragma omp parallel for
    for (int i = 0; i < n_; ++i) {
        const float* query = get_point(i);
        float dist_sq;
        faiss::idx_t nearest_idx;

        center_index_->search(1, query, 1, &dist_sq, &nearest_idx);
        labels[i] = static_cast<int>(nearest_idx);
    }

    return labels;
}

float AFKMC2::squared_distance(int i, int j) const {
    const float* pi = get_point(i);
    const float* pj = get_point(j);

    float dist_sq = 0.0f;
    for (int k = 0; k < d_; ++k) {
        float diff = pi[k] - pj[k];
        dist_sq += diff * diff;
    }
    return dist_sq;
}

std::pair<std::vector<float>, std::vector<int>>
AFKMC2::cluster(int k, int m, const std::string& index_type,
                const std::string& index_params, unsigned int random_seed) {
    if (!preprocessed_) {
        throw std::runtime_error("Must call preprocess() before cluster()");
    }

    if (k <= 0 || k > n_) {
        throw std::invalid_argument("k must be in range [1, n]");
    }

    if (m <= 0) {
        throw std::invalid_argument("m must be positive");
    }

    // Initialize RNG
    rng_.seed(random_seed);

    // Clear previous clustering
    selected_center_indices_.clear();

    // ========== AFK-MC² SEEDING (NO FAISS) ==========

    // Algorithm 1, Line 4: C1 ← {c1}
    selected_center_indices_.push_back(c1_idx_);
    std::cout << "Selected first center: idx=" << c1_idx_ << std::endl;

    // Algorithm 1, Line 5: for i = 2, 3, ..., k do
    for (int i = 2; i <= k; ++i) {
        // Lines 6-11: Sample next center using MCMC (pure brute force, no FAISS)
        int next_center = sample_next_center_mcmc(m, selected_center_indices_);

        // Line 12: C_i ← C_{i-1} ∪ {x}
        selected_center_indices_.push_back(next_center);

        if (i % 10 == 0 || i == k) {
            std::cout << "Selected " << i << "/" << k << " centers" << std::endl;
        }
    }

    // ========== LABEL ASSIGNMENT (WITH FAISS, like RS-k-means++) ==========

    // Extract center coordinates
    std::vector<float> centers(k * d_);
    for (int i = 0; i < k; ++i) {
        int idx = selected_center_indices_[i];
        const float* point = get_point(idx);
        std::copy(point, point + d_, &centers[i * d_]);
    }

    // Assign labels using FAISS (same approach as RS-k-means++)
    initialize_index(index_type, index_params);
    build_center_index();
    std::vector<int> labels = assign_labels();

    return {centers, labels};
}

} // namespace rs_kmeans
