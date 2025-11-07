#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "kmeanspp_seeding.h"
#include "rejection_sampling_lsh.h"
#include "random_handler.h"
#include "rs_kmeans.hpp"
#include "afkmc2.hpp"

namespace py = pybind11;

// Helper function to convert numpy array to vector<vector<double>>
std::vector<std::vector<double>> numpy_to_vector(py::array_t<double> X) {
    auto buf = X.request();
    if (buf.ndim != 2) {
        throw std::runtime_error("Input must be a 2D array");
    }

    int n = buf.shape[0];
    int d = buf.shape[1];

    std::vector<std::vector<double>> data(n, std::vector<double>(d));
    double* ptr = static_cast<double*>(buf.ptr);

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < d; j++) {
            data[i][j] = ptr[i * d + j];
        }
    }

    return data;
}

// Helper function to extract centers from indices
py::array_t<double> extract_centers(const std::vector<std::vector<double>>& data,
                                      const std::vector<int>& indices) {
    if (indices.empty()) {
        throw std::runtime_error("No centers selected");
    }

    int k = indices.size();
    int d = data[0].size();

    auto result = py::array_t<double>({k, d});
    auto result_buf = result.request();
    double* result_ptr = static_cast<double*>(result_buf.ptr);

    for (int i = 0; i < k; i++) {
        int idx = indices[i];
        if (idx < 0 || idx >= static_cast<int>(data.size())) {
            throw std::runtime_error("Invalid center index: " + std::to_string(idx));
        }
        for (int j = 0; j < d; j++) {
            result_ptr[i * d + j] = data[idx][j];
        }
    }

    return result;
}

// 1. Standard k-means++ seeding
py::array_t<double> kmeanspp_seeding(py::array_t<double> X, int k, int random_state) {
    if (k <= 0) {
        throw std::invalid_argument("k must be positive");
    }

    auto data = numpy_to_vector(X);
    int n = data.size();

    if (k > n) {
        throw std::invalid_argument("k cannot be larger than number of samples");
    }

    // Seed the random number generator
    fast_k_means::RandomHandler::eng.seed(random_state);

    // Run k-means++ seeding
    // number_greedy_rounds=1 means standard k-means++ (one sample per center)
    fast_k_means::KMeansPPSeeding kmeanspp;
    kmeanspp.RunAlgorithm(data, k, 1);

    // Extract and return actual center points
    return extract_centers(data, kmeanspp.centers_);
}

// 2. Rejection Sampling LSH (Google 2020)
py::array_t<double> rejection_sampling_lsh_2020(
    py::array_t<double> X,
    int k,
    int number_of_trees,
    double scaling_factor,
    int number_greedy_rounds,
    double boosting_prob_factor,
    int random_state) {

    if (k <= 0) {
        throw std::invalid_argument("k must be positive");
    }

    auto data = numpy_to_vector(X);
    int n = data.size();

    if (k > n) {
        throw std::invalid_argument("k cannot be larger than number of samples");
    }

    // Seed the random number generator
    fast_k_means::RandomHandler::eng.seed(random_state);

    // Run rejection sampling LSH algorithm
    fast_k_means::RejectionSamplingLSH rs_lsh;
    rs_lsh.RunAlgorithm(data, k, number_of_trees, scaling_factor,
                        number_greedy_rounds, boosting_prob_factor);

    // Extract and return actual center points
    return extract_centers(data, rs_lsh.centers);
}

// Helper function to convert numpy array to vector<float> (for RS-kmeans and AFKMC2)
std::vector<float> numpy_to_float_vector(py::array_t<double> X, int& n, int& d) {
    auto buf = X.request();
    if (buf.ndim != 2) {
        throw std::runtime_error("Input must be a 2D array");
    }

    n = buf.shape[0];
    d = buf.shape[1];

    std::vector<float> data(n * d);
    double* ptr = static_cast<double*>(buf.ptr);

    for (int i = 0; i < n * d; i++) {
        data[i] = static_cast<float>(ptr[i]);
    }

    return data;
}

// Helper function to convert float centers to numpy array
py::array_t<double> float_centers_to_numpy(const std::vector<float>& centers_flat, int k, int d) {
    auto result = py::array_t<double>({k, d});
    auto result_buf = result.request();
    double* result_ptr = static_cast<double*>(result_buf.ptr);

    for (size_t i = 0; i < centers_flat.size(); i++) {
        result_ptr[i] = static_cast<double>(centers_flat[i]);
    }

    return result;
}

