# __init__.py

from .Vigenere import Vigenere
from .DataAnalysis import normalise, split
from .Mowie import Mowie

# Import the subpackage
from . import TnOComputeEngine

__all__ = [
    "Vigenere",
    "normalise",
    "split",
    "Mowie",
    "AutoML",
    "preprocess_data",
    "select_model",
    "tune_model",
    "evaluate_model",
    "save_model",
    "load_model",
    "TnOComputeEngine",  # Now the subpackage is available
]
