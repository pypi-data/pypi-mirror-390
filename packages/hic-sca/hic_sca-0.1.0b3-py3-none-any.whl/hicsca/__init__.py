"""
HiC-SCA: Hi-C Spectral Compartment Assignment

A Python package for analyzing Hi-C data to predict A-B chromosomal compartments
using spectral decomposition and observed/expected normalization.
"""

from .hicsca import (
    HiCDataLoader,
    BackgroundNormalizer,
    LowCoverageFilter,
    EigenDecomposer,
    CompartmentAssigner,
    HiCSCA
)

# Import submodules for hicsca.eval and hicsca.formats access
from . import evals
from . import formats

__version__ = "0.1.0"
__all__ = [
    "HiCDataLoader",
    "BackgroundNormalizer",
    "LowCoverageFilter",
    "EigenDecomposer",
    "CompartmentAssigner",
    "HiCSCA",
    "evals",
    "formats"
]