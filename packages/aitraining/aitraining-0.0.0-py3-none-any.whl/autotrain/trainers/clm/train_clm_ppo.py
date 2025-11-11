"""
PPO Training for AutoTrain Advanced
====================================

Proximal Policy Optimization (PPO) trainer integration for CLI.
Uses TRL's PPOTrainer for consistency with other trainers.

Requirements:
- A trained reward model (via --rl-reward-model-path or --model-ref)
- Reward model validation happens at config time, not training time
"""

import torch
from peft import LoraConfig
from transformers.trainer_callback import PrinterCallback
from trl import PPOConfig, PPOTrainer, AutoModelForCausalLMWithValueHead
from trl.core import LengthSampler

from autotrain import logger
from autotrain.trainers.clm import utils
from autotrain.trainers.clm.params import LLMTrainingParams
from autotrain.trainers.clm.sweep_utils import with_sweep


@with_sweep
def train(config):
    """PPO training entry point for AutoTrain CLI."""
    logger.info("Starting PPO training...")

    if isinstance(config, dict):
        config = LLMTrainingParams(**config)

    # NOTE: RL environment customization (rl_env_type, rl_env_config, rl_multi_objective)
    # is not yet implemented. The parameters exist but are not wired to the PPO trainer.
    # Currently uses TRL's default PPO behavior.
    # See trainers/rl/environments.py for prepared implementations.

    # Note: Reward model validation now happens at config validation time
    # See params.py::validate_ppo_requirements()
    logger.info("PPO training initialized. Using reward model from: %s",
                config.rl_reward_model_path or config.model_ref)

    # Load data and tokenizer
    train_data, valid_data = utils.process_input_data(config)

    # Validate required columns
    utils.validate_required_columns(
        train_data,
        [config.text_column],
        "PPO",
        "training"
    )
    # PPO doesn't use validation data but check if provided
    if valid_data is not None:
        logger.info("Note: PPO trainer doesn't use validation data, but it was provided")

    tokenizer = utils.get_tokenizer(config)
    train_data, valid_data = utils.process_data_with_chat_template(config, tokenizer, train_data, valid_data)

    # Configure training args similar to other trainers
    logging_steps = utils.configure_logging_steps(config, train_data, valid_data)
    training_args = utils.configure_training_args(config, logging_steps)
    config = utils.configure_block_size(config, tokenizer)

    # PPO specific configuration
    training_args["learning_rate"] = config.lr
    training_args["batch_size"] = config.batch_size
    training_args["num_ppo_epochs"] = getattr(config, 'rl_num_ppo_epochs', 4)
    training_args["mini_batch_size"] = getattr(config, 'rl_mini_batch_size', 1)
    training_args["gradient_accumulation_steps"] = config.gradient_accumulation
    # Disable bf16 if not supported
    training_args["bf16"] = False
    training_args["fp16"] = False
    # PPO hyperparameters
    training_args["kl_coef"] = getattr(config, 'rl_kl_coef', 0.1)
    training_args["gamma"] = getattr(config, 'rl_gamma', 0.99)
    training_args["lam"] = getattr(config, 'rl_gae_lambda', 0.95)
    training_args["cliprange"] = getattr(config, 'rl_clip_range', 0.2)
    training_args["cliprange_value"] = getattr(config, 'rl_value_clip_range', 0.2)
    training_args["vf_coef"] = getattr(config, 'rl_value_loss_coef', 1.0)
    training_args["max_grad_norm"] = config.max_grad_norm

    # Generation parameters for PPO sampling
    generation_kwargs = {
        "min_length": -1,
        "max_new_tokens": getattr(config, 'rl_max_new_tokens', 256),
        "top_k": getattr(config, 'rl_top_k', 0),
        "top_p": getattr(config, 'rl_top_p', 1.0),
        "do_sample": True,
        "temperature": getattr(config, 'rl_temperature', 1.0),
        "pad_token_id": tokenizer.pad_token_id,
        "eos_token_id": tokenizer.eos_token_id,
    }

    # Create PPO config
    # Disable evaluation if no validation data
    training_args["do_eval"] = valid_data is not None
    if valid_data is None:
        training_args["eval_strategy"] = "no"
        # Disable sample generation which requires eval_dataloader
        training_args["num_sample_generations"] = 0
    ppo_config = PPOConfig(
        **training_args,
        # log_with="tensorboard",  # Not supported in current version
        # project_kwargs={"logging_dir": config.project_name},
    )

    # Load models
    model = utils.get_model(config, tokenizer)

    # Configure PEFT if needed
    peft_config = None
    if config.peft:
        peft_config = LoraConfig(
            r=config.lora_r,
            lora_alpha=config.lora_alpha,
            lora_dropout=config.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=utils.get_target_modules(config),
        )

    # For PPO, we need a reference model
    # If using PEFT, ref_model should be None
    # Otherwise, we need a deep copy of the model
    if peft_config is not None:
        ref_model = None
    else:
        import copy
        ref_model = copy.deepcopy(model)

    # Prepare dataset for PPO (needs to return tokenized queries)
    # PPO expects tokenized prompts/queries to generate from
    def prepare_dataset(dataset):
        def tokenize_queries(examples):
            # Get the text column to use
            text_col = config.text_column if config.text_column in dataset.column_names else "text"
            # Truncate to half block size to leave room for generation
            queries = [text[:config.block_size // 2] for text in examples[text_col]]
            # Tokenize the queries
            return tokenizer(queries, truncation=True, max_length=config.block_size // 2, padding=False)

        return dataset.map(tokenize_queries, batched=True, remove_columns=dataset.column_names)

    train_dataset = prepare_dataset(train_data)

    # Create reward model or use simple reward function
    # For now, use a simple length-based reward as default
    def reward_fn(samples):
        """Simple reward function for demonstration."""
        rewards = []
        for sample in samples:
            # Reward shorter, coherent responses
            text = tokenizer.decode(sample, skip_special_tokens=True)
            length_penalty = -0.01 * max(0, len(text.split()) - 50)
            coherence_bonus = 0.5 if any(p in text for p in '.!?') else 0.0
            rewards.append(length_penalty + coherence_bonus)
        return rewards

    # If a reward model path is provided, load it
    reward_model = None
    reward_model_path = config.rl_reward_model_path or config.model_ref

    if reward_model_path:
        from transformers import AutoModelForSequenceClassification, AutoConfig
        from autotrain.utils import get_model_loading_kwargs, maybe_move_to_mps

        logger.info(f"Loading reward model from {reward_model_path}")

        # Load reward model config first to ensure num_labels is set
        reward_config = AutoConfig.from_pretrained(reward_model_path, token=config.token)

        # Ensure pad_token is set in config to match tokenizer
        reward_config.pad_token_id = tokenizer.pad_token_id

        # Use existing utilities for device handling
        reward_kwargs = get_model_loading_kwargs(token=config.token, fp16_if_cuda=False, trust_remote_code=True)
        reward_model = AutoModelForSequenceClassification.from_pretrained(
            reward_model_path,
            config=reward_config,
            **reward_kwargs
        )
        reward_model = maybe_move_to_mps(reward_model, reward_kwargs)
        reward_model.eval()

        # Create reward function using the model (backup, not used by PPOTrainer)
        def reward_fn(samples):
            with torch.no_grad():
                inputs = tokenizer(
                    samples,
                    padding=True,
                    truncation=True,
                    return_tensors="pt",
                    pad_to_multiple_of=8
                )
                # Move inputs to same device as reward model
                device = next(reward_model.parameters()).device
                inputs = {k: v.to(device) for k, v in inputs.items()}
                outputs = reward_model(**inputs)
                logits = outputs.logits.squeeze()
                # Handle both single sample and batch
                if logits.dim() == 0:
                    return [logits.cpu().item()]
                return logits.cpu().tolist()

    # Create PPO trainer with required arguments
    callbacks = utils.get_callbacks(config)

    # Set up custom metrics via callbacks if specified
    # PPO doesn't support compute_metrics directly, so we use callbacks
    if hasattr(config, 'custom_metrics') and config.custom_metrics:
        # Parse custom metrics list from config
        if isinstance(config.custom_metrics, str):
            import json
            custom_metrics_list = json.loads(config.custom_metrics)
        else:
            custom_metrics_list = config.custom_metrics

        logger.info(f"Setting up custom metrics for PPO via callbacks: {custom_metrics_list}")

        # Use the generic CustomMetricsCallback that handles ANY metric
        from autotrain.trainers.common_metrics import CustomMetricsCallback
        metrics_callback = CustomMetricsCallback(custom_metrics_list, tokenizer=tokenizer)
        callbacks.append(metrics_callback)
        logger.info(f"Added CustomMetricsCallback for PPO with metrics: {custom_metrics_list}")

    # Create value model by wrapping the base model with a value head
    # This works with any causal LM model (GPT-2, LLaMA, etc.)
    value_model = AutoModelForCausalLMWithValueHead.from_pretrained(
        config.model,
        token=config.token,
        trust_remote_code=getattr(config, 'trust_remote_code', False),
    )

    # Move value model to same device as main model
    device = next(model.parameters()).device
    value_model = value_model.to(device)

    # Fix compatibility with PPOTrainer
    # PPOTrainer expects to access the base model through base_model_prefix attribute
    # Set base_model_prefix to 'pretrained_model' since that's where the actual model is
    value_model.base_model_prefix = 'pretrained_model'

    # Also create a direct reference to pretrained_model's transformer if it exists
    # This handles cases where PPOTrainer might look for nested attributes
    if hasattr(value_model, 'pretrained_model'):
        if hasattr(value_model.pretrained_model, 'transformer'):
            value_model.transformer = value_model.pretrained_model.transformer
        elif hasattr(value_model.pretrained_model, 'model'):
            value_model.model = value_model.pretrained_model.model

    # Add score method to value_model for PPOTrainer compatibility
    # PPOTrainer's get_reward function expects this method
    def value_score_method(self, hidden_states):
        """Score method expected by TRL's PPOTrainer for value model."""
        # AutoModelForCausalLMWithValueHead has a v_head that computes values
        if hasattr(self, 'v_head'):
            return self.v_head(hidden_states)
        else:
            # Fallback - this shouldn't happen with AutoModelForCausalLMWithValueHead
            raise AttributeError("Value model doesn't have v_head for scoring")

    # Bind the score method to the value model instance
    value_model.score = value_score_method.__get__(value_model, type(value_model))

    # Prepare eval dataset if validation data exists
    eval_dataset = None
    if valid_data is not None:
        eval_dataset = prepare_dataset(valid_data)

    ppo_trainer = PPOTrainer(
        args=ppo_config,  # Changed from config to args
        model=model,
        ref_model=ref_model,
        reward_model=reward_model,  # Now a required argument
        train_dataset=train_dataset,  # Now a required argument
        eval_dataset=eval_dataset,  # Only pass eval dataset if we have validation data
        value_model=value_model,  # Proper value model with value head
        processing_class=tokenizer,  # Changed from tokenizer to processing_class
        peft_config=peft_config,
        callbacks=callbacks,
        # PPOTrainer doesn't support compute_metrics - use callbacks instead
    )

    ppo_trainer.remove_callback(PrinterCallback)

    # Training loop - Use TRL's train() method
    logger.info("Starting PPO training...")

    # In newer TRL versions, PPOTrainer uses the standard train() method
    ppo_trainer.train()

    # Save final model
    utils.post_training_steps(config, ppo_trainer)

    return ppo_trainer
