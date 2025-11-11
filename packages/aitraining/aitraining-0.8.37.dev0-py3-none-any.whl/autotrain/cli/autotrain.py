import argparse
import sys

from autotrain import __version__, logger
from autotrain.cli.run_api import RunAutoTrainAPICommand
from autotrain.cli.run_app import RunAutoTrainAppCommand
from autotrain.cli.run_extractive_qa import RunAutoTrainExtractiveQACommand
from autotrain.cli.run_image_classification import RunAutoTrainImageClassificationCommand
from autotrain.cli.run_image_regression import RunAutoTrainImageRegressionCommand
from autotrain.cli.run_llm import RunAutoTrainLLMCommand
from autotrain.cli.run_object_detection import RunAutoTrainObjectDetectionCommand
from autotrain.cli.run_sent_tranformers import RunAutoTrainSentenceTransformersCommand
from autotrain.cli.run_seq2seq import RunAutoTrainSeq2SeqCommand
from autotrain.cli.run_setup import RunSetupCommand
from autotrain.cli.run_spacerunner import RunAutoTrainSpaceRunnerCommand
from autotrain.cli.run_tabular import RunAutoTrainTabularCommand
from autotrain.cli.run_text_classification import RunAutoTrainTextClassificationCommand
from autotrain.cli.run_text_regression import RunAutoTrainTextRegressionCommand
from autotrain.cli.run_token_classification import RunAutoTrainTokenClassificationCommand
from autotrain.cli.run_tools import RunAutoTrainToolsCommand
from autotrain.cli.run_tui import RunAutoTrainTUICommand
from autotrain.cli.run_vlm import RunAutoTrainVLMCommand
from autotrain.parser import AutoTrainConfigParser


ASCII_BANNER = r"""
    ___    ____  ______           _       _
   / _ |  /  _/ /_  __/______ _  (_)___  (_)__  ___ _
  / __ | _/ /    / / / __/ _ `/ / / _ \/ / _ \/ _ `/
 /_/ |_|/___/   /_/ /_/  \_,_/ /_/_//_/_/_//_/\_, /
                                             /___/
           Advanced Machine Learning Training Platform
"""

WELCOME_MESSAGE = """
Welcome to AITraining! Get started with:

  • aitraining llm --help          Show all LLM training options
  • aitraining tui                 Launch interactive configuration UI
  • aitraining llm --train         Start training with your config

Quick Examples:

  # Train with grouped parameters
  aitraining llm --trainer sft --help

  # Train with specific trainer
  aitraining llm --train --model gpt2 --data-path ./data --trainer sft

  # Fine-tune with LoRA
  aitraining llm --train --model meta-llama/Llama-2-7b --peft --lora-r 16

For detailed documentation, visit: https://github.com/huggingface/autotrain-advanced
"""


def main():
    parser = argparse.ArgumentParser(
        "AITraining advanced CLI",
        usage="aitraining <command> [<args>]",
        epilog="For more information about a command, run: `aitraining <command> --help`",
    )
    parser.add_argument("--version", "-v", help="Display AITraining version", action="store_true")
    parser.add_argument("--config", help="Optional configuration file", type=str)
    commands_parser = parser.add_subparsers(help="commands")

    # Register commands
    RunAutoTrainAppCommand.register_subcommand(commands_parser)
    RunAutoTrainTUICommand.register_subcommand(commands_parser)
    RunAutoTrainLLMCommand.register_subcommand(commands_parser)
    RunSetupCommand.register_subcommand(commands_parser)
    RunAutoTrainAPICommand.register_subcommand(commands_parser)
    RunAutoTrainTextClassificationCommand.register_subcommand(commands_parser)
    RunAutoTrainImageClassificationCommand.register_subcommand(commands_parser)
    RunAutoTrainTabularCommand.register_subcommand(commands_parser)
    RunAutoTrainSpaceRunnerCommand.register_subcommand(commands_parser)
    RunAutoTrainSeq2SeqCommand.register_subcommand(commands_parser)
    RunAutoTrainTokenClassificationCommand.register_subcommand(commands_parser)
    RunAutoTrainToolsCommand.register_subcommand(commands_parser)
    RunAutoTrainTextRegressionCommand.register_subcommand(commands_parser)
    RunAutoTrainObjectDetectionCommand.register_subcommand(commands_parser)
    RunAutoTrainSentenceTransformersCommand.register_subcommand(commands_parser)
    RunAutoTrainImageRegressionCommand.register_subcommand(commands_parser)
    RunAutoTrainExtractiveQACommand.register_subcommand(commands_parser)
    RunAutoTrainVLMCommand.register_subcommand(commands_parser)

    args = parser.parse_args()

    if args.version:
        print(__version__)
        exit(0)

    if args.config:
        logger.info(f"Using AITraining configuration: {args.config}")
        cp = AutoTrainConfigParser(args.config)
        cp.run()
        exit(0)

    if not hasattr(args, "func"):
        # Show ASCII banner and welcome message when no command is provided
        if sys.stdout.isatty():  # Only show in terminal, not when piped
            print(ASCII_BANNER)
            print(WELCOME_MESSAGE)
        else:
            # When piped, just show help
            parser.print_help()
        exit(1)

    command = args.func(args)
    command.run()


if __name__ == "__main__":
    main()
