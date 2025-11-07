#!/usr/bin/env python3
"""
DRACMA Manager - High-level interface for DRACMA token operations
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .drachma_calculator import DrachmaCalculator
from .reward_distribution import RewardDistribution
from ..core.config import Config
from ..utils.logging import AiloosLogger


from ..core.config import get_config

class DRACMA_Manager:
    """High-level manager for DRACMA token operations"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = AiloosLogger(__name__)

        # Initialize components
        self.calculator = DrachmaCalculator(self.config)
        self.distribution = RewardDistribution(self.config, self.calculator)

    async def calculate_and_distribute_rewards(self, contributions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate and distribute rewards for contributions"""
        try:
            # Calculate rewards
            calculations = []
            for contrib in contributions:
                calc = await self.calculator.calculate_reward(
                    node_id=contrib['node_id'],
                    contribution_type=contrib['type'],
                    metrics=contrib.get('metrics', {}),
                    session_id=contrib.get('session_id', 'default')
                )
                calculations.append(calc)

            # Distribute rewards
            transactions = await self.distribution.distribute_rewards(calculations)

            return {
                'success': True,
                'calculations': len(calculations),
                'transactions': len(transactions),
                'total_drachma': sum(tx.drachma_amount for tx in transactions)
            }

        except Exception as e:
            self.logger.error(f"Error in reward calculation/distribution: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_node_balance(self, node_id: str) -> Dict[str, Any]:
        """Get balance information for a node"""
        try:
            balance = self.distribution.get_node_balance(node_id)
            if balance:
                return {
                    'node_id': balance.node_id,
                    'balance': balance.balance,
                    'total_earned': balance.total_earned,
                    'total_withdrawn': balance.total_withdrawn,
                    'last_updated': balance.last_updated.isoformat(),
                    'transaction_count': balance.transaction_count
                }
            else:
                return {
                    'node_id': node_id,
                    'balance': 0.0,
                    'total_earned': 0.0,
                    'total_withdrawn': 0.0,
                    'transaction_count': 0
                }

        except Exception as e:
            self.logger.error(f"Error getting balance for {node_id}: {e}")
            return {'error': str(e)}

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        try:
            calc_stats = self.calculator.get_calculation_stats()
            dist_stats = self.distribution.get_distribution_stats()

            return {
                'calculator': calc_stats,
                'distribution': dist_stats,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return {'error': str(e)}

    def get_pending_distributions(self) -> List[Dict[str, Any]]:
        """Get pending reward distributions"""
        try:
            pending = self.distribution.get_pending_distributions()
            return [
                {
                    'tx_hash': tx.tx_hash,
                    'node_id': tx.node_id,
                    'drachma_amount': tx.drachma_amount,
                    'session_id': tx.session_id,
                    'status': tx.status,
                    'timestamp': tx.timestamp.isoformat()
                }
                for tx in pending
            ]

        except Exception as e:
            self.logger.error(f"Error getting pending distributions: {e}")
            return []

    def get_completed_distributions(self, node_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get completed reward distributions"""
        try:
            completed = self.distribution.get_completed_distributions(node_id)
            return [
                {
                    'tx_hash': tx.tx_hash,
                    'node_id': tx.node_id,
                    'drachma_amount': tx.drachma_amount,
                    'session_id': tx.session_id,
                    'block_number': tx.block_number,
                    'gas_used': tx.gas_used,
                    'status': tx.status,
                    'timestamp': tx.timestamp.isoformat()
                }
                for tx in completed
            ]

        except Exception as e:
            self.logger.error(f"Error getting completed distributions: {e}")
            return []

    def get_balance(self, node_id: Optional[str] = None) -> Dict[str, Any]:
        """Get balance information (synchronous wrapper for CLI)."""
        try:
            # If no node_id provided, use current node from config
            if not node_id:
                node_id = self.config.get('node_id', 'default_node')

            # Get real balance from distribution system
            balance_info = self.distribution.get_node_balance(node_id)

            if balance_info:
                # Calculate additional metrics
                sessions_participated = len(self.calculator.get_node_rewards(node_id))
                total_rewards = self.calculator.get_total_node_rewards(node_id)
                avg_reward_per_session = total_rewards / max(sessions_participated, 1)

                return {
                    'total_balance': balance_info.balance,
                    'available_balance': balance_info.balance,  # Assuming all balance is available
                    'pending_balance': 0.0,  # TODO: Implement pending rewards tracking
                    'locked_balance': 0.0,   # TODO: Implement staking locks
                    'reputation_score': self._calculate_reputation_score(node_id),
                    'total_earned': balance_info.total_earned,
                    'sessions_participated': sessions_participated,
                    'avg_reward_per_session': avg_reward_per_session,
                    'next_claim_eligible': None,  # TODO: Implement claim cooldown
                    'min_claim_amount': self.config.get('min_claim_amount', 0.01),
                    'node_id': node_id,
                    'last_updated': balance_info.last_updated.isoformat()
                }
            else:
                # Node has no balance record yet
                return {
                    'total_balance': 0.0,
                    'available_balance': 0.0,
                    'pending_balance': 0.0,
                    'locked_balance': 0.0,
                    'reputation_score': 0.0,
                    'total_earned': 0.0,
                    'sessions_participated': 0,
                    'avg_reward_per_session': 0.0,
                    'next_claim_eligible': None,
                    'min_claim_amount': self.config.get('min_claim_amount', 0.01),
                    'node_id': node_id,
                    'last_updated': datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Error getting balance: {e}")
            return {
                'error': str(e),
                'total_balance': 0.0,
                'available_balance': 0.0,
                'pending_balance': 0.0,
                'locked_balance': 0.0,
                'reputation_score': 0.0,
                'total_earned': 0.0,
                'sessions_participated': 0,
                'avg_reward_per_session': 0.0,
                'next_claim_eligible': None,
                'min_claim_amount': 0.01
            }

    def get_history(self, node_id: Optional[str] = None, limit=20, start_date=None, end_date=None, reward_type='all') -> Dict[str, Any]:
        """Get rewards history (synchronous wrapper for CLI)."""
        try:
            # If no node_id provided, use current node from config
            if not node_id:
                node_id = self.config.get('node_id', 'default_node')

            # Get completed distributions for this node
            distributions = self.distribution.get_completed_distributions(node_id)

            # Filter by date range if provided
            if start_date or end_date:
                filtered_distributions = []
                for dist in distributions:
                    include = True
                    if start_date:
                        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        if dist.timestamp < start_dt:
                            include = False
                    if end_date:
                        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                        if dist.timestamp > end_dt:
                            include = False
                    if include:
                        filtered_distributions.append(dist)
                distributions = filtered_distributions

            # Sort by timestamp (most recent first)
            distributions.sort(key=lambda x: x.timestamp, reverse=True)

            # Apply limit
            has_more = len(distributions) > limit
            limited_distributions = distributions[:limit]

            # Convert to dict format
            rewards = []
            for dist in limited_distributions:
                rewards.append({
                    'tx_hash': dist.tx_hash,
                    'amount': dist.drachma_amount,
                    'session_id': dist.session_id,
                    'timestamp': dist.timestamp.isoformat(),
                    'block_number': dist.block_number,
                    'gas_used': dist.gas_used,
                    'status': dist.status,
                    'type': 'distribution'
                })

            return {
                'rewards': rewards,
                'total_count': len(distributions),
                'has_more': has_more,
                'node_id': node_id
            }

        except Exception as e:
            self.logger.error(f"Error getting rewards history: {e}")
            return {
                'rewards': [],
                'total_count': 0,
                'has_more': False,
                'error': str(e)
            }

    def _calculate_reputation_score(self, node_id: str) -> float:
        """Calculate reputation score for a node."""
        try:
            node_rewards = self.calculator.get_node_rewards(node_id)
            if not node_rewards:
                return 0.0

            # Factors for reputation:
            # 1. Consistency (regular participation)
            # 2. Performance (high rewards indicate good performance)
            # 3. Volume (total contributions)

            total_earned = sum(calc.drachma_amount for calc in node_rewards)
            sessions_count = len(node_rewards)
            avg_reward = total_earned / sessions_count

            # Simple reputation calculation (0-100 scale)
            consistency_score = min(sessions_count * 5, 40)  # Max 40 points for consistency
            performance_score = min(avg_reward * 20, 40)     # Max 40 points for performance
            volume_score = min(total_earned * 0.1, 20)       # Max 20 points for volume

            reputation = consistency_score + performance_score + volume_score
            return min(reputation, 100.0)

        except Exception as e:
            self.logger.error(f"Error calculating reputation for {node_id}: {e}")
            return 0.0

    def _calculate_efficiency_score(self, node_id: str) -> float:
        """Calculate efficiency score based on reward per contribution."""
        try:
            node_calculations = self.calculator.get_node_rewards(node_id)
            if not node_calculations:
                return 0.0

            # Efficiency = average reward per calculation
            total_reward = sum(calc.drachma_amount for calc in node_calculations)
            efficiency = total_reward / len(node_calculations)

            # Normalize to 0-100 scale (assuming 10 DRACMA is excellent efficiency)
            return min(efficiency * 10, 100.0)

        except Exception as e:
            self.logger.error(f"Error calculating efficiency for {node_id}: {e}")
            return 0.0

    def _calculate_accuracy_contribution(self, node_id: str) -> float:
        """Calculate average accuracy contribution from rewards."""
        try:
            # This is a simplified calculation - in reality would need accuracy data
            # For now, derive from reward amounts (higher rewards = better accuracy)
            node_calculations = self.calculator.get_node_rewards(node_id)
            if not node_calculations:
                return 0.0

            # Use reward amount as proxy for accuracy contribution
            avg_accuracy = sum(calc.drachma_amount for calc in node_calculations) / len(node_calculations)
            # Convert to percentage (assuming max reasonable reward is 50 DRACMA = 100%)
            return min(avg_accuracy * 2, 100.0)

        except Exception as e:
            self.logger.error(f"Error calculating accuracy contribution for {node_id}: {e}")
            return 0.0

    def claim_rewards(self, amount, wallet=None) -> Dict[str, Any]:
        """Claim rewards (synchronous wrapper for CLI)."""
        # Mock data
        return {
            'amount': amount,
            'wallet_address': wallet or 'mock_wallet',
            'transaction_hash': 'mock_tx_hash',
            'confirmed_at': '2024-01-01T00:00:00Z'
        }

    def calculate_staking_reward(self, amount, duration) -> Dict[str, Any]:
        """Calculate staking reward."""
        return {
            'multiplier': 1.5,
            'estimated_reward': amount * 0.1,
            'unlock_date': '2024-02-01T00:00:00Z'
        }

    def stake_tokens(self, amount, duration) -> Dict[str, Any]:
        """Stake tokens."""
        return {
            'stake_id': 'mock_stake_id',
            'unlock_date': '2024-02-01T00:00:00Z',
            'multiplier': 1.5
        }

    def unstake_tokens(self, stake_id) -> Dict[str, Any]:
        """Unstake tokens."""
        return {
            'returned_amount': 100.0,
            'reward': 10.0
        }

    def get_stake_info(self, stake_id):
        """Get stake info."""
        return {
            'amount': 100.0,
            'multiplier': 1.5,
            'earned_reward': 10.0,
            'locked_until': '2024-02-01T00:00:00Z'
        }

    def calculate_early_unstake_penalty(self, stake_id):
        """Calculate early unstake penalty."""
        return 5.0

    def get_stakes(self) -> Dict[str, Any]:
        """Get stakes."""
        return {
            'stakes': [],
            'total_staked': 0.0,
            'total_multiplier': 1.0,
            'pending_rewards': 0.0
        }

    def get_validator_info(self, validator_id):
        """Get validator info."""
        return {
            'reputation': 95,
            'apr': 12.5
        }

    def delegate_tokens(self, amount, validator, duration) -> Dict[str, Any]:
        """Delegate tokens."""
        return {
            'delegation_id': 'mock_delegation_id',
            'apr': 12.5,
            'end_date': '2024-02-01T00:00:00Z'
        }

    def get_delegation_info(self, delegation_id):
        """Get delegation info."""
        return {
            'amount': 100.0,
            'validator': 'validator_1',
            'earned_reward': 12.5,
            'locked_until': '2024-02-01T00:00:00Z'
        }

    def undelegate_tokens(self, delegation_id) -> Dict[str, Any]:
        """Undelegate tokens."""
        return {
            'returned_amount': 100.0,
            'reward': 12.5
        }

    def get_delegations(self) -> Dict[str, Any]:
        """Get delegations."""
        return {
            'delegations': [],
            'total_delegated': 0.0,
            'total_apr': 0.0,
            'pending_rewards': 0.0
        }

    def update_settings(self, settings):
        """Update settings."""
        pass

    def get_settings(self) -> Dict[str, Any]:
        """Get settings."""
        return {
            'wallet_address': None,
            'auto_claim': False,
            'min_claim_amount': 0.01
        }

    def get_stats(self, node_id: Optional[str] = None) -> Dict[str, Any]:
        """Get stats."""
        try:
            # If no node_id provided, use current node from config
            if not node_id:
                node_id = self.config.get('node_id', 'default_node')

            # Get distribution stats
            dist_stats = self.distribution.get_distribution_stats()

            # Get calculator stats
            calc_stats = self.calculator.get_calculation_stats()

            # Get node-specific data
            node_rewards = self.calculator.get_node_rewards(node_id)
            total_earned = self.calculator.get_total_node_rewards(node_id)
            sessions_participated = len(node_rewards)
            avg_reward_per_session = total_earned / max(sessions_participated, 1)

            # Calculate rank (simplified - based on total earned)
            all_nodes_rewards = {}
            for calc in self.calculator.calculations:
                if calc.node_id not in all_nodes_rewards:
                    all_nodes_rewards[calc.node_id] = 0
                all_nodes_rewards[calc.node_id] += calc.drachma_amount

            sorted_nodes = sorted(all_nodes_rewards.items(), key=lambda x: x[1], reverse=True)
            node_rank = next((i + 1 for i, (nid, _) in enumerate(sorted_nodes) if nid == node_id), 0)

            return {
                'overall': {
                    'total_supply': 1000000.0,  # TODO: Get from blockchain
                    'total_distributed': dist_stats.get('total_distributed_drachma', 0.0),
                    'active_participants': dist_stats.get('unique_nodes', 0),
                    'total_sessions': len(self.calculator.reward_pools),
                    'total_calculations': len(self.calculator.calculations)
                },
                'user': {
                    'total_earned': total_earned,
                    'sessions_participated': sessions_participated,
                    'avg_reward_per_session': avg_reward_per_session,
                    'rank': node_rank,
                    'node_id': node_id
                },
                'performance': {
                    'efficiency_score': self._calculate_efficiency_score(node_id),
                    'accuracy_contribution': self._calculate_accuracy_contribution(node_id),
                    'uptime_percentage': 98.5  # TODO: Implement uptime tracking
                },
                'distribution': dist_stats,
                'calculator': calc_stats
            }

        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {
                'overall': {
                    'total_supply': 1000000.0,
                    'total_distributed': 0.0,
                    'active_participants': 0
                },
                'user': {
                    'total_earned': 0.0,
                    'sessions_participated': 0,
                    'avg_reward_per_session': 0.0,
                    'rank': 0
                },
                'performance': {
                    'efficiency_score': 0,
                    'accuracy_contribution': 0.0,
                    'uptime_percentage': 0.0
                },
                'error': str(e)
            }