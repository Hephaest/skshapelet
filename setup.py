# adapted from https://github.com/Hephaest/sktime/blob/master/setup.py
import os
import platform
import sktime
import shutil
import sys
from distutils.command.clean import clean as Clean  # noqa
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
}

EXTRAS_REQUIRE = {
    "all_extras": [
        "cython>=0.29.0",
        "matplotlib>=3.3.2",
        "pmdarima>=1.8.0",
        "seaborn>=0.11.0",
        "tsfresh>=0.17.0",
        "catch22>=0.2.0",
        "stumpy>=1.5.1",
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

# Optional setuptools features
# For some commands, use setuptools
SETUPTOOLS_COMMANDS = {
    "install",
    "develop",
    "release",
    "build_ext",
    "bdist_egg",
    "bdist_rpm",
    "bdist_wininst",
    "install_egg_info",
    "build_sphinx",
    "egg_info",
    "easy_install",
    "upload",
    "bdist_wheel",
    "--single-version-externally-managed",
    "sdist",
}

if SETUPTOOLS_COMMANDS.intersection(sys.argv):
    # We need to import setuptools early, if we want setuptools features,
    # (e.g. "bdist_wheel") as it monkey-patches the 'setup' function
    import setuptools  # noqa

    extra_setuptools_args = dict(
        zip_safe=False,  # the package can run out of an .egg file
        include_package_data=True,
    )

else:
    extra_setuptools_args = dict()


# Custom clean command to remove build artifacts
class CleanCommand(Clean):
    description = "Remove build artifacts from the source tree"

    def run(self):
        Clean.run(self)

        # Remove c files if we are not within a sdist package
        cwd = os.path.abspath(os.path.dirname(__file__))
        remove_c_files = not os.path.exists(os.path.join(cwd, "PKG-INFO"))
        if remove_c_files:
            print("Will remove generated .c files")  # noqa: T001
        if os.path.exists("build"):
            shutil.rmtree("build")
        for dirpath, dirnames, filenames in os.walk("skshapelet"):
            for filename in filenames:
                if any(
                    filename.endswith(suffix)
                    for suffix in (".so", ".pyd", ".dll", ".pyc")
                ):
                    os.unlink(os.path.join(dirpath, filename))
                    continue
                extension = os.path.splitext(filename)[1]
                if remove_c_files and extension in [".c", ".cpp"]:
                    pyx_file = str.replace(filename, extension, ".pyx")
                    if os.path.exists(os.path.join(dirpath, pyx_file)):
                        os.unlink(os.path.join(dirpath, filename))
            for dirname in dirnames:
                if dirname == "__pycache__":
                    shutil.rmtree(os.path.join(dirpath, dirname))


cmdclass = {"clean": CleanCommand }

# custom build_ext command to set OpenMP compile flags depending on os and
# compiler
# build_ext has to be imported after setuptools
try:
    from numpy.distutils.command.build_ext import build_ext  # noqa

    class build_ext_subclass(build_ext):
        def build_extensions(self):
            from skshapelet._build_utils.openmp_helpers import get_openmp_flag

            if not os.getenv("SKTIME_NO_OPENMP"):
                openmp_flag = get_openmp_flag(self.compiler)

                for e in self.extensions:
                    e.extra_compile_args += openmp_flag
                    e.extra_link_args += openmp_flag

            build_ext.build_extensions(self)

    cmdclass["build_ext"] = build_ext_subclass

except ImportError:
    # Numpy should not be a dependency just to be able to introspect
    # that python 3.6 is required.
    pass

def setup_package():
    metadata = dict(
        name="skshapelet",
        version="1.1.0",
        author="Miao Cai",
        author_email="philliphily@gmail.com",
        description="Time Series Shapelets Transformation",
        license="BSD-3-Clause",
        long_description=long_description,
        url="https://github.com/Hephaest/skshapelet",
        packages=setuptools.find_packages(),
        classifiers=CLASSIFIERS,
        cmdclass=cmdclass,
        python_requires=">={}".format(MIN_PYTHON_VERSION),
        setup_requires=SETUP_REQUIRES,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        **extra_setuptools_args
    )

    # For these actions, NumPy is not required
    # They are required to succeed without Numpy for example when
    # pip is used to install skshapelet when Numpy is not yet
    # present in the system.
    if len(sys.argv) == 1 or (
        len(sys.argv) >= 2
        and (
            "--help" in sys.argv[1:]
            or sys.argv[1] in ("--help-commands", "egg_info", "--version", "clean")
        )
    ):
        try:
            from setuptools import setup
        except ImportError:
            from distutils.core import setup

    # otherwise check Python and required package versions
    else:
        if sys.version_info < tuple([int(i) for i in MIN_PYTHON_VERSION.split(".")]):
            raise RuntimeError(
                "skshapelet requires Python %s or later. The current"
                " Python version is %s installed in %s."
                % (MIN_PYTHON_VERSION, platform.python_version(), sys.executable)
            )

        from numpy.distutils.core import setup

    setup(**metadata)


if __name__ == "__main__":
    setup_package()