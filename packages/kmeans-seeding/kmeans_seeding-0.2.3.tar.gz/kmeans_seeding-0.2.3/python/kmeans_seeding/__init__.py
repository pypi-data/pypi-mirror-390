"""
kmeans-seeding: Fast k-means++ Seeding Algorithms
====================================================

A library providing state-of-the-art k-means initialization algorithms
implemented in C++ with Python bindings.

Algorithms included:
- Standard k-means++
- RS-k-means++ (Rejection Sampling)
- AFK-MC² (Adaptive Fast k-MC²)
- Fast-LSH k-means++ (Google 2020)

Example usage:
    >>> from kmeans_seeding import rskmeans
    >>> from sklearn.cluster import KMeans
    >>>
    >>> # Get initial centers using RS-k-means++
    >>> centers = rskmeans(X, n_clusters=10)
    >>>
    >>> # Use with sklearn
    >>> kmeans = KMeans(n_clusters=10, init=centers, n_init=1)
    >>> kmeans.fit(X)
"""

__version__ = "0.2.2"
__author__ = "Poojan Shah"
__email__ = "cs1221594@cse.iitd.ac.in"

from .initializers import (
    kmeanspp,
    rskmeans,
    rejection_sampling,  # Backwards compatibility
    afkmc2,
    multitree_lsh,
    fast_lsh,  # Backwards compatibility
    rejection_sampling_lsh_2020,
)

__all__ = [
    "kmeanspp",
    "rskmeans",
    "rejection_sampling",  # Backwards compatibility
    "afkmc2",
    "multitree_lsh",
    "fast_lsh",  # Backwards compatibility
    "rejection_sampling_lsh_2020",
    "__version__",
]
