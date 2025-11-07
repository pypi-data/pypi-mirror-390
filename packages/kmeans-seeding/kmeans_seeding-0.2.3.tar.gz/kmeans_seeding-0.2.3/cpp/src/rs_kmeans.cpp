#include "rs_kmeans.hpp"

// FAISS is optional - only include if available
#ifdef HAS_FAISS
#include <faiss/IndexFlat.h>
#include <faiss/index_factory.h>
#include <faiss/IndexIVFFlat.h>
#include <faiss/IndexHNSW.h>
#include <faiss/IndexLSH.h>
#endif

#include "lsh.h"
#include "fast_lsh.h"
#include <numeric>
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <limits>
#include <iostream>
#include <sstream>
#include <unordered_set>

namespace rs_kmeans {

RSkMeans::RSkMeans()
    : n_(0), d_(0), preprocessed_(false), data_norm_sq_(0.0f) {}

RSkMeans::~RSkMeans() = default;

void RSkMeans::preprocess(const std::vector<float>& data, int n, int d) {
    if (data.size() != static_cast<size_t>(n * d)) {
        throw std::invalid_argument("Data size mismatch");
    }

    n_ = n;
    d_ = d;

    // Compute mean
    mean_.resize(d, 0.0f);
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < d; ++j) {
            mean_[j] += data[i * d + j];
        }
    }
    for (int j = 0; j < d; ++j) {
        mean_[j] /= n;
    }

    // Center data and compute norms
    centered_data_.resize(n * d);
    norms_sq_.resize(n);
    data_norm_sq_ = 0.0f;

    for (int i = 0; i < n; ++i) {
        float norm_sq = 0.0f;
        for (int j = 0; j < d; ++j) {
            float centered_val = data[i * d + j] - mean_[j];
            centered_data_[i * d + j] = centered_val;
            norm_sq += centered_val * centered_val;
        }
        norms_sq_[i] = norm_sq;
        data_norm_sq_ += norm_sq;
    }

    // Initialize norm distribution for efficient D_X sampling (Lemma 4.9)
    norm_dist_ = std::discrete_distribution<int>(norms_sq_.begin(), norms_sq_.end());

    preprocessed_ = true;

    std::cout << "Preprocessed: n=" << n_ << ", d=" << d_
              << ", ||X||²=" << data_norm_sq_ << std::endl;
}

