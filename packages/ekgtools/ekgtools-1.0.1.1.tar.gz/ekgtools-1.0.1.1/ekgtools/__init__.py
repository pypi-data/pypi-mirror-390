from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ekgtools")
except PackageNotFoundError:
    __version__ = "0.0.0"

# Bring top-level API into the package namespace
from .dataset import ECGDataset
from .parser import ECGParser
from .plot import plot, plot_one

__all__ = [
    "ECGDataset",
    "ECGParser",
    "plot",
    "plot_one",
    "__version__",
]
