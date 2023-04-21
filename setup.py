import numpy as np
from Cython.Build import cythonize
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

VERSION = "0.0.1"


# Avoid a gcc warning below:
# cc1plus: warning: command line option ‘-Wstrict-prototypes’ is valid for C/ObjC but not for C++
class BuildExt(build_ext):
    def build_extensions(self):
        if "-Wstrict-prototypes" in self.compiler.compiler_so:
            self.compiler.compiler_so.remove("-Wstrict-prototypes")
        super().build_extensions()


ext_modules = [
    Extension(
        name=str("adapt._c_llr_segmentation"),
        sources=[str("adapt/_c_llr_segmentation.pyx")],
        include_dirs=[np.get_include()],
        language="c++",
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    )
]

for e in ext_modules:
    e.cython_directives = {"embedsignature": True}


setup(
    name="ADAPT",
    version=VERSION,
    packages=["adapt"],
    install_requires=[
        "numpy==1.22",
        "ont-fast5-api>=4",
        "pandas",
    ],
    author="Wiep van der Toorn",
    author_email="w.vandertoorn@fu-berlin.de",
    description="Adapter detection in direct RNA sequencing reads.",
    license="CC BY-SA 4.0",
    keywords="dRNA-seq nanopore adapter correction",
    url="https://github.com/wvandertoorn/ADAPT",
    entry_points={"console_scripts": ["adapt = adapt.__main__:main"]},
    include_package_data=True,
    ext_modules=cythonize(ext_modules, language_level="3"),
    cmdclass={"build_ext": BuildExt},
    test_suite="pytest",
    tests_require=["pytest"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython,"
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Typing :: Typed",
    ],
)
