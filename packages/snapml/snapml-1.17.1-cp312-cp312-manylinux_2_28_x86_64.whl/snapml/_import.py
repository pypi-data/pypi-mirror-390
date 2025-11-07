# *****************************************************************
#
# Licensed Materials - Property of IBM
#
# (C) Copyright IBM Corp. 2021. All Rights Reserved.
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
#
# ******************************************************************

from importlib import import_module
import warnings
import os
from ctypes import CDLL
import platform
from ctypes.util import find_library

# Try to detect CPU feature flags from NumPy
try:
    from numpy.core._multiarray_umath import __cpu_features__ as cpu_features
except Exception:
    warnings.warn(
        "Cannot detect CPU features info from NumPy; AVX2 will not be used.",
        category=UserWarning,
    )
    cpu_features = None


def import_libutils():
    """Import correct libsnapmlutils variant (ZDNN, AVX2, or generic)."""
    is_s390x = platform.machine() == "s390x"

    if is_s390x:
        lib_override = os.getenv("SNAPML_ZDNN_LIB")
        zdnn_lib = lib_override or find_library("zdnn")

        if zdnn_lib:
            try:
                CDLL(zdnn_lib)
                return import_module("snapml.libsnapmlutils_zdnn")
            except OSError:
                warnings.warn(
                    "Falling back to CPU-only mode. IBM Snap ML will not leverage NNPA.",
                    RuntimeWarning,
                )
        else:
            warnings.warn(
                "Falling back to CPU-only mode. IBM Snap ML will not leverage NNPA.",
                RuntimeWarning,
            )

        return import_module("snapml.libsnapmlutils")

    # Non-s390x: choose AVX2 if supported
    if cpu_features and cpu_features.get("AVX2", False):
        return import_module("snapml.libsnapmlutils_avx2")
    else:
        return import_module("snapml.libsnapmlutils")


def import_libsnapml(mpi_enabled=False):
    """Import correct core Snap ML library variant (ZDNN, AVX2, or generic)."""
    is_s390x = platform.machine() == "s390x"

    if is_s390x:
        lib_override = os.getenv("SNAPML_ZDNN_LIB")
        zdnn_lib = lib_override or find_library("zdnn")
        if zdnn_lib:
            try:
                CDLL(zdnn_lib)
                return import_module("snapml.libsnapmllocal3_zdnn")
            except OSError:
                warnings.warn(
                    "Falling back to CPU-only mode. IBM Snap ML will not leverage NNPA.",
                    RuntimeWarning,
                )
        else:
            warnings.warn(
                "Falling back to CPU-only mode. IBM Snap ML will not leverage NNPA.",
                RuntimeWarning,
            )

        return import_module("snapml.libsnapmllocal3")

    # Non-s390x: choose AVX2 variant if supported
    if cpu_features is not None and cpu_features.get("AVX2", False):
        if mpi_enabled:
            return import_module("snapml.libsnapmlmpi3_avx2")
        else:
            return import_module("snapml.libsnapmllocal3_avx2")
    else:
        if mpi_enabled:
            return import_module("snapml.libsnapmlmpi3")
        else:
            return import_module("snapml.libsnapmllocal3")
