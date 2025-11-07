"""
Rewards and DRACMA management commands for Ailoos CLI.
Handles token balance, claiming, history, and staking operations.
"""

import asyncio
import click
import json
from datetime import datetime, timedelta
from typing import Optional


from ...rewards.dracma_manager import DRACMA_Manager
from ...core.config import get_config
from ...utils.logging import AiloosLogger


@click.group()
@click.pass_context
def rewards(ctx):
    """Rewards and DRACMA token management commands."""
    ctx.obj = get_config()


@rewards.command()
@click.option('--json', is_flag=True, help='Output in JSON format')
@click.option('--detailed', is_flag=True, help='Show detailed breakdown')
@click.pass_context
def balance(ctx, json, detailed):
    """Show DRACMA token balance and rewards."""
    config = ctx.obj
    manager = DRACMA_Manager(config=config)

    try:
        balance_info = manager.get_balance()

        if json:
            click.echo(json.dumps(balance_info, indent=2, default=str))
        else:
            click.echo("💰 DRACMA Balance")
            click.echo("=" * 50)
            click.echo(f"📊 Total Balance: {balance_info['total_balance']} DRACMA")
            click.echo(f"✅ Available: {balance_info['available_balance']} DRACMA")
            click.echo(f"⏳ Pending: {balance_info['pending_balance']} DRACMA")
            click.echo(f"🔒 Locked: {balance_info['locked_balance']} DRACMA")

            if detailed:
                click.echo(f"\n🏆 Reputation Score: {balance_info['reputation_score']}")
                click.echo(f"📈 Total Earned: {balance_info['total_earned']} DRACMA")
                click.echo(f"🎯 Sessions Participated: {balance_info['sessions_participated']}")
                click.echo(f"📊 Average Reward per Session: {balance_info['avg_reward_per_session']} DRACMA")

                click.echo(f"\n⏰ Next Claim Eligible: {balance_info['next_claim_eligible']}")
                click.echo(f"💡 Minimum Claim: {balance_info['min_claim_amount']} DRACMA")

    except Exception as e:
        click.echo(f"❌ Error getting balance: {e}")
        raise click.ClickException(f"Balance check failed: {e}")


@rewards.command()
@click.option('--amount', type=float, help='Specific amount to claim')
@click.option('--wallet', help='Wallet address for claim')
@click.option('--all', is_flag=True, help='Claim all available balance')
@click.option('--force', is_flag=True, help='Skip confirmation')
@click.pass_context
def claim(ctx, amount, wallet, all, force):
    """Claim available DRACMA rewards."""
    config = ctx.obj
    manager = DRACMA_Manager(config=config)

    try:
        # Get current balance
        balance = manager.get_balance()

        if all:
            amount = balance['available_balance']
        elif not amount:
            # Use default minimum claim amount
            amount = max(balance['available_balance'], balance['min_claim_amount'])

        if amount <= 0:
            click.echo("❌ No rewards available to claim")
            raise click.Abort()

        if amount < balance['min_claim_amount']:
            click.echo(f"❌ Amount below minimum claim threshold ({balance['min_claim_amount']} DRACMA)")
            raise click.Abort()

        # Confirm claim
        if not force:
            if not click.confirm(f"Claim {amount} DRACMA to wallet?"):
                return

        # Perform claim
        claim_result = manager.claim_rewards(amount, wallet)

        click.echo("✅ Rewards claimed successfully!")
        click.echo(f"💰 Amount: {claim_result['amount']} DRACMA")
        click.echo(f"🏦 Wallet: {claim_result['wallet_address']}")
        click.echo(f"🔗 Transaction: {claim_result['transaction_hash']}")
        click.echo(f"⏱️  Confirmed at: {claim_result['confirmed_at']}")

    except Exception as e:
        click.echo(f"❌ Claim failed: {e}")
        raise click.ClickException(f"Reward claim failed: {e}")


@rewards.command()
@click.option('--limit', default=20, type=int, help='Number of records to show')
@click.option('--json', is_flag=True, help='Output in JSON format')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
@click.option('--type', type=click.Choice(['all', 'earned', 'claimed', 'staked']),
              default='all', help='Type of rewards to show')
