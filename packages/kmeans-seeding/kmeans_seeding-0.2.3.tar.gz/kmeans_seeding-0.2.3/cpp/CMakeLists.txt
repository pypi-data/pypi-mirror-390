cmake_minimum_required(VERSION 3.15...3.27)
project(kmeans_seeding VERSION 0.1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -march=native")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -O0")

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include/kmeans_seeding)

# Find dependencies
# On macOS with Homebrew, help CMake find OpenMP
if(APPLE)
    set(OpenMP_C_FLAGS "-Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include")
    set(OpenMP_CXX_FLAGS "-Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include")
    set(OpenMP_C_LIB_NAMES "omp")
    set(OpenMP_CXX_LIB_NAMES "omp")
    set(OpenMP_omp_LIBRARY "/opt/homebrew/opt/libomp/lib/libomp.dylib")
endif()

find_package(OpenMP)
if(OpenMP_CXX_FOUND)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
    message(STATUS "OpenMP found: ${OpenMP_CXX_VERSION}")
else()
    message(WARNING "OpenMP not found. Building without OpenMP support.")
endif()

# FAISS (optional but recommended)
find_package(faiss QUIET)
if(faiss_FOUND)
    message(STATUS "FAISS found: ${faiss_VERSION}")
    add_compile_definitions(HAS_FAISS)
    set(FAISS_LIBRARIES faiss)
else()
    message(WARNING "FAISS not found. Some features will be disabled.")
    message(WARNING "Install FAISS: conda install -c pytorch faiss-cpu")
    set(FAISS_LIBRARIES "")
endif()

# Source files
set(CORE_SOURCES
    src/kmeanspp_seeding.cc
    src/lsh.cc
    src/rejection_sampling_lsh.cc
    src/random_handler.cc
    src/preprocess_input_points.cc
    src/tree_embedding.cc
    src/compute_cost.cc
    src/multi_tree_clustering.cc
    src/single_tree_clustering.cc
)

set(ALGORITHM_SOURCES
    src/rs_kmeans.cpp
    src/afkmc2.cpp
    src/fast_lsh.cpp
)

# Core library (without Python bindings)
add_library(kmeans_seeding_core STATIC
    ${CORE_SOURCES}
    ${ALGORITHM_SOURCES}
)

target_include_directories(kmeans_seeding_core PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

target_link_libraries(kmeans_seeding_core PUBLIC
    ${FAISS_LIBRARIES}
)

if(OpenMP_CXX_FOUND)
    target_link_libraries(kmeans_seeding_core PUBLIC OpenMP::OpenMP_CXX)
endif()

# Python bindings (optional, controlled by BUILD_PYTHON)
option(BUILD_PYTHON "Build Python bindings" ON)

if(BUILD_PYTHON)
    # Find Python and pybind11
    find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
    find_package(pybind11 CONFIG QUIET)

    if(pybind11_FOUND)
        message(STATUS "pybind11 found: ${pybind11_VERSION}")

        # Python extension module
        pybind11_add_module(_core
            src/python_bindings.cpp
        )

        target_link_libraries(_core PRIVATE
            kmeans_seeding_core
            ${FAISS_LIBRARIES}
        )

        target_include_directories(_core PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/include
        )

        # Set output directory
        set_target_properties(_core PROPERTIES
            LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/kmeans_seeding
        )

        message(STATUS "Python bindings will be built")
    else()
        message(WARNING "pybind11 not found. Python bindings will not be built.")
        message(WARNING "Install pybind11: pip install pybind11")
    endif()
endif()

# Installation rules
install(TARGETS kmeans_seeding_core
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY include/kmeans_seeding
    DESTINATION include
    FILES_MATCHING PATTERN "*.h" PATTERN "*.hpp"
)

# Testing (optional)
option(BUILD_TESTS "Build C++ tests" OFF)
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# Summary
message(STATUS "")
message(STATUS "========================================")
message(STATUS "kmeans-seeding Configuration Summary")
message(STATUS "========================================")
message(STATUS "  Version:        ${PROJECT_VERSION}")
message(STATUS "  Build type:     ${CMAKE_BUILD_TYPE}")
message(STATUS "  C++ standard:   ${CMAKE_CXX_STANDARD}")
message(STATUS "  OpenMP:         ${OpenMP_CXX_FOUND}")
message(STATUS "  FAISS:          ${faiss_FOUND}")
message(STATUS "  Python:         ${BUILD_PYTHON}")
if(BUILD_PYTHON AND pybind11_FOUND)
message(STATUS "  pybind11:       ${pybind11_VERSION}")
endif()
message(STATUS "  Tests:          ${BUILD_TESTS}")
message(STATUS "========================================")
message(STATUS "")
