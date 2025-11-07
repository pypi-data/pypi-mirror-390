#!/usr/bin/env python3
"""
Ailoos CLI - Command Line Interface for Decentralized AI Training
=================================================================

A comprehensive CLI tool for managing Ailoos federated learning nodes,
training sessions, models, rewards, and system monitoring.

Usage:
    ailoos node start [--node-id=NODE_ID] [--coordinator-url=URL]
    ailoos node stop [--force]
    ailoos node status [--json] [--watch]
    ailoos federated join SESSION_ID [--model=MODEL] [--data-path=PATH]
    ailoos federated status [SESSION_ID] [--json] [--watch]
    ailoos model list [--remote] [--local] [--filter=FILTER]
    ailoos model download MODEL_NAME [--version=VERSION]
    ailoos rewards balance [--json]
    ailoos rewards claim AMOUNT [--wallet=WALLET]
    ailoos config set KEY VALUE [--global]
    ailoos logs tail [--level=LEVEL] [--follow]
    ailoos --help
    ailoos --version

Examples:
    # Quick start
    ailoos node start

    # Advanced node setup
    ailoos node start --node-id my_node --coordinator-url https://coordinator.ailoos.ai

    # Join federated training
    ailoos federated join session_2024_001 --model empoorio-lm

    # Monitor training
    ailoos federated status --watch

    # Download model
    ailoos model download empoorio-lm --version v1.0.0

    # Check rewards
    ailoos rewards balance

    # Configure settings
    ailoos config set federated.batch_size 64

    # Monitor logs
    ailoos logs tail --level INFO --follow
"""

import asyncio
import sys
from pathlib import Path

# Import command groups
from .commands.node import node
from .commands.federated import federated
from .commands.model import model
from .commands.config import config
from .commands.rewards import rewards
from .commands.logs import logs
from .commands.coordinator import coordinator

# Import utilities
from ..utils.logging import setup_logging


def create_cli_app():
    """Create the main CLI application with all commands."""
    import click

    @click.group()
    @click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
    @click.option('--config', default='./ailoos.yaml',
                  help='Path to configuration file')
    @click.version_option(version='2.0.12', prog_name='Ailoos CLI')
    @click.pass_context
    def cli(ctx, verbose, config):
        """🚀 Ailoos CLI - Decentralized AI Training Platform

        A comprehensive command-line tool for managing federated learning
        nodes, training sessions, models, and rewards in the Ailoos ecosystem.
        """
        ctx.ensure_object(dict)
        ctx.obj['verbose'] = verbose
        ctx.obj['config'] = config

        # Setup logging
        log_level = 'DEBUG' if verbose else 'INFO'
        ctx.obj['logger'] = setup_logging(level=log_level)

    # Register command groups
    cli.add_command(node)
    cli.add_command(federated)
    cli.add_command(model)
    cli.add_command(config)
    cli.add_command(rewards)
    cli.add_command(logs)
    cli.add_command(coordinator)

    return cli

def main():
    """Synchronous main entry point for module execution."""
    cli = create_cli_app()
    try:
        cli()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        if '--verbose' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()