@click.pass_context
def history(ctx, limit, json, start_date, end_date, type):
    """Show rewards history and transactions."""
    config = ctx.obj
    manager = DRACMA_Manager(config=config)

    try:
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        history_data = manager.get_history(
            limit=limit,
            start_date=start,
            end_date=end,
            reward_type=type
        )

        if json:
            click.echo(json.dumps(history_data, indent=2, default=str))
        else:
            click.echo("📋 DRACMA Rewards History")
            click.echo("=" * 70)
            click.echo("<12")
            click.echo("-" * 70)

            for reward in history_data['rewards']:
                type_emoji = {
                    'training': '🎯',
                    'validation': '✅',
                    'bonus': '🎁',
                    'staking': '🔒',
                    'claim': '💰'
                }.get(reward['type'], '📊')

                click.echo("<12")

            click.echo("-" * 70)
            click.echo(f"📊 Total Records: {history_data['total_count']}")
            if history_data['has_more']:
                click.echo(f"💡 Showing first {limit} records. Use --limit for more.")

    except Exception as e:
        click.echo(f"❌ Error getting history: {e}")
        raise click.ClickException(f"History retrieval failed: {e}")


@rewards.command()
@click.argument('amount', type=float)
@click.option('--duration', default=30, type=int,
              help='Staking duration in days')
@click.option('--force', is_flag=True, help='Skip confirmation')
@click.pass_context
def stake(ctx, amount, duration, force):
    """Stake DRACMA tokens for rewards multiplier."""
    config = ctx.obj
    manager = DRACMA_Manager(config=config)

    try:
        # Validate staking amount
        balance = manager.get_balance()
        if amount > balance['available_balance']:
            click.echo(f"❌ Insufficient balance. Available: {balance['available_balance']} DRACMA")
            raise click.Abort()

        # Calculate rewards
        reward_info = manager.calculate_staking_reward(amount, duration)

        click.echo("🔒 DRACMA Staking")
        click.echo("=" * 40)
        click.echo(f"💰 Amount to stake: {amount} DRACMA")
        click.echo(f"⏱️  Duration: {duration} days")
        click.echo(f"📈 Reward multiplier: {reward_info['multiplier']}x")
        click.echo(f"🎁 Estimated reward: {reward_info['estimated_reward']} DRACMA")
        click.echo(f"📅 Unlock date: {reward_info['unlock_date']}")

        if not force:
            if not click.confirm("Proceed with staking?"):
                return

        # Perform staking
        stake_result = manager.stake_tokens(amount, duration)

        click.echo("✅ Tokens staked successfully!")
        click.echo(f"🔗 Stake ID: {stake_result['stake_id']}")
        click.echo(f"⏱️  Unlock date: {stake_result['unlock_date']}")
        click.echo(f"📈 Multiplier: {stake_result['multiplier']}x")

    except Exception as e:
        click.echo(f"❌ Staking failed: {e}")
        raise click.ClickException(f"Token staking failed: {e}")


@rewards.command()
@click.argument('stake_id')
@click.option('--force', is_flag=True, help='Skip confirmation')
@click.pass_context
def unstake(ctx, stake_id, force):
    """Unstake DRACMA tokens."""
    config = ctx.obj
    manager = DRACMA_Manager(config=config)

    try:
        # Get stake info
        stake_info = manager.get_stake_info(stake_id)

        if not stake_info:
            click.echo(f"❌ Stake ID '{stake_id}' not found")
            raise click.Abort()

        click.echo("🔓 Unstake DRACMA Tokens")
        click.echo("=" * 40)
        click.echo(f"🔗 Stake ID: {stake_id}")
        click.echo(f"💰 Amount: {stake_info['amount']} DRACMA")
        click.echo(f"📈 Multiplier: {stake_info['multiplier']}x")
        click.echo(f"🎁 Earned reward: {stake_info['earned_reward']} DRACMA")

        if stake_info['locked_until'] > datetime.now():
            early_penalty = manager.calculate_early_unstake_penalty(stake_id)
            click.echo(f"⚠️  Early unstake penalty: {early_penalty} DRACMA")
            if not force:
                if not click.confirm("Unstake early (penalty applies)?"):
                    return

        # Perform unstaking
        unstake_result = manager.unstake_tokens(stake_id)

        click.echo("✅ Tokens unstaked successfully!")
        click.echo(f"💰 Returned: {unstake_result['returned_amount']} DRACMA")
        click.echo(f"🎁 Reward: {unstake_result['reward']} DRACMA")
        if 'penalty' in unstake_result:
            click.echo(f"⚠️  Penalty: {unstake_result['penalty']} DRACMA")

    except Exception as e:
        click.echo(f"❌ Unstaking failed: {e}")
        raise click.ClickException(f"Token unstaking failed: {e}")


