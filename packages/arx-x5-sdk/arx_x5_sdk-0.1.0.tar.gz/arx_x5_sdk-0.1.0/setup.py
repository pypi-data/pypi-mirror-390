"""Setup script for ARX SDK Python extension."""

import shutil
import subprocess
from pathlib import Path

from setuptools import setup
from setuptools.command.build import build
from setuptools.command.install import install


class BuildArxSDK(build):
    """Build the ARX SDK extension using CMake."""

    def run(self):
        import sys
        import sysconfig

        this_dir = Path(__file__).parent.absolute()
        build_dir = this_dir / "build"
        build_dir.mkdir(exist_ok=True)

        # Pass Python executable and paths to CMake to force it to use the correct Python
        python_include = sysconfig.get_path("include")
        python_lib = sysconfig.get_config_var("LIBDIR")
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

        # Use shutil.which to get full paths (addresses Bandit B607)
        cmake_path = shutil.which("cmake")
        make_path = shutil.which("make")
        if not cmake_path:
            raise RuntimeError("Could not find 'cmake' in PATH")
        if not make_path:
            raise RuntimeError("Could not find 'make' in PATH")

        # CMake will find pybind11 via find_package(pybind11 REQUIRED)
        # We don't need to import pybind11 in Python - CMake handles it
        # Try to find pybind11's location to help CMake, but don't fail if we can't
        cmake_prefix_path = None
        pybind11_dir = None
        try:
            import pybind11

            pybind11_path = Path(pybind11.__file__).parent
            # Try to find pybind11 CMake files
            pybind11_cmake_path = pybind11_path.parent / "share" / "cmake" / "pybind11"
            if not pybind11_cmake_path.exists():
                pybind11_cmake_path = pybind11_path / "share" / "cmake" / "pybind11"
            if pybind11_cmake_path.exists():
                pybind11_dir = str(pybind11_cmake_path)
            cmake_prefix_path = str(pybind11_path.parent)
        except ImportError:
            # pybind11 not importable, but CMake might still find it
            # This is OK - CMake's find_package will handle it
            pass

        cmake_args = [
            cmake_path,
            "..",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DPython3_EXECUTABLE={sys.executable}",
            f"-DPython3_INCLUDE_DIR={python_include}",
            f"-DPython3_LIBRARY_DIR={python_lib}",
            f"-DPython3_VERSION={python_version}",
            "-DPYBIND11_FINDPYTHON=OFF",  # Disable pybind11's Python finding, use our manual setup
        ]

        # Add pybind11 hints if we found them, but CMake should find it anyway
        if pybind11_dir:
            cmake_args.append(f"-Dpybind11_DIR={pybind11_dir}")
        if cmake_prefix_path:
            cmake_args.append(f"-DCMAKE_PREFIX_PATH={cmake_prefix_path}")
        subprocess.check_call(cmake_args, cwd=build_dir)
        subprocess.check_call([make_path], cwd=build_dir)
        subprocess.check_call([make_path, "install"], cwd=build_dir)

        super().run()


class InstallArxSDK(install):
    """Install the ARX SDK extension."""

    def run(self):
        # CMake already installed everything to arx_x5_sdk/, 
        # so we just run the standard install
        super().run()


setup(
    name="arx-x5-sdk",
    version="0.1.0",
    author="Remi Cadene, UMA",
    description="ARX X5 Robot Arm Python SDK",
    long_description="Python bindings for ARX X5 robot arm SDK",
    packages=["arx_x5_sdk"],
    package_dir={"arx_x5_sdk": "arx_x5_sdk"},
    package_data={"arx_x5_sdk": ["urdf/*.urdf"]},
    cmdclass={"build": BuildArxSDK, "install": InstallArxSDK},
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=["pybind11>=2.10.0"],
)
