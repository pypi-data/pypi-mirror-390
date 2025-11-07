#!/usr/bin/env python3
"""
Tokenomics Engine for Ailoos Network
Implementa modelos económicos avanzados con teoría de juegos y tokenomics
"""

import math
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import asyncio
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenType(Enum):
    """Tipos de tokens en el sistema"""
    UTILITY = "utility"
    GOVERNANCE = "governance"
    REWARD = "reward"
    STAKING = "staking"

class EconomicAgent(Enum):
    """Tipos de agentes económicos"""
    NODE = "node"
    USER = "user"
    VALIDATOR = "validator"
    DEVELOPER = "developer"

@dataclass
class TokenMetrics:
    """Métricas de un token"""
    token_type: TokenType
    total_supply: float
    circulating_supply: float
    market_cap: float = 0.0
    price: float = 1.0
    volume_24h: float = 0.0
    holders: int = 0
    transactions_24h: int = 0

@dataclass
class AgentProfile:
    """Perfil económico de un agente"""
    agent_id: str
    agent_type: EconomicAgent
    balance: Dict[TokenType, float] = field(default_factory=dict)
    reputation_score: float = 0.0
    stake_amount: float = 0.0
    contribution_score: float = 0.0
    risk_tolerance: float = 0.5
    last_activity: Optional[datetime] = None
    economic_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class EconomicEvent:
    """Evento económico"""
    event_id: str
    event_type: str
    timestamp: datetime
    participants: List[str]
    token_flows: Dict[str, Dict[TokenType, float]]
    metadata: Dict[str, Any] = field(default_factory=dict)

