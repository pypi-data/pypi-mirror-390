import logging
import random
from typing import Dict, Any, List, Optional
from infrastructure.control.scheduler import TrainingScheduler
from models.lifecycle.model_version_manager import ModelVersionManager
from infrastructure.control.dao_governance.onchain_governance_interface import OnchainGovernanceInterface

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelFineTuningAgent:
    """
    Agente inteligente que gestiona el fine-tuning de modelos en la red P2P.
    Permite a los usuarios o a la DAO proponer y ejecutar tareas de fine-tuning
    en modelos específicos utilizando datasets especializados.
    """
    def __init__(self, 
                 scheduler: TrainingScheduler, 
                 model_version_manager: ModelVersionManager, 
                 governance_interface: OnchainGovernanceInterface):
        self.scheduler = scheduler
        self.model_version_manager = model_version_manager
        self.governance_interface = governance_interface
        self.fine_tuning_tasks: Dict[str, Dict[str, Any]] = {}
        logger.info("ModelFineTuningAgent inicializado.")

    def propose_fine_tuning(self, 
                            proposer_address: str, 
                            model_id: str, 
                            base_version_id: str, 
                            dataset_id: str, 
                            description: str) -> Optional[str]:
        """
        Propone una tarea de fine-tuning a través del sistema de gobernanza DAO.
        """
        proposal_title = f"Fine-tuning de {model_id} (v{base_version_id}) con {dataset_id}"
        proposal_description = f"Propuesta de fine-tuning: {description}. Modelo base: {model_id} v{base_version_id}, Dataset: {dataset_id}."
        
        # Requiere aprobación de la DAO
        proposal_id = self.governance_interface.create_proposal(
            proposer_address,
            proposal_title,
            proposal_description,
            required_dracmas_stake=500 # Stake para propuestas de fine-tuning
        )

        if proposal_id:
            self.fine_tuning_tasks[proposal_id] = {
                "proposer": proposer_address,
                "model_id": model_id,
                "base_version_id": base_version_id,
                "dataset_id": dataset_id,
                "description": description,
                "status": "pending_dao_approval",
                "assigned_nodes": []
            }
            logger.info(f"Propuesta de fine-tuning creada para {model_id} v{base_version_id} con dataset {dataset_id}. ID: {proposal_id}.")
        else:
            logger.error(f"Fallo al crear la propuesta de fine-tuning para {model_id}.")
        return proposal_id

    def execute_fine_tuning(self, proposal_id: str, num_nodes: int = 5) -> bool:
        """
        Ejecuta la tarea de fine-tuning en nodos seleccionados si la propuesta es aprobada.
        """
        task = self.fine_tuning_tasks.get(proposal_id)
        if not task:
            logger.warning(f"Tarea de fine-tuning {proposal_id} no encontrada.")
            return False

        gov_status = self.governance_interface.get_proposal_status(proposal_id)
        if not gov_status or gov_status["status"] != "passed":
            logger.warning(f"Propuesta de fine-tuning {proposal_id} no aprobada por la DAO.")
            return False

        if task["status"] != "pending_dao_approval":
            logger.warning(f"Tarea de fine-tuning {proposal_id} ya está en progreso o completada.")
            return False

        # Seleccionar nodos para fine-tuning (simplificado)
        eligible_nodes = self.scheduler.get_active_nodes()
        if len(eligible_nodes) < num_nodes:
            logger.warning(f"No hay suficientes nodos activos ({len(eligible_nodes)}) para el fine-tuning ({num_nodes} requeridos).")
            return False
        
        selected_nodes = random.sample(eligible_nodes, num_nodes)
        task["assigned_nodes"] = [node.node_id for node in selected_nodes]
        task["status"] = "in_progress"

        logger.info(f"Iniciando fine-tuning para la propuesta {proposal_id} en nodos: {task['assigned_nodes']}.")
        # En un escenario real, se distribuirían los datos y el modelo a estos nodos
        # y se iniciaría el proceso de entrenamiento local.

        # Simular el monitoreo y la finalización del fine-tuning
        import time
        time.sleep(random.uniform(5, 10)) # Simular tiempo de fine-tuning
        task["status"] = "completed"
        logger.info(f"Fine-tuning para la propuesta {proposal_id} completado.")

        # Registrar la nueva versión del modelo fine-tuned
        new_version_id = f"{task['base_version_id']}_ft_{int(time.time())}"
        self.model_version_manager.register_version(
            new_version_id,
            ipfs_cid=f"cid_ft_{proposal_id}", # Simulado
            zk_proof_hash=f"zk_ft_{proposal_id}", # Simulado
            training_params={'fine_tuning_epochs': 1, 'dataset': task['dataset_id']},
            dataset_hash=task['dataset_id'],
            status="testing",
            metadata={'fine_tuning_proposal_id': proposal_id}
        )
        logger.info(f"Nueva versión de modelo fine-tuned registrada: {new_version_id}.")
        return True

if __name__ == "__main__":
    # Inicializar dependencias simuladas
    from infrastructure.control.dao_governance.onchain_governance_interface import DracmasClient
    scheduler = TrainingScheduler()
    model_version_manager = ModelVersionManager()
    dracmas_client = DracmasClient(initial_supply=1000000)
    governance_interface = OnchainGovernanceInterface(dracmas_client)

    # Registrar algunos nodos en el scheduler
    scheduler.register_node("node_FT_1", 100.0)
    scheduler.register_node("node_FT_2", 80.0)
    scheduler.register_node("node_FT_3", 120.0)
    scheduler.register_node("node_FT_4", 90.0)
    scheduler.register_node("node_FT_5", 70.0)

    # Registrar una versión base del modelo
    model_version_manager.register_version("EmpoorioLM_base_v1", "cid_base_v1", "zk_base_v1", {}, "dataset_base", "stable")

    agent = ModelFineTuningAgent(scheduler, model_version_manager, governance_interface)

    # Dar DracmaS al proponente
    proposer_ft = "0xProposerFT"
    dracmas_client.mint(proposer_ft, 1000)

    # Proponer una tarea de fine-tuning
    proposal_id_ft = agent.propose_fine_tuning(
        proposer_ft,
        "EmpoorioLM",
        "EmpoorioLM_base_v1",
        "Medical_Dataset_v1",
        "Fine-tuning para especializar el modelo en terminología médica."
    )

    if proposal_id_ft:
        logger.info(f"\nPropuesta de fine-tuning creada: {proposal_id_ft}")

        # Simular aprobación de la DAO (votos)
        dracmas_client.mint("0xVoterFT1", 10000)
        dracmas_client.mint("0xVoterFT2", 15000)
        governance_interface.vote_on_proposal("0xVoterFT1", proposal_id_ft, "for")
        governance_interface.vote_on_proposal("0xVoterFT2", proposal_id_ft, "for")
        governance_interface.finalize_proposal(proposal_id_ft, min_votes=20000, min_for_ratio=0.51)

        # Ejecutar el fine-tuning
        agent.execute_fine_tuning(proposal_id_ft, num_nodes=3)

    logger.info("model_fine_tuning_agent.py implementado y listo para gestionar el fine-tuning de modelos.")
