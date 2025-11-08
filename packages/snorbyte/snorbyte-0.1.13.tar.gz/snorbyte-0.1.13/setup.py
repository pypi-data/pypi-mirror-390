from setuptools import setup, find_packages
from Cython.Build import cythonize

# compile all .pyx under snorbyte
ext_modules = cythonize(
    ["snorbyte/*.pyx"],
    compiler_directives={"language_level": "3"},
)

setup(
    # name/version/metadata come from setup.cfg
    packages=find_packages(),
    ext_modules=ext_modules,
    include_package_data=True,
    zip_safe=False,
)
