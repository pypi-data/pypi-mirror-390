"""
K-means seeding algorithms - User-facing API

This module provides clean, sklearn-compatible functions for k-means initialization.
All functions return initial cluster centers that can be used with sklearn.cluster.KMeans.
"""

import numpy as np
from typing import Optional, Union
import warnings

try:
    from . import _core
    HAS_CORE = True
except ImportError:
    HAS_CORE = False
    warnings.warn(
        "C++ extension module '_core' not found. "
        "Please rebuild the package or install from source.",
        ImportWarning
    )


def _validate_input(X, n_clusters):
    """Validate and prepare input data."""
    X = np.asarray(X, dtype=np.float64, order='C')  # Changed to float64 for C++ compatibility

    if X.ndim != 2:
        raise ValueError(f"X must be 2D array, got {X.ndim}D")

    n_samples, n_features = X.shape

    if n_samples < n_clusters:
        raise ValueError(
            f"n_samples={n_samples} should be >= n_clusters={n_clusters}"
        )

    if n_clusters <= 0:
        raise ValueError(f"n_clusters={n_clusters} should be > 0")

    return X, n_samples, n_features


def kmeanspp(
    X: np.ndarray,
    n_clusters: int,
    *,
    random_state: Optional[int] = None
) -> np.ndarray:
    """
    Standard k-means++ initialization.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Training data.
    n_clusters : int
        Number of clusters.
    random_state : int, optional
        Random seed for reproducibility.

    Returns
    -------
    centers : ndarray of shape (n_clusters, n_features)
        Initial cluster centers selected using k-means++.

    References
    ----------
    Arthur, D., & Vassilvitskii, S. (2007).
    k-means++: The advantages of careful seeding.

    Examples
    --------
    >>> from kmeans_seeding import kmeanspp
    >>> from sklearn.cluster import KMeans
    >>> import numpy as np
    >>>
    >>> X = np.random.randn(1000, 10)
    >>> centers = kmeanspp(X, n_clusters=5)
    >>> kmeans = KMeans(n_clusters=5, init=centers, n_init=1)
    >>> kmeans.fit(X)
    """
    if not HAS_CORE:
        raise RuntimeError("C++ extension not available. Please reinstall the package.")

    X, n_samples, n_features = _validate_input(X, n_clusters)

    if random_state is None:
        random_state = np.random.randint(0, 2**31)

    # Use the C++ k-means++ implementation
    centers = _core.kmeanspp_seeding(X, n_clusters, random_state)

    return centers


def rskmeans(
    X: np.ndarray,
    n_clusters: int,
    *,
    max_iter: int = 50,
    index_type: str = 'LSH',
    random_state: Optional[int] = None
) -> np.ndarray:
    """
    RS-k-means++ initialization using rejection sampling.

    Fast k-means++ seeding that uses rejection sampling with approximate
    nearest neighbor queries for efficient D² sampling.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Training data.
    n_clusters : int
        Number of clusters.
    max_iter : int, default=50
        Maximum number of rejection sampling iterations per center.
        Higher values improve quality but take longer.
    index_type : {'Flat', 'LSH', 'IVFFlat', 'HNSW', 'FastLSH', 'GoogleLSH'}, default='LSH'
        Approximate nearest neighbor index type:
        - 'Flat': Exact search (slowest, most accurate) [requires FAISS]
        - 'LSH': FAISS LSH (fast, ~90-95% accuracy) [requires FAISS]
        - 'IVFFlat': Inverted file index (fast, ~99% accuracy) [requires FAISS]
        - 'HNSW': Hierarchical NSW (very fast, ~95-99% accuracy) [requires FAISS]
        - 'FastLSH': DHHash-based Fast LSH (very fast, ~90-95% accuracy) [works without FAISS]
        - 'GoogleLSH': Google's LSH implementation (fast, ~85-90% accuracy) [works without FAISS]

        Note: FAISS indices (Flat, LSH, IVFFlat, HNSW) are only available if FAISS is installed.
        Install with: conda install -c pytorch faiss-cpu
    random_state : int, optional
        Random seed for reproducibility.

    Returns
    -------
    centers : ndarray of shape (n_clusters, n_features)
        Initial cluster centers selected using RS-k-means++.

    References
    ----------
    Shah, P., Agrawal, S., & Jaiswal, R. (2025).
    A New Rejection Sampling Approach to k-means++ With Improved Trade-Offs.
    arXiv preprint arXiv:2502.02085.

    Examples
    --------
    >>> from kmeans_seeding import rskmeans
    >>> from sklearn.cluster import KMeans
    >>> import numpy as np
    >>>
    >>> X = np.random.randn(10000, 50)
    >>> centers = rskmeans(X, n_clusters=100, index_type='LSH')
    >>> kmeans = KMeans(n_clusters=100, init=centers, n_init=1)
    >>> kmeans.fit(X)
    """
    if not HAS_CORE:
        raise RuntimeError("C++ extension not available. Please reinstall the package.")

    X, n_samples, n_features = _validate_input(X, n_clusters)

    if random_state is None:
        random_state = np.random.randint(0, 2**31)

    # Use the C++ rejection_sampling implementation
    centers = _core.rejection_sampling(X, n_clusters, max_iter, index_type, random_state)

    return centers