class TokenomicsEngine:
    """
    Motor de tokenomics avanzado con teoría de juegos
    Implementa modelos económicos complejos para la red Ailoos
    """

    def __init__(self):
        # Token supplies and metrics
        self.tokens: Dict[TokenType, TokenMetrics] = {}
        self._initialize_tokens()

        # Agent registry
        self.agents: Dict[str, AgentProfile] = {}

        # Economic events history
        self.economic_events: List[EconomicEvent] = []

        # Game theory models
        self.prisoners_dilemma_matrix = self._initialize_prisoners_dilemma()
        self.staking_game_matrix = self._initialize_staking_game()

        # Economic parameters
        self.inflation_rate = 0.02  # 2% annual inflation
        self.staking_reward_rate = 0.08  # 8% APY for staking
        self.contribution_reward_rate = 0.05  # 5% for contributions
        self.slashing_penalty = 0.1  # 10% slashing for misbehavior

        # Market dynamics
        self.price_elasticity = 0.3
        self.volatility_factor = 0.15

        logger.info("💰 Tokenomics Engine initialized")

    def _initialize_tokens(self):
        """Initialize token supplies and metrics"""
        # Utility Token (AIL)
        self.tokens[TokenType.UTILITY] = TokenMetrics(
            token_type=TokenType.UTILITY,
            total_supply=1_000_000_000,  # 1B tokens
            circulating_supply=200_000_000,  # 200M circulating
            price=0.1,
            holders=50000
        )

        # Governance Token (AILG)
        self.tokens[TokenType.GOVERNANCE] = TokenMetrics(
            token_type=TokenType.GOVERNANCE,
            total_supply=100_000_000,  # 100M tokens
            circulating_supply=20_000_000,  # 20M circulating
            price=1.0,
            holders=10000
        )

        # Reward Token (AILR)
        self.tokens[TokenType.REWARD] = TokenMetrics(
            token_type=TokenType.REWARD,
            total_supply=500_000_000,  # 500M tokens
            circulating_supply=100_000_000,  # 100M circulating
            price=0.05,
            holders=25000
        )

        # Staking Token (AILS)
        self.tokens[TokenType.STAKING] = TokenMetrics(
            token_type=TokenType.STAKING,
            total_supply=200_000_000,  # 200M tokens
            circulating_supply=50_000_000,  # 50M circulating
            price=0.2,
            holders=15000
        )

    def _initialize_prisoners_dilemma(self) -> Dict[Tuple[str, str], Tuple[float, float]]:
        """Initialize Prisoner's Dilemma payoff matrix"""
        # (action_agent1, action_agent2): (payoff_agent1, payoff_agent2)
        return {
            ("cooperate", "cooperate"): (3, 3),      # Mutual cooperation
            ("cooperate", "defect"): (0, 5),         # Agent 1 cooperates, Agent 2 defects
            ("defect", "cooperate"): (5, 0),         # Agent 1 defects, Agent 2 cooperates
            ("defect", "defect"): (1, 1)             # Mutual defection
        }

    def _initialize_staking_game(self) -> Dict[Tuple[str, str], Tuple[float, float]]:
        """Initialize Staking Game payoff matrix"""
        # Simplified staking game: (stake_high, stake_low)
        return {
            ("high", "high"): (2, 2),        # Both stake high - balanced rewards
            ("high", "low"): (1.5, 2.5),     # High staker gets less, low staker gets more
            ("low", "high"): (2.5, 1.5),     # Low staker gets more, high staker gets less
            ("low", "low"): (1, 1)           # Both stake low - minimal rewards
        }

    def register_agent(self, agent_id: str, agent_type: EconomicAgent,
                      initial_balance: Dict[TokenType, float] = None) -> AgentProfile:
        """Register new economic agent"""
        if initial_balance is None:
            initial_balance = {token_type: 1000.0 for token_type in TokenType}

        profile = AgentProfile(
            agent_id=agent_id,
            agent_type=agent_type,
            balance=initial_balance.copy(),
            last_activity=datetime.now()
        )

        self.agents[agent_id] = profile

        # Update token metrics
        for token_type, amount in initial_balance.items():
            if token_type in self.tokens:
                self.tokens[token_type].holders += 1

        logger.info(f"👤 Agent registered: {agent_id} ({agent_type.value})")
        return profile

    def calculate_nash_equilibrium(self, game_matrix: Dict[Tuple[str, str], Tuple[float, float]],
                                 strategies: List[str]) -> Dict[str, Any]:
        """
        Calculate Nash Equilibrium for a given game
        Returns the equilibrium strategies and payoffs
        """
        nash_equilibria = []

        # Check all possible strategy combinations
        for strategy1 in strategies:
            for strategy2 in strategies:
                payoff1, payoff2 = game_matrix[(strategy1, strategy2)]

                # Check if this is a Nash equilibrium
                is_nash = True

                # Check if agent 1 would deviate
                for alt_strategy1 in strategies:
                    if alt_strategy1 != strategy1:
                        alt_payoff1, _ = game_matrix[(alt_strategy1, strategy2)]
                        if alt_payoff1 > payoff1:
                            is_nash = False
                            break

                if not is_nash:
                    continue

                # Check if agent 2 would deviate
                for alt_strategy2 in strategies:
                    if alt_strategy2 != strategy2:
                        _, alt_payoff2 = game_matrix[(strategy1, alt_strategy2)]
                        if alt_payoff2 > payoff2:
                            is_nash = False
                            break

                if is_nash:
                    nash_equilibria.append({
                        'strategy1': strategy1,
                        'strategy2': strategy2,
                        'payoff1': payoff1,
                        'payoff2': payoff2
                    })

        return {
            'equilibria': nash_equilibria,
            'num_equilibria': len(nash_equilibria),
            'strategies': strategies
        }

    def analyze_prisoners_dilemma(self, agent1_id: str, agent2_id: str) -> Dict[str, Any]:
        """Analyze Prisoner's Dilemma between two agents"""
        if agent1_id not in self.agents or agent2_id not in self.agents:
            raise ValueError("Agents not found")

        agent1 = self.agents[agent1_id]
        agent2 = self.agents[agent2_id]

        # Calculate cooperation probability based on reputation and history
        coop_prob1 = self._calculate_cooperation_probability(agent1)
        coop_prob2 = self._calculate_cooperation_probability(agent2)

        # Simulate game outcomes
        outcomes = []
        for _ in range(100):  # Monte Carlo simulation
            action1 = "cooperate" if np.random.random() < coop_prob1 else "defect"
            action2 = "cooperate" if np.random.random() < coop_prob2 else "defect"

            payoff1, payoff2 = self.prisoners_dilemma_matrix[(action1, action2)]
            outcomes.append({
                'action1': action1,
                'action2': action2,
                'payoff1': payoff1,
                'payoff2': payoff2
            })

        # Calculate Nash equilibrium
        nash_analysis = self.calculate_nash_equilibrium(
            self.prisoners_dilemma_matrix,
            ["cooperate", "defect"]
        )

        return {
            'agent1_cooperation_prob': coop_prob1,
            'agent2_cooperation_prob': coop_prob2,
            'simulated_outcomes': outcomes,
            'nash_equilibrium': nash_analysis,
            'recommended_strategy': self._recommend_pd_strategy(coop_prob1, coop_prob2)
        }

    def _calculate_cooperation_probability(self, agent: AgentProfile) -> float:
        """Calculate probability of cooperation based on agent profile"""
        base_prob = 0.5  # Base 50% cooperation

        # Adjust based on reputation
        reputation_factor = agent.reputation_score / 100.0  # Assume 0-100 scale
        base_prob += reputation_factor * 0.3

        # Adjust based on stake amount (higher stake = more cooperative)
        stake_factor = min(agent.stake_amount / 10000.0, 1.0)
        base_prob += stake_factor * 0.2

        # Adjust based on contribution score
        contribution_factor = agent.contribution_score / 100.0
        base_prob += contribution_factor * 0.1

        return max(0.0, min(1.0, base_prob))

    def _recommend_pd_strategy(self, coop_prob1: float, coop_prob2: float) -> str:
        """Recommend strategy for Prisoner's Dilemma"""
        avg_coop = (coop_prob1 + coop_prob2) / 2

        if avg_coop > 0.7:
            return "cooperate"  # High trust environment
        elif avg_coop > 0.4:
            return "tit_for_tat"  # Mixed strategy
        else:
            return "defect"  # Low trust environment

    def calculate_staking_rewards(self, agent_id: str, time_period_days: int = 30) -> Dict[str, Any]:
        """Calculate staking rewards using game theory"""
        if agent_id not in self.agents:
            raise ValueError("Agent not found")

        agent = self.agents[agent_id]
        stake_amount = agent.stake_amount

        if stake_amount <= 0:
            return {'rewards': 0, 'reason': 'No stake amount'}

        # Base reward calculation
        base_reward = stake_amount * self.staking_reward_rate * (time_period_days / 365)

        # Game theory adjustment based on network participation
        network_participation = self._calculate_network_participation(agent)
        game_multiplier = self._calculate_staking_game_multiplier(agent, network_participation)

        total_reward = base_reward * game_multiplier

        # Calculate opportunity cost (what they could earn elsewhere)
        opportunity_cost = stake_amount * 0.03 * (time_period_days / 365)  # 3% alternative APY

        return {
            'base_reward': base_reward,
            'game_multiplier': game_multiplier,
            'total_reward': total_reward,
            'opportunity_cost': opportunity_cost,
            'net_utility': total_reward - opportunity_cost,
            'staking_strategy': 'optimal' if game_multiplier > 1.0 else 'suboptimal'
        }

    def _calculate_network_participation(self, agent: AgentProfile) -> float:
        """Calculate agent's network participation score"""
        # Simplified calculation based on activity and contributions
        activity_score = 1.0 if agent.last_activity and \
                        (datetime.now() - agent.last_activity).days < 7 else 0.5

        contribution_score = agent.contribution_score / 100.0
        reputation_score = agent.reputation_score / 100.0

        return (activity_score + contribution_score + reputation_score) / 3.0

    def _calculate_staking_game_multiplier(self, agent: AgentProfile, participation: float) -> float:
        """Calculate game theory multiplier for staking rewards"""
        # Higher participation leads to higher rewards (cooperative equilibrium)
        base_multiplier = 1.0

        if participation > 0.8:
            base_multiplier = 1.5  # High participation bonus
        elif participation > 0.6:
            base_multiplier = 1.2  # Medium participation bonus
        elif participation < 0.3:
            base_multiplier = 0.8  # Low participation penalty

        # Risk adjustment based on agent's risk tolerance
        risk_adjustment = 1.0 + (agent.risk_tolerance - 0.5) * 0.2

        return base_multiplier * risk_adjustment

    def simulate_token_economics(self, time_steps: int = 100) -> Dict[str, Any]:
        """Simulate token economics over time using agent-based modeling"""
        simulation_results = {
            'time_series': [],
            'equilibria': [],
            'market_events': []
        }

        # Initialize simulation state
        token_prices = {token_type: metrics.price for token_type, metrics in self.tokens.items()}
        agent_balances = {agent_id: agent.balance.copy() for agent_id, agent in self.agents.items()}

        for step in range(time_steps):
            step_data = {
                'step': step,
                'token_prices': token_prices.copy(),
                'total_value_locked': sum(
                    sum(balances.values()) for balances in agent_balances.values()
                ),
                'active_agents': len([a for a in self.agents.values() if a.last_activity and
                                    (datetime.now() - a.last_activity).days < 30])
            }

            # Simulate market dynamics
            token_prices = self._simulate_market_dynamics(token_prices, step)

            # Simulate agent interactions
            agent_balances = self._simulate_agent_interactions(agent_balances, step)

            # Check for economic equilibria
            if step % 10 == 0:  # Check every 10 steps
                equilibrium = self._detect_economic_equilibrium(token_prices, agent_balances)
                if equilibrium:
                    simulation_results['equilibria'].append({
                        'step': step,
                        'equilibrium': equilibrium
                    })

            simulation_results['time_series'].append(step_data)

        return simulation_results

    def _simulate_market_dynamics(self, prices: Dict[TokenType, float], step: int) -> Dict[TokenType, float]:
        """Simulate market price dynamics"""
        new_prices = {}

        for token_type, price in prices.items():
            # Random walk with mean reversion
            drift = 0.001  # Slight upward drift
            volatility = self.volatility_factor

            # Price elasticity effect
            supply_pressure = np.random.normal(0, 0.1)
            price_change = drift + volatility * np.random.normal() - self.price_elasticity * supply_pressure

            new_price = price * (1 + price_change)
            new_prices[token_type] = max(0.001, new_price)  # Floor price at 0.001

        return new_prices

    def _simulate_agent_interactions(self, balances: Dict[str, Dict[TokenType, float]], step: int) -> Dict[str, Dict[TokenType, float]]:
        """Simulate agent-to-agent economic interactions"""
        new_balances = {}

        for agent_id, balance in balances.items():
            new_balance = balance.copy()

            # Random trading activity
            if np.random.random() < 0.1:  # 10% chance of trade per step
                trade_amount = np.random.uniform(10, 100)
                from_token = np.random.choice(list(TokenType))
                to_token = np.random.choice([t for t in TokenType if t != from_token])

                if new_balance[from_token] >= trade_amount:
                    new_balance[from_token] -= trade_amount
                    new_balance[to_token] += trade_amount * 0.95  # 5% fee

            # Staking rewards
            if np.random.random() < 0.05:  # 5% chance of staking activity
                stake_amount = np.random.uniform(100, 1000)
                if new_balance[TokenType.UTILITY] >= stake_amount:
                    new_balance[TokenType.UTILITY] -= stake_amount
                    new_balance[TokenType.STAKING] += stake_amount

            new_balances[agent_id] = new_balance

        return new_balances

    def _detect_economic_equilibrium(self, prices: Dict[TokenType, float],
                                   balances: Dict[str, Dict[TokenType, float]]) -> Optional[Dict[str, Any]]:
        """Detect if the system has reached economic equilibrium"""
        # Simplified equilibrium detection
        # In a real implementation, this would use more sophisticated economic indicators

        total_value = sum(sum(balance.values()) for balance in balances.values())
        price_stability = np.std(list(prices.values()))

        # Check for price stability (low volatility)
        if price_stability < 0.05:
            return {
                'type': 'price_stability',
                'total_value_locked': total_value,
                'price_volatility': price_stability,
                'description': 'Market prices have stabilized'
            }

        # Check for balanced token distribution
        token_totals = defaultdict(float)
        for balance in balances.values():
            for token_type, amount in balance.items():
                token_totals[token_type] += amount

        distribution_entropy = self._calculate_distribution_entropy(list(token_totals.values()))
        if distribution_entropy > 0.8:  # High entropy = balanced distribution
            return {
                'type': 'balanced_distribution',
                'distribution_entropy': distribution_entropy,
                'description': 'Token distribution is well-balanced'
            }

        return None

    def _calculate_distribution_entropy(self, values: List[float]) -> float:
        """Calculate Shannon entropy of a distribution"""
        total = sum(values)
        if total == 0:
            return 0.0

        probabilities = [v/total for v in values]
        entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)

        # Normalize by maximum possible entropy
        max_entropy = math.log2(len(values))
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def calculate_network_utility(self) -> Dict[str, Any]:
        """Calculate overall network utility using game theory"""
        if not self.agents:
            return {'network_utility': 0, 'reason': 'No agents registered'}

        # Calculate individual utilities
        agent_utilities = {}
        for agent_id, agent in self.agents.items():
            utility = self._calculate_agent_utility(agent)
            agent_utilities[agent_id] = utility

        # Calculate network-level metrics
        total_utility = sum(agent_utilities.values())
        avg_utility = total_utility / len(agent_utilities)

        # Calculate Pareto efficiency
        pareto_efficient = self._check_pareto_efficiency(agent_utilities)

        # Calculate Nash equilibrium status
        nash_status = self._analyze_network_nash_equilibrium()

        return {
            'total_network_utility': total_utility,
            'average_agent_utility': avg_utility,
            'pareto_efficient': pareto_efficient,
            'nash_equilibrium_reached': nash_status['reached'],
            'agent_utilities': agent_utilities,
            'network_health_score': self._calculate_network_health_score(agent_utilities, nash_status)
        }

    def _calculate_agent_utility(self, agent: AgentProfile) -> float:
        """Calculate utility for an individual agent"""
        # Utility = balance_value + reputation_bonus + contribution_bonus - risk_penalty
        balance_value = sum(amount * self.tokens[token_type].price
                          for token_type, amount in agent.balance.items())

        reputation_bonus = agent.reputation_score * 10
        contribution_bonus = agent.contribution_score * 5
        risk_penalty = agent.risk_tolerance * balance_value * 0.1  # Risk-adjusted penalty

        return balance_value + reputation_bonus + contribution_bonus - risk_penalty

    def _check_pareto_efficiency(self, agent_utilities: Dict[str, float]) -> bool:
        """Check if current allocation is Pareto efficient"""
        # Simplified check: if any agent can be made better off without making others worse
        # In practice, this requires checking all possible reallocations
        utilities = list(agent_utilities.values())

        # Check if utilities are reasonably balanced (simplified Pareto check)
        avg_utility = sum(utilities) / len(utilities)
        max_deviation = max(abs(u - avg_utility) for u in utilities) / avg_utility

        return max_deviation < 0.5  # Within 50% of average

    def _analyze_network_nash_equilibrium(self) -> Dict[str, Any]:
        """Analyze if network has reached Nash equilibrium"""
        # Simplified analysis: check if agents are satisfied with current strategies
        satisfied_agents = 0

        for agent in self.agents.values():
            # Agent is satisfied if their utility is above threshold
            utility = self._calculate_agent_utility(agent)
            threshold = 1000  # Arbitrary threshold

            if utility > threshold:
                satisfied_agents += 1

        satisfaction_ratio = satisfied_agents / len(self.agents) if self.agents else 0

        return {
            'reached': satisfaction_ratio > 0.8,  # 80% of agents satisfied
            'satisfaction_ratio': satisfaction_ratio,
            'satisfied_agents': satisfied_agents,
            'total_agents': len(self.agents)
        }

    def _calculate_network_health_score(self, agent_utilities: Dict[str, float],
                                      nash_status: Dict[str, Any]) -> float:
        """Calculate overall network health score"""
        # Combine multiple factors
        utility_score = min(100, sum(agent_utilities.values()) / len(agent_utilities) / 10)
        nash_score = 100 if nash_status['reached'] else 50
        participation_score = len(self.agents) * 2  # More agents = healthier network

        # Weighted average
        health_score = (utility_score * 0.4 + nash_score * 0.4 + participation_score * 0.2)
        return min(100, max(0, health_score))

