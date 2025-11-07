import sys
import sysconfig

from setuptools import Extension, setup
from Cython.Build import cythonize

# ABI3 example from https://github.com/joerick/python-abi3-package-sample
# Cython docs at
# https://docs.cython.org/en/latest/src/userguide/limited_api.html
#
# Py_LIMITED_API values:
#
# 0x03080000 - Python 3.8 - the minimum version that Cython supports.
# 0x030B0000 - Python 3.11 - support typed memoryviews.
# 0x030C0000 - Python 3.12 - support vectorcall (performance improvement).

py_limited_api_kwargs = {}
bdist_wheel_kwargs = {}
if sys.implementation.name == "cpython" and not sysconfig.get_config_var(
    "Py_GIL_DISABLED"
):
    py_limited_api_kwargs = {
        "define_macros": [
            # For now we are at python 3.8 as we still support 3.10.
            ("Py_LIMITED_API", 0x03080000),
        ],
        "py_limited_api": True,
    }
    bdist_wheel_kwargs = {"py_limited_api": "cp38"}

setup(
    ext_modules=cythonize(
        [
            Extension(
                name="raiser",
                sources=["cython_test_exception_raiser/raiser.pyx"],
                **py_limited_api_kwargs
            ),
        ]
    ),
    options={"bdist_wheel": {**bdist_wheel_kwargs}},
)