# Backwards compatibility alias
rejection_sampling = rskmeans


def afkmc2(
    X: np.ndarray,
    n_clusters: int,
    *,
    chain_length: int = 200,
    index_type: str = 'Flat',
    random_state: Optional[int] = None
) -> np.ndarray:
    """
    AFK-MC² initialization using MCMC sampling.

    Adaptive Fast k-MC² uses Markov Chain Monte Carlo to sample centers
    according to the D² distribution without computing all distances.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Training data.
    n_clusters : int
        Number of clusters.
    chain_length : int, default=200
        Length of the Markov chain per center.
        Longer chains give better quality but take more time.
    index_type : {'Flat', 'LSH', 'HNSW'}, default='Flat'
        FAISS index type for label assignment (not used in sampling).
    random_state : int, optional
        Random seed for reproducibility.

    Returns
    -------
    centers : ndarray of shape (n_clusters, n_features)
        Initial cluster centers selected using AFK-MC².

    References
    ----------
    Bachem, O., Lucic, M., Hassani, H., & Krause, A. (2016).
    Approximate k-means++ in sublinear time.
    AAAI Conference on Artificial Intelligence.

    Examples
    --------
    >>> from kmeans_seeding import afkmc2
    >>> from sklearn.cluster import KMeans
    >>> import numpy as np
    >>>
    >>> X = np.random.randn(10000, 50)
    >>> centers = afkmc2(X, n_clusters=100, chain_length=200)
    >>> kmeans = KMeans(n_clusters=100, init=centers, n_init=1)
    >>> kmeans.fit(X)
    """
    if not HAS_CORE:
        raise RuntimeError("C++ extension not available. Please reinstall the package.")

    X, n_samples, n_features = _validate_input(X, n_clusters)

    if random_state is None:
        random_state = np.random.randint(0, 2**31)

    # Use the C++ afkmc2 implementation
    centers = _core.afkmc2(X, n_clusters, chain_length, index_type, random_state)

    return centers