@rewards.command()
@click.option('--json', is_flag=True, help='Output in JSON format')
@click.pass_context
def stakes(ctx, json):
    """Show current staking positions."""
    config = ctx.obj
    manager = DRACMA_Manager(config=config)

    try:
        stakes_data = manager.get_stakes()

        if json:
            click.echo(json.dumps(stakes_data, indent=2, default=str))
        else:
            if not stakes_data['stakes']:
                click.echo("📊 No active stakes")
                return

            click.echo("🔒 Active DRACMA Stakes")
            click.echo("=" * 80)
            click.echo("<12")
            click.echo("-" * 80)

            for stake in stakes_data['stakes']:
                status_emoji = "🔒" if stake['is_locked'] else "🔓"
                click.echo("<12")

            click.echo("-" * 80)
            click.echo(f"💰 Total staked: {stakes_data['total_staked']} DRACMA")
            click.echo(f"📈 Total multiplier: {stakes_data['total_multiplier']}x")
            click.echo(f"🎁 Pending rewards: {stakes_data['pending_rewards']} DRACMA")

    except Exception as e:
        click.echo(f"❌ Error getting stakes: {e}")
        raise click.ClickException(f"Stakes retrieval failed: {e}")


@rewards.command()
@click.option('--amount', type=float, required=True, help='Amount to delegate')
@click.option('--validator', required=True, help='Validator node ID')
@click.option('--duration', default=30, type=int, help='Delegation duration in days')
@click.option('--force', is_flag=True, help='Skip confirmation')
@click.pass_context
def delegate(ctx, amount, validator, duration, force):
    """Delegate DRACMA tokens to a validator."""
    config = ctx.obj
    manager = DRACMA_Manager(config=config)

    try:
        # Validate delegation
        balance = manager.get_balance()
        if amount > balance['available_balance']:
            click.echo(f"❌ Insufficient balance. Available: {balance['available_balance']} DRACMA")
            raise click.Abort()

        # Get validator info
        validator_info = manager.get_validator_info(validator)
        if not validator_info:
            click.echo(f"❌ Validator '{validator}' not found")
            raise click.Abort()

        click.echo("🎯 Delegate DRACMA Tokens")
        click.echo("=" * 40)
        click.echo(f"💰 Amount: {amount} DRACMA")
        click.echo(f"🏛️  Validator: {validator}")
        click.echo(f"🏆 Reputation: {validator_info['reputation']}")
        click.echo(f"📊 APR: {validator_info['apr']}%")
        click.echo(f"⏱️  Duration: {duration} days")

        if not force:
            if not click.confirm("Proceed with delegation?"):
                return

        # Perform delegation
        delegate_result = manager.delegate_tokens(amount, validator, duration)

        click.echo("✅ Tokens delegated successfully!")
        click.echo(f"🔗 Delegation ID: {delegate_result['delegation_id']}")
        click.echo(f"📈 Expected APR: {delegate_result['apr']}%")
        click.echo(f"⏱️  End date: {delegate_result['end_date']}")

    except Exception as e:
        click.echo(f"❌ Delegation failed: {e}")
        raise click.ClickException(f"Token delegation failed: {e}")


@rewards.command()
@click.argument('delegation_id')
@click.option('--force', is_flag=True, help='Skip confirmation')
@click.pass_context
def undelegate(ctx, delegation_id, force):
    """Undelegate DRACMA tokens from validator."""
    config = ctx.obj
    manager = DRACMA_Manager(config=config)

    try:
        # Get delegation info
        delegation_info = manager.get_delegation_info(delegation_id)

        if not delegation_info:
            click.echo(f"❌ Delegation ID '{delegation_id}' not found")
            raise click.Abort()

        click.echo("🔄 Undelegate DRACMA Tokens")
        click.echo("=" * 40)
        click.echo(f"🔗 Delegation ID: {delegation_id}")
        click.echo(f"💰 Amount: {delegation_info['amount']} DRACMA")
        click.echo(f"🏛️  Validator: {delegation_info['validator']}")
        click.echo(f"🎁 Earned reward: {delegation_info['earned_reward']} DRACMA")

        if delegation_info['locked_until'] > datetime.now():
            click.echo("⚠️  Tokens are still locked. Early undelegation may incur penalties.")
            if not force:
                if not click.confirm("Undelegate early?"):
                    return

        # Perform undelegation
        undelegate_result = manager.undelegate_tokens(delegation_id)

        click.echo("✅ Tokens undelegated successfully!")
        click.echo(f"💰 Returned: {undelegate_result['returned_amount']} DRACMA")
        click.echo(f"🎁 Reward: {undelegate_result['reward']} DRACMA")

    except Exception as e:
        click.echo(f"❌ Undelegation failed: {e}")
        raise click.ClickException(f"Token undelegation failed: {e}")