// 3. RS-k-means++ (Rejection Sampling with FAISS)
py::array_t<double> rejection_sampling(
    py::array_t<double> X,
    int k,
    int max_iter,
    const std::string& index_type,
    int random_state) {

    if (k <= 0) {
        throw std::invalid_argument("k must be positive");
    }

    int n, d;
    auto data = numpy_to_float_vector(X, n, d);

    if (k > n) {
        throw std::invalid_argument("k cannot be larger than number of samples");
    }

    // Create and run RS-kmeans
    rs_kmeans::RSkMeans model;
    model.preprocess(data, n, d);

    int m = (max_iter > 0) ? max_iter : -1;  // -1 means unlimited
    auto result = model.cluster(k, m, index_type, "", random_state);

    // Convert centers to numpy array
    return float_centers_to_numpy(result.first, k, d);
}

// 4. AFK-MC² (MCMC-based seeding)
py::array_t<double> afkmc2(
    py::array_t<double> X,
    int k,
    int chain_length,
    const std::string& index_type,
    int random_state) {

    if (k <= 0) {
        throw std::invalid_argument("k must be positive");
    }

    int n, d;
    auto data = numpy_to_float_vector(X, n, d);

    if (k > n) {
        throw std::invalid_argument("k cannot be larger than number of samples");
    }

    // Create and run AFKMC2
    rs_kmeans::AFKMC2 model;
    model.preprocess(data, n, d);

    auto result = model.cluster(k, chain_length, index_type, "", random_state);

    // Convert centers to numpy array
    return float_centers_to_numpy(result.first, k, d);
}

// Wrapper classes for sklearn-compatible interface
class KMeansPPEstimator {
public:
    KMeansPPEstimator(int n_clusters = 8, int random_state = 0)
        : n_clusters_(n_clusters), random_state_(random_state) {}

    py::array_t<double> fit(py::array_t<double> X) {
        centers_ = kmeanspp_seeding(X, n_clusters_, random_state_);
        return centers_;
    }

    py::array_t<double> get_centers() const {
        return centers_;
    }

    int get_n_clusters() const { return n_clusters_; }
    int get_random_state() const { return random_state_; }

private:
    int n_clusters_;
    int random_state_;
    py::array_t<double> centers_;
};

class RejectionSamplingLSH2020Estimator {
public:
    RejectionSamplingLSH2020Estimator(
        int n_clusters = 8,
        int number_of_trees = 3,
        double scaling_factor = 0.5,
        int number_greedy_rounds = 10,
        double boosting_prob_factor = 1.0,
        int random_state = 0)
        : n_clusters_(n_clusters),
          number_of_trees_(number_of_trees),
          scaling_factor_(scaling_factor),
          number_greedy_rounds_(number_greedy_rounds),
          boosting_prob_factor_(boosting_prob_factor),
          random_state_(random_state) {}

    py::array_t<double> fit(py::array_t<double> X) {
        centers_ = rejection_sampling_lsh_2020(
            X, n_clusters_, number_of_trees_, scaling_factor_,
            number_greedy_rounds_, boosting_prob_factor_, random_state_);
        return centers_;
    }

    py::array_t<double> get_centers() const {
        return centers_;
    }

    int get_n_clusters() const { return n_clusters_; }

private:
    int n_clusters_;
    int number_of_trees_;
    double scaling_factor_;
    int number_greedy_rounds_;
    double boosting_prob_factor_;
    int random_state_;
    py::array_t<double> centers_;
};

