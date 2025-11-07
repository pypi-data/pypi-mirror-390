# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

**Common Commands:**

```bash
# Build and install the package
pip install -e .                       # Development install
pip install .                          # Regular install

# Build C++ extension manually (if needed)
cd cpp
mkdir build && cd build
cmake .. -DBUILD_PYTHON=ON
make -j$(nproc)

# Run tests
pytest tests/                          # All tests
pytest tests/test_rejection_sampling.py  # Specific test file
pytest -v -s tests/                    # Verbose with output

# LaTeX paper compilation (if working on theory)
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex

# Quantization analysis experiments
cd quantization_analysis
source venv/bin/activate
python3 run_local_experiments.py      # Local datasets
python3 run_experiments.py            # UCI ML datasets

# Publish to PyPI (maintainers only)
./republish.sh                         # Automated build and publish script
```

## Project Overview

**kmeans-seeding** is a Python package providing fast k-means++ initialization algorithms implemented in C++ with Python bindings. Published on PyPI as `kmeans-seeding`.

### Key Algorithms

1. **RS-k-means++** (Rejection Sampling) - *Primary contribution*
   - Fast approximate D² sampling using FAISS-based rejection sampling
   - Supports multiple FAISS index types (Flat, LSH, IVFFlat, HNSW)
   - Also supports FAISS-free FastLSH and GoogleLSH indices
   - Best for large datasets (n > 10,000)

2. **AFK-MC²** (Adaptive Fast k-MC²)
   - MCMC-based sampling without computing all distances
   - Good balance of speed and quality

3. **Fast-LSH k-means++** (Google 2020 implementation)
   - Tree embedding with LSH for fast sampling
   - Excellent for high-dimensional data
   - **Optimized Nov 2025**: Fixed critical hash collision bug, 20-40% faster

4. **Standard k-means++**
   - Classic D² sampling (baseline)

## Repository Structure

```
.
├── cpp/                              # C++ implementation
│   ├── CMakeLists.txt               # Build configuration
│   ├── include/kmeans_seeding/      # C++ headers
│   └── src/                         # C++ source files
│       ├── rs_kmeans.cpp            # RS-k-means++ implementation
│       ├── afkmc2.cpp               # AFK-MC² implementation
│       ├── fast_lsh.cpp             # Fast-LSH implementation
│       ├── python_bindings.cpp      # pybind11 bindings
│       ├── kmeanspp_seeding.cc      # Standard k-means++
│       ├── lsh.cc                   # LSH data structure
│       ├── rejection_sampling_lsh.cc # Rejection sampling core
│       └── [other core files]       # Tree embedding, utilities
│
├── python/kmeans_seeding/           # Python package
│   ├── __init__.py                  # Package exports
│   └── initializers.py              # User-facing API functions
│
├── tests/                           # Pytest test suite
│   ├── conftest.py                  # Test fixtures
│   ├── test_rejection_sampling.py   # RS-k-means++ tests
│   ├── test_afkmc2.py              # AFK-MC² tests
│   ├── test_fast_lsh.py            # Fast-LSH tests
│   ├── test_kmeanspp.py            # k-means++ tests
│   ├── test_all_methods.py         # Integration tests
│   └── test_package.py             # Package-level tests
│
├── docs/                            # Documentation
│   ├── README.md                   # Documentation index
│   ├── development/                # Developer guides
│   ├── publishing/                 # Maintainer/release guides
│   └── archive/                    # Historical process docs
│
├── quantization_analysis/           # Research experiments (optional)
│   ├── [various analysis scripts]  # Empirical studies
│   └── venv/                       # Separate virtual environment
│
├── archive/                         # Legacy code (archived)
│   ├── rs_kmeans/                  # Old development directory
│   └── fast_k_means_2020/          # 2020 NeurIPS paper implementation
│
├── benchmarks/                      # Performance benchmarks
├── examples/                        # Usage examples
│
├── pyproject.toml                  # Package metadata & build config
├── setup.py                        # Build script (uses CMake)
├── CMakeLists.txt                  # Top-level CMake (delegates to cpp/)
├── README.md                       # User documentation
├── CLAUDE.md                       # This file
└── LICENSE                         # MIT License
```

