"""
DConfusion - A comprehensive confusion matrix class.

This module maintains backwards compatibility by importing all functionality
from the refactored submodules.
"""

from .core import DConfusionCore
from .metrics import MetricsMixin
from .visualization import VisualizationMixin
from .io import IOMixin


class DConfusion(DConfusionCore, MetricsMixin, VisualizationMixin, IOMixin):
    """
    A comprehensive confusion matrix class for both binary and multi-class classification analysis.

    This class can handle:
    1. Binary classification using individual TP, FN, FP, TN values
    2. Multi-class classification using a confusion matrix or predictions

    Args:
        For binary classification:
            true_positive (int): Number of true positive predictions
            false_negative (int): Number of false negative predictions
            false_positive (int): Number of false positive predictions
            true_negative (int): Number of true negative predictions

        For multi-class classification:
            confusion_matrix (List[List[int]] or np.ndarray): NxN confusion matrix
            labels (List): Optional list of class labels

    Raises:
        ValueError: If any input value is negative or matrix dimensions don't match
        TypeError: If any input value is not a number
    """
    pass