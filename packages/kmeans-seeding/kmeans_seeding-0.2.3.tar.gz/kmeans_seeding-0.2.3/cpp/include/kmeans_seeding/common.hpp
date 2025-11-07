#ifndef KMEANS_SEEDING_COMMON_HPP
#define KMEANS_SEEDING_COMMON_HPP

#include <vector>
#include <string>
#include <cstdint>

namespace kmeans_seeding {

// Version information
constexpr const char* VERSION = "0.1.0";
constexpr int VERSION_MAJOR = 0;
constexpr int VERSION_MINOR = 1;
constexpr int VERSION_PATCH = 0;

// Common type definitions
using Index = int;
using Float = float;
using IndexVector = std::vector<Index>;
using FloatVector = std::vector<Float>;

// Algorithm types
enum class Algorithm {
    KMEANSPP,           // Standard k-means++
    RS_KMEANS,          // Rejection sampling k-means++
    AFKMC2,             // AFK-MC² (MCMC-based)
    FAST_LSH            // Fast-LSH (Google 2020)
};

// Index types for FAISS (used in RS-k-means++)
enum class IndexType {
    FLAT,               // Exact search
    LSH,                // Locality-sensitive hashing
    IVF_FLAT,           // Inverted file index
    HNSW                // Hierarchical navigable small world
};

// Convert string to IndexType
inline IndexType string_to_index_type(const std::string& str) {
    if (str == "Flat" || str == "FLAT") return IndexType::FLAT;
    if (str == "LSH") return IndexType::LSH;
    if (str == "IVFFlat" || str == "IVF_FLAT" || str == "IVF") return IndexType::IVF_FLAT;
    if (str == "HNSW") return IndexType::HNSW;
    return IndexType::FLAT; // Default
}

// Convert IndexType to string
inline std::string index_type_to_string(IndexType type) {
    switch (type) {
        case IndexType::FLAT: return "Flat";
        case IndexType::LSH: return "LSH";
        case IndexType::IVF_FLAT: return "IVFFlat";
        case IndexType::HNSW: return "HNSW";
        default: return "Flat";
    }
}

} // namespace kmeans_seeding

#endif // KMEANS_SEEDING_COMMON_HPP