void RSkMeans::initialize_index(const std::string& index_type, const std::string& params) {
    current_index_type_ = index_type;

    // FastLSH: Use DHHash-based Fast LSH implementation
    if (index_type == "FastLSH") {
        // Parse parameters: L=10,k=5,w=4.0
        int L = 10;        // default: number of hash tables
        int k = 5;         // default: hash functions per table
        double w = 4.0;    // default: bucket width

        if (!params.empty()) {
            std::istringstream iss(params);
            std::string token;
            while (std::getline(iss, token, ',')) {
                size_t eq_pos = token.find('=');
                if (eq_pos != std::string::npos) {
                    std::string key = token.substr(0, eq_pos);
                    std::string value = token.substr(eq_pos + 1);
                    if (key == "L") {
                        L = std::stoi(value);
                    } else if (key == "k") {
                        k = std::stoi(value);
                    } else if (key == "w") {
                        w = std::stod(value);
                    }
                }
            }
        }

        fast_lsh_index_.reset(new fast_k_means::FastLSH(L, k, d_, w));
        std::cout << "FastLSH initialized: L=" << L
                  << ", k=" << k << ", w=" << w << std::endl;
        return;
    }

    // GoogleLSH: Use Google's LSH implementation
    if (index_type == "GoogleLSH") {
        // Parse parameters: bucket_size=100,nb_bins=10
        int bucket_size = 100;  // default
        int nb_bins = 10;       // default

        if (!params.empty()) {
            std::istringstream iss(params);
            std::string token;
            while (std::getline(iss, token, ',')) {
                size_t eq_pos = token.find('=');
                if (eq_pos != std::string::npos) {
                    std::string key = token.substr(0, eq_pos);
                    std::string value = token.substr(eq_pos + 1);
                    if (key == "bucket_size") {
                        bucket_size = std::stoi(value);
                    } else if (key == "nb_bins") {
                        nb_bins = std::stoi(value);
                    }
                }
            }
        }

        google_lsh_index_.reset(new fast_k_means::LSHDataStructure(bucket_size, nb_bins, d_));
        std::cout << "GoogleLSH initialized: bucket_size=" << bucket_size
                  << ", nb_bins=" << nb_bins << std::endl;
        return;
    }

#ifdef HAS_FAISS
    // FAISS indices
    if (index_type == "Flat") {
        center_index_.reset(new faiss::IndexFlatL2(d_));
    }
    else if (index_type == "LSH") {
        // LSH with default nbits = 8*d
        int nbits = 8 * d_;
        center_index_.reset(new faiss::IndexLSH(d_, nbits));
    }
    else if (index_type == "IVFFlat") {
        // IVF needs training, we'll use a simple approach
        // nlist = sqrt(k) is a common heuristic
        int nlist = std::max(1, static_cast<int>(std::sqrt(selected_center_indices_.size())));
        auto quantizer = new faiss::IndexFlatL2(d_);
        auto ivf = new faiss::IndexIVFFlat(quantizer, d_, nlist);
        ivf->nprobe = 10; // default nprobe
        center_index_.reset(ivf);
    }
    else if (index_type == "HNSW") {
        int M = 32; // default connectivity
        center_index_.reset(new faiss::IndexHNSWFlat(d_, M));
    }
    else {
        // Use index_factory for custom index strings
        try {
            center_index_.reset(faiss::index_factory(d_, index_type.c_str()));
        } catch (const std::exception& e) {
            throw std::invalid_argument("Invalid index_type: " + index_type);
        }
    }
#else
    // FAISS not available - throw informative error
    throw std::runtime_error(
        "FAISS index type '" + index_type + "' requested but FAISS library is not available.\n"
        "RS-k-means++ requires FAISS for rejection sampling with approximate nearest neighbors.\n\n"
        "To use RS-k-means++ with FAISS indices (Flat, LSH, IVFFlat, HNSW):\n"
        "  1. Install FAISS: conda install -c pytorch faiss-cpu\n"
        "  2. Rebuild the package: pip install --force-reinstall --no-cache-dir kmeans-seeding\n\n"
        "Alternatively, you can use:\n"
        "  - FastLSH index (index_type='FastLSH') - works without FAISS\n"
        "  - GoogleLSH index (index_type='GoogleLSH') - works without FAISS\n"
        "  - Other algorithms: kmeanspp(), afkmc2(), multitree_lsh() - do not require FAISS"
    );
#endif
}

void RSkMeans::add_center_to_index(int point_idx) {
    const float* point = get_point(point_idx);

    // FastLSH
    if (current_index_type_ == "FastLSH") {
        // Convert float* to vector<double>
        std::vector<double> point_double(d_);
        for (int i = 0; i < d_; ++i) {
            point_double[i] = static_cast<double>(point[i]);
        }
        fast_lsh_index_->InsertPoint(selected_center_indices_.size() - 1, point_double);
        return;
    }

    // GoogleLSH
    if (current_index_type_ == "GoogleLSH") {
        // Convert float* to vector<double>
        std::vector<double> point_double(d_);
        for (int i = 0; i < d_; ++i) {
            point_double[i] = static_cast<double>(point[i]);
        }
        google_lsh_index_->InsertPoint(selected_center_indices_.size() - 1, point_double);
        return;
    }

#ifdef HAS_FAISS
    // FAISS indices
    // For IVF indices, we need to train before adding
    if (auto* ivf = dynamic_cast<faiss::IndexIVFFlat*>(center_index_.get())) {
        if (!ivf->is_trained && selected_center_indices_.size() >= static_cast<size_t>(ivf->nlist)) {
            // Train on current centers
            std::vector<float> training_data;
            for (int idx : selected_center_indices_) {
                const float* p = get_point(idx);
                training_data.insert(training_data.end(), p, p + d_);
            }
            ivf->train(selected_center_indices_.size(), training_data.data());
        }
    }

    center_index_->add(1, point);
#endif
}