@rewards.command()
@click.option('--json', is_flag=True, help='Output in JSON format')
@click.pass_context
def delegations(ctx, json):
    """Show current delegations."""
    config = ctx.obj
    manager = DRACMA_Manager(config=config)

    try:
        delegations_data = manager.get_delegations()

        if json:
            click.echo(json.dumps(delegations_data, indent=2, default=str))
        else:
            if not delegations_data['delegations']:
                click.echo("📊 No active delegations")
                return

            click.echo("🎯 Active DRACMA Delegations")
            click.echo("=" * 90)
            click.echo("<12")
            click.echo("-" * 90)

            for delegation in delegations_data['delegations']:
                click.echo("<12")

            click.echo("-" * 90)
            click.echo(f"💰 Total delegated: {delegations_data['total_delegated']} DRACMA")
            click.echo(f"📈 Total APR: {delegations_data['total_apr']}%")
            click.echo(f"🎁 Pending rewards: {delegations_data['pending_rewards']} DRACMA")

    except Exception as e:
        click.echo(f"❌ Error getting delegations: {e}")
        raise click.ClickException(f"Delegations retrieval failed: {e}")


@rewards.command()
@click.option('--wallet', help='Set default wallet address')
@click.option('--auto-claim', type=bool, help='Enable/disable auto-claim')
@click.option('--min-claim', type=float, help='Set minimum claim amount')
@click.pass_context
def settings(ctx, wallet, auto_claim, min_claim):
    """Configure rewards settings."""
    config = ctx.obj
    manager = DRACMA_Manager(config=config)

    try:
        updated_settings = {}

        if wallet is not None:
            updated_settings['wallet_address'] = wallet
            click.echo(f"🏦 Wallet address set to: {wallet}")

        if auto_claim is not None:
            updated_settings['auto_claim'] = auto_claim
            click.echo(f"🤖 Auto-claim {'enabled' if auto_claim else 'disabled'}")

        if min_claim is not None:
            updated_settings['min_claim_amount'] = min_claim
            click.echo(f"💰 Minimum claim amount set to: {min_claim} DRACMA")

        if updated_settings:
            manager.update_settings(updated_settings)
            click.echo("✅ Settings updated successfully")
        else:
            # Show current settings
            settings_data = manager.get_settings()
            click.echo("⚙️  Current Rewards Settings")
            click.echo("=" * 40)
            click.echo(f"🏦 Wallet: {settings_data.get('wallet_address', 'Not set')}")
            click.echo(f"🤖 Auto-claim: {settings_data.get('auto_claim', False)}")
            click.echo(f"💰 Min claim: {settings_data.get('min_claim_amount', 0.01)} DRACMA")

    except Exception as e:
        click.echo(f"❌ Settings update failed: {e}")
        raise click.ClickException(f"Settings update failed: {e}")


@rewards.command()
@click.option('--json', is_flag=True, help='Output in JSON format')
@click.pass_context
def stats(ctx, json):
    """Show rewards statistics and analytics."""
    config = ctx.obj
    manager = DRACMA_Manager(config=config)

    try:
        stats_data = manager.get_stats()

        if json:
            click.echo(json.dumps(stats_data, indent=2, default=str))
        else:
            click.echo("📊 DRACMA Rewards Statistics")
            click.echo("=" * 50)

            # Overall stats
            overall = stats_data['overall']
            click.echo(f"🌍 Total DRACMA in circulation: {overall['total_supply']}")
            click.echo(f"🎯 Total rewards distributed: {overall['total_distributed']}")
            click.echo(f"👥 Active participants: {overall['active_participants']}")

            # User stats
            user = stats_data['user']
            click.echo(f"\n👤 Your Statistics:")
            click.echo(f"   💰 Total earned: {user['total_earned']} DRACMA")
            click.echo(f"   🎯 Sessions participated: {user['sessions_participated']}")
            click.echo(f"   📈 Average reward/session: {user['avg_reward_per_session']} DRACMA")
            click.echo(f"   🏆 Rank: #{user['rank']} of {overall['active_participants']}")

            # Performance
            perf = stats_data['performance']
            click.echo(f"\n📈 Performance:")
            click.echo(f"   🏃‍♂️ Efficiency score: {perf['efficiency_score']}/100")
            click.echo(f"   🎯 Accuracy contribution: {perf['accuracy_contribution']}%")
            click.echo(f"   ⚡ Uptime: {perf['uptime_percentage']}%")

    except Exception as e:
        click.echo(f"❌ Error getting stats: {e}")
        raise click.ClickException(f"Stats retrieval failed: {e}")


@rewards.command()
@click.pass_context
def test(ctx):
    """Test command to instantiate DRACMA_Manager."""
    config = ctx.obj
    click.echo(f"Config from ctx.obj: {config}")
    click.echo(f"Type: {type(config)}")
    try:
        manager = DRACMA_Manager(config=config)
        click.echo("✅ DRACMA_Manager instantiated successfully")
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise click.ClickException(f"Test failed: {e}")




