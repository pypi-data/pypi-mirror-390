"""
Setup script for kmeans-seeding package.

This uses CMake to build the C++ extension module.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    """Extension that is built using CMake."""

    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    """Build extension using CMake."""

    def build_extension(self, ext):
        if not isinstance(ext, CMakeExtension):
            return super().build_extension(ext)

        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        # Create build directory
        build_temp = Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)

        # CMake configuration arguments
        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            "-DBUILD_PYTHON=ON",
            "-DBUILD_TESTS=OFF",
        ]

        # Build type
        cfg = os.environ.get("CMAKE_BUILD_TYPE", "Release")
        cmake_args.append(f"-DCMAKE_BUILD_TYPE={cfg}")

        # Build arguments
        build_args = ["--config", cfg]

        # Set parallel build level
        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            # Use number of CPUs available
            import multiprocessing
            parallel_level = max(1, multiprocessing.cpu_count() - 1)
            build_args.extend(["--parallel", str(parallel_level)])

        # Platform-specific configuration
        if sys.platform.startswith("darwin"):
            # macOS: Detect architecture
            archs = os.environ.get("ARCHFLAGS", "")
            if "arm64" in archs:
                cmake_args.append("-DCMAKE_OSX_ARCHITECTURES=arm64")
            elif "x86_64" in archs:
                cmake_args.append("-DCMAKE_OSX_ARCHITECTURES=x86_64")

            # Try to find OpenMP on macOS
            if Path("/usr/local/opt/libomp").exists():
                cmake_args.extend([
                    "-DOpenMP_C_FLAGS=-Xpreprocessor -fopenmp -I/usr/local/opt/libomp/include",
                    "-DOpenMP_CXX_FLAGS=-Xpreprocessor -fopenmp -I/usr/local/opt/libomp/include",
                    "-DOpenMP_omp_LIBRARY=/usr/local/opt/libomp/lib/libomp.dylib",
                ])

        elif sys.platform.startswith("win"):
            # Windows: Use Visual Studio generator
            cmake_args.extend([
                "-G", "Visual Studio 16 2019" if sys.version_info >= (3, 8) else "Visual Studio 15 2017",
            ])

        # Try to find FAISS
        conda_prefix = os.environ.get("CONDA_PREFIX")
        if conda_prefix:
            cmake_args.append(f"-DCMAKE_PREFIX_PATH={conda_prefix}")

        # Run CMake configure
        print(f"Running CMake configure...")
        print(f"  Source dir: {ext.sourcedir}")
        print(f"  Build dir: {self.build_temp}")
        print(f"  CMake args: {' '.join(cmake_args)}")

        subprocess.check_call(
            ["cmake", f"{ext.sourcedir}/cpp"] + cmake_args,
            cwd=self.build_temp
        )

        # Run CMake build
        print(f"Running CMake build...")
        print(f"  Build args: {' '.join(build_args)}")

        subprocess.check_call(
            ["cmake", "--build", "."] + build_args,
            cwd=self.build_temp
        )

        # Copy the built extension to the right place
        # The extension is built in build_temp/kmeans_seeding/_core.so (or _core.*.so on some platforms)
        built_ext = list(Path(self.build_temp).rglob("_core.*.so"))
        if not built_ext:
            # Try .dylib for macOS, .pyd for Windows
            built_ext = list(Path(self.build_temp).rglob("_core.*.dylib"))
        if not built_ext:
            built_ext = list(Path(self.build_temp).rglob("_core.*.pyd"))

        if built_ext:
            # Filter out directories (only want files)
            built_ext = [f for f in built_ext if f.is_file()]

        if built_ext:
            src = built_ext[0]
            dst = Path(extdir) / src.name
            print(f"Copying {src} -> {dst}")
            shutil.copy2(src, dst)
        else:
            print("Warning: Could not find built extension module")


# Read version from __init__.py
def get_version():
    init_file = Path(__file__).parent / "python" / "kmeans_seeding" / "__init__.py"
    for line in init_file.read_text().splitlines():
        if line.startswith("__version__"):
            return line.split('"')[1]
    return "0.0.0"


setup(
    name="kmeans-seeding",
    version=get_version(),
    ext_modules=[CMakeExtension("kmeans_seeding._core")],
    cmdclass={"build_ext": CMakeBuild},
    zip_safe=False,
)
