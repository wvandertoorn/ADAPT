import numpy as np
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from setuptools import Extension, setup

VERSION = "0.0.1"
    
ext_modules = [
    Extension(name=str("adapt._c_llr_segmentation"),
              sources=[str("adapt/_c_llr_segmentation.pyx")],
              include_dirs=[np.get_include()],
              language="c++")
]

for e in ext_modules:
    e.cython_directives = {"embedsignature": True}


setup(
    name = "ADAPT",
    version = VERSION,
    packages = ['adapt'],
    install_requires = ['numpy', 'ont-fast5-api>=4', 'pandas', 'setuptools'],
    author = "Wiep van der Toorn",
    author_email = "w.vandertoorn@fu-berlin.de",
    description='Adapter detection in direct RNA sequencing reads.',
    # license = "mpl-2.0",
    keywords = "dRNA-seq nanopore adapter correction",
    url = "https://github.com/wvandertoorn/ADAPT",
    entry_points={
        'console_scripts': [
            'adapt = adapt.__main__:main'
        ]
    },
    include_package_data=True,
    ext_modules=cythonize(ext_modules),
    cmdclass={'build_ext': build_ext},
    test_suite='pytest',
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        # 'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython,'
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ]
)