def multitree_lsh(
    X: np.ndarray,
    n_clusters: int,
    *,
    n_trees: int = 4,
    scaling_factor: float = 1.0,
    n_greedy_samples: int = 1,
    index_type: str = 'Flat',
    random_state: Optional[int] = None
) -> np.ndarray:
    """
    Fast k-means++ using tree embedding (Google 2020).

    Uses tree embedding and integer casting for fast D² sampling.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Training data.
    n_clusters : int
        Number of clusters.
    n_trees : int, default=4
        Number of trees for embedding.
    scaling_factor : float, default=1.0
        Scaling factor for integer casting.
    n_greedy_samples : int, default=1
        Number of greedy samples per center.
    index_type : str, default='Flat'
        FAISS index type for label assignment.
    random_state : int, optional
        Random seed for reproducibility.

    Returns
    -------
    centers : ndarray of shape (n_clusters, n_features)
        Initial cluster centers.

    References
    ----------
    Cohen-Addad, V., Lattanzi, S., Mitrović, S., Norouzi-Fard, A.,
    Parotsidis, N., & Tarnawski, J. (2020).
    Fast and accurate k-means++ via rejection sampling.
    NeurIPS 2020.

    Examples
    --------
    >>> from kmeans_seeding import multitree_lsh
    >>> from sklearn.cluster import KMeans
    >>> import numpy as np
    >>>
    >>> X = np.random.randn(10000, 50)
    >>> centers = multitree_lsh(X, n_clusters=100)
    >>> kmeans = KMeans(n_clusters=100, init=centers, n_init=1)
    >>> kmeans.fit(X)
    """
    if not HAS_CORE:
        raise RuntimeError("C++ extension not available. Please reinstall the package.")

    X, n_samples, n_features = _validate_input(X, n_clusters)

    if random_state is None:
        random_state = np.random.randint(0, 2**31)

    # fast_lsh is an alias for rejection_sampling_lsh_2020
    # Both implement the same Google 2020 algorithm with tree embedding
    centers = _core.rejection_sampling_lsh_2020(
        X,
        n_clusters,
        number_of_trees=n_trees,
        scaling_factor=scaling_factor,
        number_greedy_rounds=n_greedy_samples,
        boosting_prob_factor=1.0,
        random_state=random_state
    )

    return centers


# Backwards compatibility alias
fast_lsh = multitree_lsh


def rejection_sampling_lsh_2020(
    X: np.ndarray,
    n_clusters: int,
    *,
    n_trees: int = 4,
    scaling_factor: float = 1.0,
    n_greedy_samples: int = 1,
    boosting_prob_factor: float = -1.0,
    index_type: str = 'Flat',
    random_state: Optional[int] = None
) -> np.ndarray:
    """
    Rejection sampling with LSH (Google 2020).

    Combines rejection sampling with LSH-based tree embedding.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Training data.
    n_clusters : int
        Number of clusters.
    n_trees : int, default=4
        Number of trees for embedding.
    scaling_factor : float, default=1.0
        Scaling factor for integer casting.
    n_greedy_samples : int, default=1
        Number of greedy samples per center.
    boosting_prob_factor : float, default=-1.0
        Multiply acceptance probability. If negative, uses sqrt(d).
    index_type : str, default='Flat'
        FAISS index type for label assignment.
    random_state : int, optional
        Random seed for reproducibility.

    Returns
    -------
    centers : ndarray of shape (n_clusters, n_features)
        Initial cluster centers.

    References
    ----------
    Cohen-Addad, V., Lattanzi, S., Mitrović, S., Norouzi-Fard, A.,
    Parotsidis, N., & Tarnawski, J. (2020).
    Fast and accurate k-means++ via rejection sampling.
    NeurIPS 2020.

    Examples
    --------
    >>> from kmeans_seeding import rejection_sampling_lsh_2020
    >>> from sklearn.cluster import KMeans
    >>> import numpy as np
    >>>
    >>> X = np.random.randn(10000, 50)
    >>> centers = rejection_sampling_lsh_2020(X, n_clusters=100)
    >>> kmeans = KMeans(n_clusters=100, init=centers, n_init=1)
    >>> kmeans.fit(X)
    """
    if not HAS_CORE:
        raise RuntimeError("C++ extension not available. Please reinstall the package.")

    X, n_samples, n_features = _validate_input(X, n_clusters)

    if random_state is None:
        random_state = np.random.randint(0, 2**31)

    # Use the C++ rejection_sampling_lsh_2020 implementation
    centers = _core.rejection_sampling_lsh_2020(
        X,
        n_clusters,
        number_of_trees=n_trees,
        scaling_factor=scaling_factor,
        number_greedy_rounds=n_greedy_samples,
        boosting_prob_factor=boosting_prob_factor if boosting_prob_factor > 0 else 1.0,
        random_state=random_state
    )

    return centers
