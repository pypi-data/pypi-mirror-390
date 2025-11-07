# kmeans-seeding: Fast k-means++ Initialization Algorithms

[![PyPI version](https://img.shields.io/pypi/v/kmeans-seeding.svg)](https://pypi.org/project/kmeans-seeding/)
[![Python versions](https://img.shields.io/pypi/pyversions/kmeans-seeding.svg)](https://pypi.org/project/kmeans-seeding/)
[![License](https://img.shields.io/pypi/l/kmeans-seeding.svg)](https://github.com/pcshah2004/kmeans-seeding/blob/main/LICENSE)
[![Documentation](https://readthedocs.org/projects/kmeans-seeding/badge/?version=latest)](https://kmeans-seeding.readthedocs.io/)

**Fast, state-of-the-art k-means initialization algorithms implemented in C++ with Python bindings.**

## Features

🚀 **Fast**: C++ implementation with OpenMP parallelization
🎯 **Accurate**: State-of-the-art algorithms with theoretical guarantees
🔌 **Compatible**: Drop-in replacement for sklearn's k-means++ initialization
📦 **Easy to use**: Simple Python API, works with NumPy arrays
🛠️ **Flexible**: Multiple algorithms to choose from

## Algorithms Included

1. **RS-k-means++** (Rejection Sampling) - *Our contribution*
   - Fast approximate D² sampling using rejection sampling
   - Supports FAISS for approximate nearest neighbors
   - Best for large datasets (n > 10,000)

2. **AFK-MC²** (Adaptive Fast k-MC²)
   - MCMC-based sampling without computing all distances
   - Good balance of speed and quality

3. **Fast-LSH k-means++** (Google 2020)
   - Tree embedding with LSH for fast sampling
   - Excellent for high-dimensional data

4. **Standard k-means++**
   - Classic D² sampling algorithm
   - Baseline for comparison

## Installation

### From PyPI (recommended)

```bash
pip install kmeans-seeding
```

### With FAISS support (recommended for large datasets)

```bash
# CPU version
conda install -c pytorch faiss-cpu
pip install kmeans-seeding

# GPU version
conda install -c pytorch faiss-gpu
pip install kmeans-seeding
```

### From source

```bash
git clone https://github.com/pcshah2004/kmeans-seeding.git
cd kmeans-seeding
pip install -e .
```

## Quick Start

```python
from kmeans_seeding import rejection_sampling
from sklearn.cluster import KMeans
import numpy as np

# Generate sample data
X = np.random.randn(10000, 50)

# Get initial centers using RS-k-means++
centers = rejection_sampling(X, n_clusters=100, index_type='LSH')

# Use with sklearn
kmeans = KMeans(n_clusters=100, init=centers, n_init=1)
kmeans.fit(X)
```

## Usage Examples

### RS-k-means++ (Rejection Sampling)

```python
from kmeans_seeding import rejection_sampling

centers = rejection_sampling(
    X,
    n_clusters=100,
    max_iter=50,           # Max rejection sampling iterations
    index_type='LSH',      # FAISS index type: 'Flat', 'LSH', 'IVFFlat', 'HNSW'
    random_state=42
)
```

### AFK-MC² (MCMC Sampling)

```python
from kmeans_seeding import afkmc2

centers = afkmc2(
    X,
    n_clusters=100,
    chain_length=200,      # Markov chain length
    random_state=42
)
```

### Fast-LSH k-means++

```python
from kmeans_seeding import fast_lsh

centers = fast_lsh(
    X,
    n_clusters=100,
    n_trees=4,             # Number of trees for embedding
    random_state=42
)
```

### Standard k-means++

```python
from kmeans_seeding import kmeanspp

centers = kmeanspp(X, n_clusters=100, random_state=42)
```

## Benchmarks

Performance comparison on various datasets:

| Dataset | n | d | Algorithm | Time (s) | Cost Ratio* |
|---------|---|---|-----------|----------|-------------|
| MNIST | 60K | 784 | k-means++ | 45.2 | 1.00 |
| | | | RS-k-means++ (LSH) | **2.1** | 1.02 |
| | | | AFK-MC² | 8.3 | 1.05 |
| CIFAR-10 | 50K | 512 | k-means++ | 38.7 | 1.00 |
| | | | RS-k-means++ (LSH) | **1.8** | 1.01 |
| | | | AFK-MC² | 6.9 | 1.04 |

*Cost ratio: Final k-means cost compared to standard k-means++

## Documentation

Full documentation available at: https://kmeans-seeding.readthedocs.io

- [Installation Guide](https://kmeans-seeding.readthedocs.io/en/latest/installation.html)
- [API Reference](https://kmeans-seeding.readthedocs.io/en/latest/api.html)
- [Algorithm Details](https://kmeans-seeding.readthedocs.io/en/latest/algorithms.html)
- [Benchmarks](https://kmeans-seeding.readthedocs.io/en/latest/benchmarks.html)

## Requirements

- Python 3.9+
- NumPy >= 1.20.0
- (Optional) FAISS >= 1.7.0 for fast approximate nearest neighbors
- (Optional) scikit-learn for full k-means clustering

## Citation

If you use this library in your research, please cite:

```bibtex
@article{shah2025rejection,
  title={A New Rejection Sampling Approach to k-means++ With Improved Trade-Offs},
  author={Shah, Poojan and Agrawal, Shashwat and Jaiswal, Ragesh},
  journal={arXiv preprint arXiv:2502.02085},
  year={2025}
}
```

For AFK-MC²:
```bibtex
@inproceedings{bachem2016approximate,
  title={Approximate k-means++ in sublinear time},
  author={Bachem, Olivier and Lucic, Mario and Hassani, Hamed and Krause, Andreas},
  booktitle={AAAI Conference on Artificial Intelligence},
  year={2016}
}
```

For Fast-LSH k-means++:
```bibtex
@inproceedings{cohen2020fast,
  title={Fast and accurate k-means++ via rejection sampling},
  author={Cohen-Addad, Vincent and Lattanzi, Silvio and Mitrovi{\'c}, Slobodan and Norouzi-Fard, Ashkan and Parotsidis, Nikos and Tarnawski, Jakub},
  booktitle={Advances in Neural Information Processing Systems},
  year={2020}
}
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FAISS library by Facebook AI Research
- scikit-learn for the k-means clustering API design
- Research supported by the Department of Computer Science, IIT Delhi

## Contact

- **Poojan Shah**: cs1221594@cse.iitd.ac.in
- **Issues**: https://github.com/pcshah2004/kmeans-seeding/issues
- **Discussions**: https://github.com/pcshah2004/kmeans-seeding/discussions
