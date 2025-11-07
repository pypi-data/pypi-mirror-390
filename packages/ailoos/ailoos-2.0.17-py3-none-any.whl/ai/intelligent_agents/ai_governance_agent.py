import logging
import random
from typing import Dict, Any, Optional
from infrastructure.control.dao_governance.onchain_governance_interface import OnchainGovernanceInterface
from infrastructure.resource_marketplace.dracmas_client import DracmasClient # Para simular el balance del agente

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIGovernanceAgent:
    """
    Agente inteligente que participa en la gobernanza DAO.
    Monitorea propuestas, genera recomendaciones y puede votar automáticamente
    basándose en políticas predefinidas.
    """
    def __init__(self, 
                 agent_address: str, 
                 governance_interface: OnchainGovernanceInterface, 
                 dracmas_client: DracmasClient,
                 policies: Dict[str, Any]):
        self.agent_address = agent_address
        self.governance_interface = governance_interface
        self.dracmas_client = dracmas_client
        self.policies = policies # Políticas de votación (e.g., umbrales de costo, impacto en la red)
        logger.info(f"AIGovernanceAgent inicializado con dirección {agent_address}.")

    def evaluate_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """
        Evalúa una propuesta basándose en las políticas internas del agente.
        """
        proposal_info = self.governance_interface.get_proposal_status(proposal_id)
        if not proposal_info:
            logger.warning(f"Propuesta {proposal_id} no encontrada para evaluar.")
            return {"recommendation": "abstain", "reason": "Propuesta no encontrada."}

        logger.info(f"Evaluando propuesta '{proposal_info['title']}' ({proposal_id})...")

        # Ejemplo de lógica de evaluación basada en políticas
        if "cost_threshold" in self.policies and proposal_info.get("required_dracmas_stake", 0) > self.policies["cost_threshold"]:
            return {"recommendation": "against", "reason": "Costo de stake excede el umbral de la política."}

        if "keywords_for" in self.policies and any(kw in proposal_info["description"].lower() for kw in self.policies["keywords_for"]):
            return {"recommendation": "for", "reason": "Descripción contiene palabras clave positivas."}

        if "keywords_against" in self.policies and any(kw in proposal_info["description"].lower() for kw in self.policies["keywords_against"]):
            return {"recommendation": "against", "reason": "Descripción contiene palabras clave negativas."}

        # Si no hay reglas específicas, abstenerse o votar por defecto
        return {"recommendation": "abstain", "reason": "No hay políticas específicas para esta propuesta."}

    def cast_vote_automatically(self, proposal_id: str) -> bool:
        """
        Emite un voto automático en una propuesta si la recomendación es clara y el agente tiene DracmaS.
        """
        evaluation = self.evaluate_proposal(proposal_id)
        recommendation = evaluation["recommendation"]
        reason = evaluation["reason"]

        if recommendation == "abstain":
            logger.info(f"Agente {self.agent_address} se abstiene de votar en {proposal_id}: {reason}.")
            return False

        agent_balance = self.dracmas_client.get_balance(self.agent_address)
        if agent_balance == 0:
            logger.warning(f"Agente {self.agent_address} no tiene DracmaS para votar en {proposal_id}.")
            return False

        logger.info(f"Agente {self.agent_address} votará '{recommendation.upper()}' en propuesta {proposal_id} (Razón: {reason}).")
        success = self.governance_interface.vote_on_proposal(self.agent_address, proposal_id, recommendation)
        return success

if __name__ == "__main__":
    # Inicializar dependencias simuladas
    dracmas_client = DracmasClient(initial_supply=1000000)
    governance_interface = OnchainGovernanceInterface(dracmas_client)

    # Dirección del agente de gobernanza
    ai_agent_address = "0xAIGovAgent"
    dracmas_client.mint(ai_agent_address, 50000) # Darle DracmaS para votar

    # Políticas de ejemplo para el agente
    agent_policies = {
        "cost_threshold": 200, # No votar a favor de propuestas con stake > 200 DRS
        "keywords_for": ["recompensa", "eficiencia", "escalabilidad"],
        "keywords_against": ["centralización", "riesgo", "costoso"]
    }

    ai_governance_agent = AIGovernanceAgent(ai_agent_address, governance_interface, dracmas_client, agent_policies)

    # Simular creación de propuestas
    proposer_human = "0xHumanProposer"
    dracmas_client.mint(proposer_human, 1000)

    # Propuesta 1: Aprobada por el agente
    prop_id_1 = governance_interface.create_proposal(
        proposer_human,
        "Mejorar eficiencia de recompensas",
        "Proponemos optimizar el algoritmo de recompensas para mayor eficiencia y escalabilidad.",
        required_dracmas_stake=100
    )
    if prop_id_1:
        logger.info(f"\nPropuesta 1 creada: {prop_id_1}")
        ai_governance_agent.cast_vote_automatically(prop_id_1)

    # Propuesta 2: Rechazada por el agente (costo)
    prop_id_2 = governance_interface.create_proposal(
        proposer_human,
        "Construir granja de servidores centralizada",
        "Proponemos construir una granja de servidores centralizada para mayor control, aunque será costoso.",
        required_dracmas_stake=300
    )
    if prop_id_2:
        logger.info(f"\nPropuesta 2 creada: {prop_id_2}")
        ai_governance_agent.cast_vote_automatically(prop_id_2)

    # Propuesta 3: Agente se abstiene
    prop_id_3 = governance_interface.create_proposal(
        proposer_human,
        "Cambiar color del logo",
        "Proponemos cambiar el color del logo de azul a verde.",
        required_dracmas_stake=50
    )
    if prop_id_3:
        logger.info(f"\nPropuesta 3 creada: {prop_id_3}")
        ai_governance_agent.cast_vote_automatically(prop_id_3)

    logger.info("ai_governance_agent.py implementado y listo para la gobernanza de IA.")