float RSkMeans::compute_delta(int point_idx) {
    if (selected_center_indices_.empty()) {
        return std::numeric_limits<float>::max();
    }

    if (selected_center_indices_.size() == 1) {
        // Exact distance to first center
        return squared_distance(point_idx, selected_center_indices_[0]);
    }

    const float* query = get_point(point_idx);

    // FastLSH
    if (current_index_type_ == "FastLSH") {
        // Convert query to vector<double>
        std::vector<double> query_double(d_);
        for (int i = 0; i < d_; ++i) {
            query_double[i] = static_cast<double>(query[i]);
        }

        // QueryPoint returns candidate point IDs
        int max_candidates = 50;  // Budget for LSH query
        std::vector<int> candidates = fast_lsh_index_->QueryPoint(query_double, max_candidates);

        // Compute exact distance to all candidates
        float min_dist_sq = std::numeric_limits<float>::max();
        for (int candidate_id : candidates) {
            int center_idx = selected_center_indices_[candidate_id];
            float dist_sq = squared_distance(point_idx, center_idx);
            min_dist_sq = std::min(min_dist_sq, dist_sq);
        }

        // If no candidates found, fall back to brute force
        if (candidates.empty()) {
            for (int center_idx : selected_center_indices_) {
                float dist_sq = squared_distance(point_idx, center_idx);
                min_dist_sq = std::min(min_dist_sq, dist_sq);
            }
        }

        return min_dist_sq;
    }

    // GoogleLSH
    if (current_index_type_ == "GoogleLSH") {
        // Convert query to vector<double>
        std::vector<double> query_double(d_);
        for (int i = 0; i < d_; ++i) {
            query_double[i] = static_cast<double>(query[i]);
        }

        // QueryPoint returns the squared distance directly
        int running_time = 100;  // Budget for LSH query
        double dist_sq = google_lsh_index_->QueryPoint(query_double, running_time);
        return static_cast<float>(dist_sq);
    }

#ifdef HAS_FAISS
    // FAISS for approximate nearest neighbor
    float dist_sq;
    faiss::idx_t nearest_idx;

    center_index_->search(1, query, 1, &dist_sq, &nearest_idx);

    return dist_sq;
#else
    // Should not reach here if initialize_index() properly validates
    throw std::runtime_error("FAISS not available");
#endif
}

int RSkMeans::sample_from_proposal(float c1_norm_sq) {
    // Efficient O(1) sampling from D₂ using Lemma 4.11
    // D₂(x) = (‖x‖² + ‖c₁‖²) / (‖X‖² + n·‖c₁‖²)
    //
    // Sample from D_X with prob ‖X‖²/(‖X‖² + n·‖c₁‖²)
    // Otherwise sample uniformly

    std::uniform_real_distribution<float> uniform(0.0f, 1.0f);
    float threshold = data_norm_sq_ / (data_norm_sq_ + n_ * c1_norm_sq);

    if (uniform(rng_) <= threshold) {
        // Sample from D_X (distribution proportional to norms)
        return sample_from_norm_distribution();
    } else {
        // Sample uniformly
        std::uniform_int_distribution<int> uniform_dist(0, n_ - 1);
        return uniform_dist(rng_);
    }
}

int RSkMeans::sample_from_norm_distribution() {
    // Sample from D_X in O(log n) time using preprocessed discrete_distribution
    return norm_dist_(rng_);
}

int RSkMeans::sample_next_center(int m, float c1_norm_sq) {
    std::uniform_real_distribution<float> uniform(0.0f, 1.0f);

    // Create a set for fast lookup of already-selected centers
    std::unordered_set<int> selected_set(selected_center_indices_.begin(),
                                          selected_center_indices_.end());

    int iterations = 0;
    int max_iter = (m < 0) ? std::numeric_limits<int>::max() : m;

    while (iterations < max_iter) {
        iterations++;

        // Sample x from proposal distribution (O(log n) time)
        int x = sample_from_proposal(c1_norm_sq);

        // Skip if x is already a selected center
        if (selected_set.find(x) != selected_set.end()) {
            continue;
        }

        // Compute acceptance probability
        float delta_x = compute_delta(x);
        float x_norm_sq = norms_sq_[x];

        // ρ(x) = (1/2) · Δ(x,S) / (‖x‖² + ‖c₁‖²)
        float rho = 0.5f * delta_x / (x_norm_sq + c1_norm_sq);

        // Accept/reject
        float r = uniform(rng_);
        if (r <= rho) {
            return x;
        }
    }

    // If rejection sampling fails after m iterations, sample uniformly
    // Make sure we don't select an already-chosen center
    std::uniform_int_distribution<int> uniform_dist(0, n_ - 1);
    int x;
    do {
        x = uniform_dist(rng_);
    } while (selected_set.find(x) != selected_set.end());
    return x;
}