## Build System Architecture

### Three-Layer Build Process

1. **CMake (C++ Layer)**: `cpp/CMakeLists.txt`
   - Builds C++ library `kmeans_seeding_core` (static library)
   - Builds Python extension `_core` (pybind11 module) if `BUILD_PYTHON=ON`
   - Handles OpenMP, FAISS detection
   - Platform-specific compiler flags

2. **setup.py (Python Layer)**
   - Custom `CMakeBuild` class extends setuptools `build_ext`
   - Invokes CMake to build C++ extension
   - Copies built `_core` module to correct location
   - Handles cross-platform builds (macOS, Linux, Windows)

3. **pyproject.toml (Package Metadata)**
   - PEP 517/518 build configuration
   - Package metadata, dependencies, versioning
   - pytest, black, mypy configuration
   - `cibuildwheel` config for wheel building

### Key Build Dependencies

- **Required**: CMake 3.15+, C++17 compiler, pybind11, NumPy
- **Optional**: FAISS (enables rejection sampling), OpenMP (parallelization)

## Python API Architecture

### Two-Layer Design

1. **C++ Extension (`_core` module)**: Built from `cpp/src/python_bindings.cpp`
   - Low-level functions exposed via pybind11
   - Direct NumPy array access (zero-copy)
   - Functions: `kmeanspp_seeding()`, `rskmeans_seeding()`, `afkmc2_seeding()`, `fast_lsh_seeding()`, `rejection_sampling_lsh_2020_seeding()`

2. **Python Wrapper (`python/kmeans_seeding/initializers.py`)**
   - User-facing API with clean sklearn-compatible interface
   - Input validation, type conversion, error handling
   - Functions: `kmeanspp()`, `rskmeans()`, `afkmc2()`, `multitree_lsh()`, `fast_lsh()` (alias), `rejection_sampling()` (alias)
   - All functions return `(n_clusters, n_features)` NumPy arrays of cluster centers

### Function Naming

- **User API**: Clean names (`rskmeans`, `afkmc2`, `multitree_lsh`)
- **Backwards compatibility**: Aliases (`rejection_sampling` → `rskmeans`, `fast_lsh` → `multitree_lsh`)
- **Internal C++ functions**: Suffixed with `_seeding` (e.g., `rskmeans_seeding()`)

## Development Workflow

### Making Changes to C++ Code

1. Edit files in `cpp/src/` or `cpp/include/kmeans_seeding/`
2. Rebuild: `pip install -e .` (runs CMake + compilation)
3. Test: `pytest tests/test_rejection_sampling.py -v`

### Making Changes to Python API

1. Edit `python/kmeans_seeding/initializers.py`
2. No rebuild needed (pure Python)
3. Test: `pytest tests/test_package.py -v`

### Adding a New Algorithm

1. Implement C++ class in `cpp/src/new_algorithm.cpp` + header in `cpp/include/kmeans_seeding/`
2. Add source file to `cpp/CMakeLists.txt` in `ALGORITHM_SOURCES`
3. Add pybind11 binding in `cpp/src/python_bindings.cpp`
4. Add Python wrapper in `python/kmeans_seeding/initializers.py`
5. Export in `python/kmeans_seeding/__init__.py`
6. Write tests in `tests/test_new_algorithm.py`

### Testing Strategy

- **Unit tests**: Each algorithm has its own test file (`test_*.py`)
- **Integration tests**: `test_all_methods.py` compares all algorithms
- **Package tests**: `test_package.py` validates imports, API, versioning
- **Fixtures**: Defined in `conftest.py` (shared test data)

Run tests with different verbosity:
```bash
pytest tests/                           # Default
pytest tests/ -v                        # Verbose
pytest tests/ -v -s                     # Verbose + show print statements
pytest tests/test_rejection_sampling.py -k test_basic  # Single test
```

## Important Implementation Details

### FAISS Integration

- **Optional dependency**: Code compiles and works without FAISS
- **Detection**: CMake checks for FAISS, sets `HAS_FAISS` preprocessor flag if found
- **Conditional compilation**: `#ifdef HAS_FAISS` guards wrap all FAISS-specific code
- **Usage**: Only in `rs_kmeans.cpp` for rejection sampling with certain index types
- **Index types**:
  - **With FAISS**: Flat (exact), LSH (fast), IVFFlat (balanced), HNSW (very fast)
  - **Without FAISS**: FastLSH, GoogleLSH (use native LSH implementations)
