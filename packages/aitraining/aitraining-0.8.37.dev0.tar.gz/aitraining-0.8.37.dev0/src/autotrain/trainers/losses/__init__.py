"""
Custom Loss Functions for AutoTrain Advanced
=============================================

Provides flexible loss functions inspired by Tinker's approach.
"""

from .custom_loss import CustomLoss, CustomLossConfig
from .variance_loss import VarianceLoss, variance_regularization
from .kl_loss import KLDivergenceLoss, compute_kl_penalty
from .importance_sampling import ImportanceSamplingLoss
from .ppo_loss import PPOLoss, compute_ppo_loss

__all__ = [
    "CustomLoss",
    "CustomLossConfig",
    "VarianceLoss",
    "variance_regularization",
    "KLDivergenceLoss",
    "compute_kl_penalty",
    "ImportanceSamplingLoss",
    "PPOLoss",
    "compute_ppo_loss",
]