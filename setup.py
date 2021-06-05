import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

MIN_PYTHON_VERSION = "3.6"
MIN_REQUIREMENTS = {
    "numpy": "1.19.0",
    "pandas": "1.1.0",
    "scikit-learn": "0.23.0",
    "statsmodels": "0.12.1",
    "numba": "0.50",
    "tqdm": "4.10.0",
    "sktime": "0.5.3",
    "xgboost":"1.3.3",
    "mass-ts":"0.1.4",
}

EXTRAS_REQUIRE = {
    "all_extras": [
        "cython>=0.29.0",
        "matplotlib>=3.3.2",
        "pmdarima>=1.8.0",
        "scikit_posthocs>= 0.6.5",
        "seaborn>=0.11.0",
        "tsfresh>=0.17.0",
        "catch22>=0.2.0",
        "hcrystalball>=0.1.9",
        "stumpy>=1.5.1",
        "tbats>=1.1.0",
        "fbprophet>=0.7.1",
    ],
}

INSTALL_REQUIRES = [
    *[
        "{}>={}".format(package, version)
        for package, version in MIN_REQUIREMENTS.items()
    ],
    "wheel",
]

CLASSIFIERS = [
    "Intended Audience :: Science/Research",
    "Intended Audience :: Developers",
    "License :: OSI Approved",
    "Programming Language :: Python",
    "Topic :: Software Development",
    "Topic :: Scientific/Engineering",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Operating System :: MacOS",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
]

SETUP_REQUIRES = ["wheel"]

setuptools.setup(
    name="skshapelet",
    version="1.0.2",
    author="Miao Cai",
    author_email="philliphily@gmail.com",
    description="Time Series Shapelets Transformation",
    license="BSD-3-Clause",
    long_description=long_description,
    url="https://github.com/Hephaest/skshapelet",
    packages=setuptools.find_packages(),
    classifiers=CLASSIFIERS,
    setup_requires=SETUP_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
)