std::vector<int> RSkMeans::assign_labels() {
    std::vector<int> labels(n_);

#ifdef HAS_FAISS
    // If using FastLSH or GoogleLSH, create a temporary FAISS index for label assignment
    std::unique_ptr<faiss::Index> label_index;
    if (current_index_type_ == "FastLSH" || current_index_type_ == "GoogleLSH") {
        label_index.reset(new faiss::IndexFlatL2(d_));

        // Add all selected centers to the FAISS index
        std::vector<float> centers_data;
        centers_data.reserve(selected_center_indices_.size() * d_);
        for (int idx : selected_center_indices_) {
            const float* p = get_point(idx);
            centers_data.insert(centers_data.end(), p, p + d_);
        }
        label_index->add(selected_center_indices_.size(), centers_data.data());
    } else {
        // Use the existing FAISS index
        label_index = std::move(center_index_);
    }

    #pragma omp parallel for
    for (int i = 0; i < n_; ++i) {
        const float* query = get_point(i);
        float dist_sq;
        faiss::idx_t nearest_idx;

        label_index->search(1, query, 1, &dist_sq, &nearest_idx);
        labels[i] = static_cast<int>(nearest_idx);
    }

    // Restore the index if we moved it
    if (current_index_type_ != "FastLSH" && current_index_type_ != "GoogleLSH") {
        center_index_ = std::move(label_index);
    }
#else
    // Brute-force label assignment when FAISS is not available
    #pragma omp parallel for
    for (int i = 0; i < n_; ++i) {
        const float* query = get_point(i);
        float min_dist_sq = std::numeric_limits<float>::max();
        int best_label = 0;

        for (size_t j = 0; j < selected_center_indices_.size(); ++j) {
            int center_idx = selected_center_indices_[j];
            const float* center = get_point(center_idx);

            float dist_sq = 0.0f;
            for (int k = 0; k < d_; ++k) {
                float diff = query[k] - center[k];
                dist_sq += diff * diff;
            }

            if (dist_sq < min_dist_sq) {
                min_dist_sq = dist_sq;
                best_label = static_cast<int>(j);
            }
        }

        labels[i] = best_label;
    }
#endif

    return labels;
}

float RSkMeans::squared_distance(int i, int j) const {
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
RSkMeans::cluster(int k, int m, const std::string& index_type,
                   const std::string& index_params, unsigned int random_seed) {
    if (!preprocessed_) {
        throw std::runtime_error("Must call preprocess() before cluster()");
    }

    if (k <= 0 || k > n_) {
        throw std::invalid_argument("k must be in range [1, n]");
    }

    // Initialize RNG
    rng_.seed(random_seed);

    // Clear previous clustering
    selected_center_indices_.clear();

    // Initialize FAISS index
    initialize_index(index_type, index_params);

    // Step 1: Choose first center uniformly at random
    std::uniform_int_distribution<int> uniform_dist(0, n_ - 1);
    int c1_idx = uniform_dist(rng_);
    float c1_norm_sq = norms_sq_[c1_idx];

    selected_center_indices_.push_back(c1_idx);
    add_center_to_index(c1_idx);

    std::cout << "Selected first center: idx=" << c1_idx
              << ", norm²=" << c1_norm_sq << std::endl;

    // Step 2: Select remaining k-1 centers using rejection sampling
    for (int i = 1; i < k; ++i) {
        int next_center = sample_next_center(m, c1_norm_sq);
        selected_center_indices_.push_back(next_center);
        add_center_to_index(next_center);

        if ((i + 1) % 10 == 0 || i == k - 1) {
            std::cout << "Selected " << (i + 1) << "/" << k << " centers" << std::endl;
        }
    }

    // Step 3: Uncenter the selected centers
    std::vector<float> centers(k * d_);
    for (int i = 0; i < k; ++i) {
        int idx = selected_center_indices_[i];
        for (int j = 0; j < d_; ++j) {
            centers[i * d_ + j] = centered_data_[idx * d_ + j] + mean_[j];
        }
    }

    // Step 4: Assign labels
    std::vector<int> labels = assign_labels();

    return {centers, labels};
}

} // namespace rs_kmeans
