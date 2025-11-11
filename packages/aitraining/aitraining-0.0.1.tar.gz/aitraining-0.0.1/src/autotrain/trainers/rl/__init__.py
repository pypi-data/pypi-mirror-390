"""
AutoTrain Advanced Reinforcement Learning Module
================================================

Implements advanced training methods inspired by Tinker's approaches:
- PPO (Proximal Policy Optimization) for LLMs
- DPO (Direct Preference Optimization)
- RLHF (Reinforcement Learning from Human Feedback)
- Custom reward modeling
- Async forward-backward training pipeline
"""

from .ppo import PPOTrainer, PPOConfig
from .dpo import DPOTrainer, DPOConfig
from .reward_model import (
    RewardModel,
    RewardModelConfig,
    PairwiseRewardModel,
    MultiObjectiveRewardModel,
    RewardModelTrainer,
)
from .environments import (
    TextGenerationEnv,
    MultiObjectiveRewardEnv,
    PreferenceComparisonEnv,
    create_math_problem_env,
    create_code_generation_env,
)
from .forward_backward import (
    ForwardBackwardPipeline,
    AsyncTrainingFuture,
    ForwardBackwardOutput,
    OptimStepOutput,
)

__all__ = [
    # PPO
    "PPOTrainer",
    "PPOConfig",
    # DPO
    "DPOTrainer",
    "DPOConfig",
    # Reward Models
    "RewardModel",
    "RewardModelConfig",
    "PairwiseRewardModel",
    "MultiObjectiveRewardModel",
    "RewardModelTrainer",
    # Environments
    "TextGenerationEnv",
    "MultiObjectiveRewardEnv",
    "PreferenceComparisonEnv",
    "create_math_problem_env",
    "create_code_generation_env",
    # Forward-Backward Pipeline
    "ForwardBackwardPipeline",
    "AsyncTrainingFuture",
    "ForwardBackwardOutput",
    "OptimStepOutput",
]