# Global tokenomics engine instance
tokenomics_instance = None

def get_tokenomics_engine() -> TokenomicsEngine:
    """Get global tokenomics engine instance"""
    global tokenomics_instance
    if tokenomics_instance is None:
        tokenomics_instance = TokenomicsEngine()
    return tokenomics_instance

if __name__ == '__main__':
    # Demo
    engine = get_tokenomics_engine()

    print("💰 Tokenomics Engine Demo")
    print("=" * 50)

    # Register sample agents
    agent1 = engine.register_agent("node_001", EconomicAgent.NODE, {TokenType.UTILITY: 5000, TokenType.GOVERNANCE: 1000})
    agent2 = engine.register_agent("user_001", EconomicAgent.USER, {TokenType.UTILITY: 2000, TokenType.REWARD: 500})

    print("✅ Sample agents registered")

    # Analyze Prisoner's Dilemma
    pd_analysis = engine.analyze_prisoners_dilemma("node_001", "user_001")
    print(f"🎲 PD Analysis: Recommended strategy = {pd_analysis['recommended_strategy']}")

    # Calculate staking rewards
    staking_rewards = engine.calculate_staking_rewards("node_001")
    print(".2f"
    # Calculate network utility
    network_utility = engine.calculate_network_utility()
    print(f"🌐 Network Utility: ${network_utility['total_network_utility']:.2f}")
    print("🎉 Tokenomics Engine Demo completed!")