PYBIND11_MODULE(_core, m) {
    m.doc() = "kmeans-seeding: Fast k-means++ seeding algorithms (C++ core module)";

    // Seeding functions
    m.def("kmeanspp_seeding", &kmeanspp_seeding,
          "Standard k-means++ seeding algorithm.\n\n"
          "Parameters\n"
          "----------\n"
          "X : array-like of shape (n_samples, n_features)\n"
          "    Training data\n"
          "k : int\n"
          "    Number of clusters\n"
          "random_state : int, default=0\n"
          "    Random seed for reproducibility\n\n"
          "Returns\n"
          "-------\n"
          "centers : ndarray of shape (k, n_features)\n"
          "    Initial cluster centers",
          py::arg("X"),
          py::arg("k"),
          py::arg("random_state") = 0);

    m.def("rejection_sampling_lsh_2020", &rejection_sampling_lsh_2020,
          "Rejection Sampling LSH k-means++ (Google 2020).\n\n"
          "Fast k-means++ initialization using LSH and tree-based rejection sampling.\n\n"
          "Parameters\n"
          "----------\n"
          "X : array-like of shape (n_samples, n_features)\n"
          "    Training data\n"
          "k : int\n"
          "    Number of clusters\n"
          "number_of_trees : int, default=3\n"
          "    Number of trees for multi-tree embedding\n"
          "scaling_factor : float, default=0.5\n"
          "    Scaling factor for tree embedding\n"
          "number_greedy_rounds : int, default=10\n"
          "    Number of greedy rounds per center\n"
          "boosting_prob_factor : float, default=1.0\n"
          "    Probability boosting factor\n"
          "random_state : int, default=0\n"
          "    Random seed for reproducibility\n\n"
          "Returns\n"
          "-------\n"
          "centers : ndarray of shape (k, n_features)\n"
          "    Initial cluster centers",
          py::arg("X"),
          py::arg("k"),
          py::arg("number_of_trees") = 3,
          py::arg("scaling_factor") = 0.5,
          py::arg("number_greedy_rounds") = 10,
          py::arg("boosting_prob_factor") = 1.0,
          py::arg("random_state") = 0);

    m.def("rejection_sampling", &rejection_sampling,
          "RS-k-means++ seeding using rejection sampling with FAISS.\n\n"
          "Parameters\n"
          "----------\n"
          "X : array-like of shape (n_samples, n_features)\n"
          "    Training data\n"
          "k : int\n"
          "    Number of clusters\n"
          "max_iter : int\n"
          "    Maximum rejection sampling iterations per center\n"
          "index_type : str\n"
          "    FAISS index type ('Flat', 'LSH', 'IVFFlat', 'HNSW')\n"
          "random_state : int, default=0\n"
          "    Random seed for reproducibility\n\n"
          "Returns\n"
          "-------\n"
          "centers : ndarray of shape (k, n_features)\n"
          "    Initial cluster centers",
          py::arg("X"),
          py::arg("k"),
          py::arg("max_iter"),
          py::arg("index_type"),
          py::arg("random_state") = 0);

    m.def("afkmc2", &afkmc2,
          "AFK-MC² seeding using MCMC sampling.\n\n"
          "Parameters\n"
          "----------\n"
          "X : array-like of shape (n_samples, n_features)\n"
          "    Training data\n"
          "k : int\n"
          "    Number of clusters\n"
          "chain_length : int\n"
          "    Markov chain length per center\n"
          "index_type : str\n"
          "    FAISS index type for label assignment\n"
          "random_state : int, default=0\n"
          "    Random seed for reproducibility\n\n"
          "Returns\n"
          "-------\n"
          "centers : ndarray of shape (k, n_features)\n"
          "    Initial cluster centers",
          py::arg("X"),
          py::arg("k"),
          py::arg("chain_length"),
          py::arg("index_type"),
          py::arg("random_state") = 0);

    // Estimator classes
    py::class_<KMeansPPEstimator>(m, "KMeansPPEstimator")
        .def(py::init<int, int>(),
             py::arg("n_clusters") = 8,
             py::arg("random_state") = 0)
        .def("fit", &KMeansPPEstimator::fit,
             "Compute k-means++ initialization",
             py::arg("X"))
        .def("get_centers", &KMeansPPEstimator::get_centers,
             "Get the computed cluster centers")
        .def_property_readonly("n_clusters", &KMeansPPEstimator::get_n_clusters)
        .def_property_readonly("random_state", &KMeansPPEstimator::get_random_state);

    py::class_<RejectionSamplingLSH2020Estimator>(m, "RejectionSamplingLSH2020Estimator")
        .def(py::init<int, int, double, int, double, int>(),
             py::arg("n_clusters") = 8,
             py::arg("number_of_trees") = 3,
             py::arg("scaling_factor") = 0.5,
             py::arg("number_greedy_rounds") = 10,
             py::arg("boosting_prob_factor") = 1.0,
             py::arg("random_state") = 0)
        .def("fit", &RejectionSamplingLSH2020Estimator::fit,
             "Compute rejection sampling LSH initialization",
             py::arg("X"))
        .def("get_centers", &RejectionSamplingLSH2020Estimator::get_centers,
             "Get the computed cluster centers")
        .def_property_readonly("n_clusters", &RejectionSamplingLSH2020Estimator::get_n_clusters);

    m.attr("__version__") = "0.1.0";
}