- **Runtime behavior**: If FAISS indices requested but FAISS not available, throws `RuntimeError` with installation instructions
- **Fallback**: All other algorithms (kmeanspp, afkmc2, multitree_lsh) work without FAISS

### OpenMP Parallelization

- **Platform-specific**: macOS requires Homebrew `libomp`, Linux uses system OpenMP
- **Detection**: CMake finds OpenMP library and sets flags
- **Usage**: Parallelizes distance computations in core algorithms
- **Fallback**: Builds without OpenMP if not found (slower but works)

### NumPy Integration

- **C++ side**: Uses pybind11 NumPy interface for zero-copy array access
- **Python side**: Converts input to C-contiguous float64 arrays
- **Memory layout**: All arrays are C-contiguous (`order='C'`)
- **Type safety**: Python validates input dimensions, C++ assumes validated input

### Random State Handling

- **Python API**: Optional `random_state` parameter (int or None)
- **Default behavior**: If None, generates random seed from `np.random`
- **C++ layer**: Always receives integer seed
- **Reproducibility**: Same seed → same initialization

## Publishing & Versioning

### Version Management

- **Single source of truth**: `python/kmeans_seeding/__init__.py` (`__version__`)
- **Sync with pyproject.toml**: Update both when bumping version
- **Semantic versioning**: MAJOR.MINOR.PATCH (currently 0.2.2)

### Publishing to PyPI

```bash
# Automated (recommended)
./republish.sh  # Builds sdist + wheel, uploads to PyPI

# Manual steps (for debugging)
python -m build           # Creates dist/*.tar.gz and dist/*.whl
twine check dist/*        # Validate packages
twine upload dist/*       # Upload to PyPI
```

### Pre-publish Checklist

1. Update version in `__init__.py` and `pyproject.toml`
2. Run full test suite: `pytest tests/`
3. Test clean install: `pip install -e .` in fresh venv
4. Update CHANGELOG/README if needed
5. Commit and tag: `git tag v0.2.2`
6. Run `./republish.sh`

## Documentation Organization

All documentation is now organized in the `docs/` directory:

- **`docs/development/`**: Developer guides (setup, architecture)
- **`docs/publishing/`**: Maintainer guides (releases, PyPI publishing)
- **`docs/archive/`**: Historical process documentation (fixes, status updates)
- **`docs/README.md`**: Complete documentation index

## Legacy Code (archive/)

### `archive/rs_kmeans/` (Archived)

- Old development directory from pre-unification
- Contains benchmarks, old build scripts, standalone tests
- **Do not modify**: Use `cpp/` and `python/` for new development
- Kept for historical reference and benchmark scripts

### `archive/fast_k_means_2020/` (Archived)

- Original C++ implementation from NeurIPS 2020 paper
- Standalone command-line tool (no Python bindings)
- **Compilation**: `g++ -std=c++11 -O3 -o fast_kmeans *.cc`
- **Usage**: Reads from stdin in custom format
- Kept for reproducibility of original paper results

### `quantization_analysis/` (Research)

- Empirical analysis of quantization dimension
- Separate from main package (not published to PyPI)
- Has own virtual environment and dependencies
- See `quantization_analysis/USAGE.md` for details

## Recent Optimizations (November 2025)

### FastLSH Data Structure Improvements

**See:** `FAST_LSH_OPTIMIZATIONS.md` for full details.

**Critical bug fixed:**
- Systematic sampling bug when `k > d_padded` caused hash collisions
- Integer division `step = d_padded / k` would produce `step=0`
- Example: d=3 (d_padded=4), k=10 → all hash indices were 0
- Now uses floating-point sampling and wrap-around with offsets

**Performance improvements:**
- 20-40% faster queries overall
- Up to 13× faster for top-k selection when k << n
- Power-of-2 calculation: O(1) instead of O(log n)
- Cached FHT normalization eliminates repeated `sqrt()` calls
- Thread-local buffers eliminate allocations in hot paths
- Partial sorting for efficient top-k candidate selection

