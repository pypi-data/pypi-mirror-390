"""
DRACMA reward distribution system with smart contracts integration.
Handles automatic distribution of rewards to participating nodes.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from web3 import Web3
from web3.contract import Contract
try:
    from web3.middleware import geth_poa_middleware
except ImportError:
    # Fallback for newer web3 versions
    from web3.middleware import ExtraDataToPOAMiddleware as geth_poa_middleware
import os

from .drachma_calculator import RewardCalculation, DrachmaCalculator
from ..core.config import Config
from ..utils.logging import AiloosLogger


@dataclass
class DistributionTransaction:
    """Represents a reward distribution transaction."""
    tx_hash: str
    node_id: str
    drachma_amount: float
    session_id: str
    block_number: int
    timestamp: datetime
    gas_used: int
    status: str  # 'pending', 'confirmed', 'failed'


@dataclass
class NodeBalance:
    """Node's DRACMA balance and transaction history."""
    node_id: str
    balance: float
    total_earned: float
    total_withdrawn: float
    last_updated: datetime
    transaction_count: int


class RewardDistribution:
    """Handles DRACMA token distribution via smart contracts."""

    def __init__(self, config: Config, calculator: DrachmaCalculator):
        self.config = config
        self.calculator = calculator
        self.logger = AiloosLogger(__name__)

        # Blockchain configuration
        self.rpc_url = config.get('blockchain_rpc_url', 'https://polygon-rpc.com/')
        self.chain_id = config.get('chain_id', 137)  # Polygon mainnet
        self.contract_address = config.get('drachma_contract_address')
        self.private_key = config.get('distribution_private_key')

        # Web3 setup
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if self.chain_id == 137:  # Polygon
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Contract setup
        self.contract: Optional[Contract] = None
        if self.contract_address:
            self.contract = self._load_contract()

        # Distribution tracking
        self.pending_distributions: Dict[str, DistributionTransaction] = {}
        self.completed_distributions: List[DistributionTransaction] = []
        self.node_balances: Dict[str, NodeBalance] = {}

        # Distribution settings
        self.batch_size = config.get('distribution_batch_size', 50)
        self.gas_limit = config.get('gas_limit', 200000)
        self.confirmation_blocks = config.get('confirmation_blocks', 12)

    def _load_contract(self) -> Contract:
        """Load DRACMA smart contract."""
        try:
            # DRACMA contract ABI (simplified)
            contract_abi = [
                {
                    "inputs": [
                        {"internalType": "address", "name": "recipient", "type": "address"},
                        {"internalType": "uint256", "name": "amount", "type": "uint256"}
                    ],
                    "name": "mintReward",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"internalType": "address", "name": "account", "type": "address"}
                    ],
                    "name": "balanceOf",
                    "outputs": [
                        {"internalType": "uint256", "name": "", "type": "uint256"}
                    ],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [],
                    "name": "totalSupply",
                    "outputs": [
                        {"internalType": "uint256", "name": "", "type": "uint256"}
                    ],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]

            return self.w3.eth.contract(
                address=self.w3.to_checksum_address(self.contract_address),
                abi=contract_abi
            )

        except Exception as e:
            self.logger.error(f"Error loading contract: {e}")
            return None

    def _node_id_to_address(self, node_id: str) -> str:
        """Convert node ID to blockchain address."""
        # In a real implementation, nodes would have registered addresses
        # For demo, we'll derive address from node_id hash
        import hashlib
        node_hash = hashlib.sha256(node_id.encode()).hexdigest()
        # Take first 20 bytes as mock address
        address = '0x' + node_hash[:40]
        return self.w3.to_checksum_address(address)

    async def distribute_rewards(self, calculations: List[RewardCalculation]) -> List[DistributionTransaction]:
        """Distribute rewards to nodes via smart contracts."""
        if not self.contract or not self.private_key:
            self.logger.warning("Smart contract not configured, using mock distribution")
            return await self._mock_distribute_rewards(calculations)

        try:
            transactions = []

            # Process in batches to avoid gas limits
            for i in range(0, len(calculations), self.batch_size):
                batch = calculations[i:i + self.batch_size]
                batch_transactions = await self._distribute_batch(batch)
                transactions.extend(batch_transactions)

                # Small delay between batches
                await asyncio.sleep(1)

            self.logger.info(f"Distributed rewards to {len(calculations)} nodes in {len(transactions)} transactions")
            return transactions

        except Exception as e:
            self.logger.error(f"Error distributing rewards: {e}")
            return []

    async def _distribute_batch(self, calculations: List[RewardCalculation]) -> List[DistributionTransaction]:
        """Distribute a batch of rewards."""
        transactions = []

        for calc in calculations:
            try:
                tx = await self._distribute_single_reward(calc)
                if tx:
                    transactions.append(tx)
                    self.pending_distributions[tx.tx_hash] = tx

            except Exception as e:
                self.logger.error(f"Error distributing to node {calc.node_id}: {e}")

        return transactions

    async def _distribute_single_reward(self, calculation: RewardCalculation) -> Optional[DistributionTransaction]:
        """Distribute reward to a single node."""
        try:
            # Convert DRACMA to smallest unit (assuming 18 decimals)
            amount_wei = int(calculation.drachma_amount * (10 ** 18))

            # Get recipient address
            recipient_address = self._node_id_to_address(calculation.node_id)

            # Build transaction
            account = self.w3.eth.account.from_key(self.private_key)
            nonce = self.w3.eth.get_transaction_count(account.address)

            tx = self.contract.functions.mintReward(
                recipient_address,
                amount_wei
            ).build_transaction({
                'chainId': self.chain_id,
                'gas': self.gas_limit,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # Create transaction record
            transaction = DistributionTransaction(
                tx_hash=tx_hash.hex(),
                node_id=calculation.node_id,
                drachma_amount=calculation.drachma_amount,
                session_id=calculation.session_id,
                block_number=0,  # Will be updated when confirmed
                timestamp=datetime.now(),
                gas_used=0,  # Will be updated when confirmed
                status='pending'
            )

            self.logger.info(f"Sent reward transaction {tx_hash.hex()} for {calculation.drachma_amount} DRACMA to {calculation.node_id}")

            return transaction

        except Exception as e:
            self.logger.error(f"Error creating reward transaction for {calculation.node_id}: {e}")
            return None

    async def _mock_distribute_rewards(self, calculations: List[RewardCalculation]) -> List[DistributionTransaction]:
        """Mock distribution for testing/development."""
        transactions = []

        for calc in calculations:
            # Create mock transaction
            mock_tx_hash = f"mock_{calc.node_id}_{calc.session_id}_{int(datetime.now().timestamp())}"

            transaction = DistributionTransaction(
                tx_hash=mock_tx_hash,
                node_id=calc.node_id,
                drachma_amount=calc.drachma_amount,
                session_id=calc.session_id,
                block_number=12345,  # Mock block
                timestamp=datetime.now(),
                gas_used=21000,  # Mock gas
                status='confirmed'
            )

            transactions.append(transaction)

            # Update mock balance
            if calc.node_id not in self.node_balances:
                self.node_balances[calc.node_id] = NodeBalance(
                    node_id=calc.node_id,
                    balance=0.0,
                    total_earned=0.0,
                    total_withdrawn=0.0,
                    last_updated=datetime.now(),
                    transaction_count=0
                )

            balance = self.node_balances[calc.node_id]
            balance.balance += calc.drachma_amount
            balance.total_earned += calc.drachma_amount
            balance.last_updated = datetime.now()
            balance.transaction_count += 1

            self.logger.info(f"Mock distributed {calc.drachma_amount} DRACMA to {calc.node_id}")

        return transactions

    async def confirm_transactions(self):
        """Check and confirm pending transactions."""
        if not self.contract:
            return

        try:
            confirmed = []

            for tx_hash, transaction in self.pending_distributions.items():
                try:
                    # Get transaction receipt
                    receipt = self.w3.eth.get_transaction_receipt(tx_hash)

                    if receipt and receipt['status'] == 1:
                        # Transaction confirmed
                        transaction.status = 'confirmed'
                        transaction.block_number = receipt['blockNumber']
                        transaction.gas_used = receipt['gasUsed']

                        # Update node balance
                        await self._update_node_balance(transaction.node_id)

                        confirmed.append(transaction)
                        self.completed_distributions.append(transaction)

                        self.logger.info(f"Confirmed transaction {tx_hash} for {transaction.drachma_amount} DRACMA")

                    elif receipt and receipt['status'] == 0:
                        # Transaction failed
                        transaction.status = 'failed'
                        self.logger.error(f"Transaction {tx_hash} failed")

                except Exception as e:
                    # Transaction might still be pending
                    self.logger.debug(f"Transaction {tx_hash} still pending: {e}")

            # Remove confirmed transactions from pending
            for tx in confirmed:
                del self.pending_distributions[tx.tx_hash]

        except Exception as e:
            self.logger.error(f"Error confirming transactions: {e}")

    async def _update_node_balance(self, node_id: str):
        """Update node's balance from blockchain."""
        if not self.contract:
            return

        try:
            address = self._node_id_to_address(node_id)
            balance_wei = self.contract.functions.balanceOf(address).call()
            balance = balance_wei / (10 ** 18)  # Convert from wei

            if node_id not in self.node_balances:
                self.node_balances[node_id] = NodeBalance(
                    node_id=node_id,
                    balance=0.0,
                    total_earned=0.0,
                    total_withdrawn=0.0,
                    last_updated=datetime.now(),
                    transaction_count=0
                )

            self.node_balances[node_id].balance = balance
            self.node_balances[node_id].last_updated = datetime.now()

        except Exception as e:
            self.logger.error(f"Error updating balance for {node_id}: {e}")

    def get_node_balance(self, node_id: str) -> Optional[NodeBalance]:
        """Get current balance for a node."""
        return self.node_balances.get(node_id)

    def get_pending_distributions(self) -> List[DistributionTransaction]:
        """Get all pending distributions."""
        return list(self.pending_distributions.values())

    def get_completed_distributions(self, node_id: Optional[str] = None) -> List[DistributionTransaction]:
        """Get completed distributions, optionally filtered by node."""
        distributions = self.completed_distributions
        if node_id:
            distributions = [d for d in distributions if d.node_id == node_id]
        return distributions

    async def get_total_supply(self) -> float:
        """Get total DRACMA supply."""
        if not self.contract:
            return 0.0

        try:
            total_wei = self.contract.functions.totalSupply().call()
            return total_wei / (10 ** 18)
        except Exception as e:
            self.logger.error(f"Error getting total supply: {e}")
            return 0.0

    async def start_monitoring(self):
        """Start background monitoring of transactions and balances."""
        asyncio.create_task(self._monitoring_loop())

    async def _monitoring_loop(self):
        """Background loop for monitoring transactions."""
        while True:
            try:
                await self.confirm_transactions()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)

    def get_distribution_stats(self) -> Dict[str, Any]:
        """Get distribution statistics."""
        total_distributed = sum(tx.drachma_amount for tx in self.completed_distributions)
        total_transactions = len(self.completed_distributions)
        pending_count = len(self.pending_distributions)

        return {
            'total_distributed_drachma': total_distributed,
            'total_transactions': total_transactions,
            'pending_transactions': pending_count,
            'unique_nodes': len(self.node_balances),
            'average_reward': total_distributed / max(total_transactions, 1)
        }