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
    import platform
    import psutil
    import os
    from pathlib import Path

    @click.group(
        epilog="""
🚀 AILOOS CLI - DECENTRALIZED AI TRAINING PLATFORM
════════════════════════════════════════════════════════════════════════════════

📋 QUICK START GUIDE:
────────────────────
1. First time setup:    ailoos config init --auto
2. Start your node:     ailoos node start --id your_node_name
3. Download a model:    ailoos model download empoorio-lm
4. Join federated training: ailoos federated sessions
5. Check rewards:       ailoos rewards balance

🔧 MOST USED COMMANDS:
─────────────────────
• ailoos node status          - Check node status
• ailoos federated status     - Monitor training
• ailoos rewards balance      - View DRACMA balance
• ailoos logs tail            - Monitor logs
• ailoos config show          - View configuration

📋 COMPLETE COMMAND REFERENCE (59+ commands):
────────────────────────────────────────────

🎯 CONFIGURATION COMMANDS (9):
  ailoos config init              - Initialize new configuration
  ailoos config show              - Show current configuration
  ailoos config get <key>         - Get configuration value
  ailoos config set <key> <value> - Set configuration value
  ailoos config unset <key>       - Remove configuration key
  ailoos config validate          - Validate configuration file
  ailoos config backup            - Create configuration backup
  ailoos config restore           - Restore configuration from backup
  ailoos config migrate           - Migrate configuration to latest format

👑 COORDINATOR COMMANDS (6):
  ailoos coordinator start                    - Start simple coordinator
  ailoos coordinator status                   - Check coordinator status
  ailoos coordinator create-session           - Create new session
  ailoos coordinator list-sessions            - List all sessions
  ailoos coordinator session-info <id>        - Get session details
  ailoos coordinator start-session <id>       - Start specific session

🔄 FEDERATED LEARNING COMMANDS (10):
  ailoos federated sessions           - List available sessions
  ailoos federated join <session>     - Join federated session
  ailoos federated leave              - Leave current session
  ailoos federated status             - Show training status
  ailoos federated monitor            - Real-time training monitor
  ailoos federated pause              - Pause training session
  ailoos federated resume             - Resume paused session
  ailoos federated abort              - Abort session (irreversible)
  ailoos federated results            - Download training results
  ailoos federated analyze            - Analyze training performance

📋 LOGGING & MONITORING COMMANDS (7):
  ailoos logs tail                    - Show recent logs
  ailoos logs search <pattern>        - Search logs for patterns
  ailoos logs analyze                 - Analyze logs for anomalies
  ailoos logs monitor                 - Real-time system monitoring
  ailoos logs diagnostics             - Generate system diagnostics
  ailoos logs config                  - Configure logging settings
  ailoos logs debug                   - Enable debug mode

🤖 MODEL MANAGEMENT COMMANDS (8):
  ailoos model list                   - List available models
  ailoos model download <model>       - Download model from repository
  ailoos model info <model>           - Show model information
  ailoos model test <model>           - Test model with sample data
  ailoos model verify <model>         - Verify model integrity
  ailoos model export <model> <fmt>   - Export model to different formats
  ailoos model remove <model>         - Remove downloaded model
  ailoos model clean                  - Clean old/unused models

🖥️ NODE MANAGEMENT COMMANDS (7):
  ailoos node start                   - Start federated learning node
  ailoos node stop                    - Stop running node
  ailoos node status                  - Show node status and info
  ailoos node config                  - Update node configuration
  ailoos node monitor                 - Monitor node performance
  ailoos node logs                    - Show recent node logs
  ailoos node backup                  - Create node data backup
  ailoos node reset                   - Reset node to initial state

💰 REWARDS & DRACMA COMMANDS (12):
  ailoos rewards balance              - Show DRACMA balance
  ailoos rewards history              - Show rewards history
  ailoos rewards claim                - Claim available rewards
  ailoos rewards stake <amount>       - Stake tokens for multiplier
  ailoos rewards unstake <amount>     - Unstake tokens
  ailoos rewards delegate <validator> - Delegate to validator
  ailoos rewards undelegate <val>     - Undelegate from validator
  ailoos rewards delegations          - Show current delegations
  ailoos rewards stakes               - Show current stakes
  ailoos rewards stats                - Show rewards statistics
  ailoos rewards settings             - Configure rewards settings
  ailoos rewards test                 - Test DRACMA_Manager

🆘 TROUBLESHOOTING:
──────────────────
• System diagnostics:    ailoos logs diagnostics
• Check configuration:   ailoos config validate
• Verbose output:        ailoos --verbose COMMAND
• Debug mode:           ailoos logs debug

📊 SYSTEM INFO:
─────────────
• Python: {python_version}
• Platform: {platform_info}
• CPU Cores: {cpu_count}
• Memory: {memory_gb:.1f}GB
• Config file: {config_file}

📚 RESOURCES:
───────────
• Documentation: https://ailoos.dev/docs
• Discord: https://discord.gg/ailoos
• GitHub: https://github.com/empoorio/ailoos
• Support: dev@empoorio.com

⚖️  LICENSE:
──────────
Proprietary License - Ailoos Technologies & Empoorio Ecosystem
See LICENSE file for details.

💡 TIP: Use 'ailoos COMMAND --help' for detailed command help
        """.format(
            python_version=platform.python_version(),
            platform_info=platform.platform(),
            cpu_count=psutil.cpu_count(),
            memory_gb=psutil.virtual_memory().total / (1024**3),
            config_file="./ailoos.yaml"
        )
    )
    @click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
    @click.option('--config', default='./ailoos.yaml',
                  help='Path to configuration file')
    @click.version_option(version='2.0.18', prog_name='Ailoos CLI')
    @click.pass_context
    def cli(ctx, verbose, config):
        """A comprehensive command-line tool for managing federated learning
        nodes, training sessions, models, and rewards in the Ailoos ecosystem."""

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