**Testing:**
```bash
# Run optimized stress tests
pytest tests/test_fast_lsh_stress.py -v

# Quick verification
python3 test_optimizations.py
```

## Common Issues & Solutions

### "C++ extension not available" error

- **Cause**: `_core` module not built or not found
- **Solution**: Run `pip install -e .` to rebuild C++ extension
- **Debug**: Check `import kmeans_seeding._core` directly

### FAISS not found during build

- **Cause**: FAISS not installed or CMake can't find it
- **Solution**: `conda install -c pytorch faiss-cpu`
- **Note**: Package still works without FAISS!
  - Use `index_type='FastLSH'` or `index_type='GoogleLSH'` with `rskmeans()`
  - All other algorithms work normally (kmeanspp, afkmc2, multitree_lsh)
  - FAISS-specific indices (Flat, LSH, IVFFlat, HNSW) will raise helpful error if requested
  - FastLSH is now highly optimized (20-40% faster) and recommended for most use cases

### OpenMP warnings on macOS

- **Cause**: OpenMP not found by CMake
- **Solution**: `brew install libomp`
- **Note**: Package still works without OpenMP (slower)

### CMake can't find pybind11

- **Cause**: pybind11 not installed
- **Solution**: `pip install pybind11`

### Tests fail with "No module named '_core'"

- **Cause**: Running tests without installing package
- **Solution**: `pip install -e .` before running tests

## Code Style & Conventions

### C++ Code

- **Standard**: C++17
- **Style**: Google C++ style (mostly)
- **Naming**:
  - Classes: `PascalCase` (e.g., `RejectionSampler`)
  - Functions: `snake_case` (e.g., `compute_distances`)
  - Member variables: `snake_case_` with trailing underscore
- **Headers**: Use include guards, forward declarations when possible

### Python Code

- **Standard**: PEP 8
- **Type hints**: Encouraged but not required
- **Docstrings**: NumPy style
- **Imports**: Absolute imports within package
- **Formatting**: Black (line length 88)

### Testing

- **Framework**: pytest
- **Naming**: `test_*.py` files, `test_*` functions
- **Assertions**: Use pytest assertions (`assert x == y`)
- **Fixtures**: Define in `conftest.py` for reuse
- **Coverage**: Use `pytest --cov=kmeans_seeding`

## Working with the LaTeX Paper

**Note**: The theoretical paper and quantization analysis are separate from the main package.

### Building the Paper

```bash
# From repository root
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Key Sections

- **Theorem 1**: Main approximation guarantee for RS-k-means++
- **Algorithm descriptions**: Theoretical analysis of rejection sampling
- **Dependencies**: `prefix.sty` (LaTeX packages), `refs.bib` (bibliography)

## Platform-Specific Notes

### macOS

- **Architecture**: Supports both x86_64 and arm64 (Apple Silicon)
- **OpenMP**: Requires Homebrew libomp (`brew install libomp`)
- **Build**: Set `ARCHFLAGS` env var for specific arch if needed

### Linux

- **OpenMP**: Usually available via system packages
- **FAISS**: Use conda or build from source
- **manylinux wheels**: Built via `cibuildwheel` for broad compatibility

### Windows

- **Compiler**: Requires Visual Studio 2017+ or MinGW
- **OpenMP**: Included with MSVC
- **FAISS**: Best installed via conda
- **Note**: Less tested than macOS/Linux

## Performance Optimization

### For Small Datasets (n < 10,000)

- Use `kmeanspp()` (standard k-means++)
- No FAISS needed, fast exact computation

### For Medium Datasets (10,000 < n < 100,000)

- Use `rskmeans()` with `index_type='LSH'`
- Good speedup with minimal quality loss

### For Large Datasets (n > 100,000)

- Use `rskmeans()` with `index_type='IVFFlat'` or `'HNSW'`
- Adjust `max_iter` parameter to trade speed vs. quality
- Consider `afkmc2()` for very high dimensions

### Parallelization

- OpenMP automatically parallelizes distance computations
- Set `OMP_NUM_THREADS` environment variable to control threads
- Default: Uses all available cores
