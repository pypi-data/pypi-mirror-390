"""
Node verification system with zero-knowledge proofs.
Provides cryptographic verification of node identity, reputation, and privacy-preserving proofs.
"""

from .node_verifier import (
    NodeVerifier,
    NodeIdentity,
    NodeReputation,
    HardwareVerification,
    VerificationChallenge
)
from .zk_proofs import (
    ZKProofManager,
    ZKProver,
    ZKVerifier,
    ZKProof,
    ContributionProof,
    HardwareProof
)

__all__ = [
    'NodeVerifier',
    'ZKProofManager',
    'NodeIdentity',
    'NodeReputation',
    'HardwareVerification',
    'VerificationChallenge',
    'ZKProver',
    'ZKVerifier',
    'ZKProof',
    'ContributionProof',
    'HardwareProof'
]