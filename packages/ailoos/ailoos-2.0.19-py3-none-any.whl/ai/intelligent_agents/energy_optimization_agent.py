import logging
import random
from typing import Dict, Any, List
from infrastructure.control.scheduler import TrainingScheduler # Para influir en la asignación de tareas

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnergyOptimizationAgent:
    """
    Agente inteligente que optimiza la asignación de tareas basándose en métricas energéticas
    (costo, intensidad de carbono) para promover la sostenibilidad y eficiencia.
    """
    def __init__(self, scheduler: TrainingScheduler):
        self.scheduler = scheduler
        self.energy_data: Dict[str, Dict[str, float]] = {} # {node_id: {"cost_per_kwh": X, "carbon_intensity": Y}}
        logger.info("EnergyOptimizationAgent inicializado.")

    def update_energy_data(self, node_id: str, cost_per_kwh: float, carbon_intensity: float):
        """
        Actualiza los datos energéticos para un nodo específico.
        """
        self.energy_data[node_id] = {"cost_per_kwh": cost_per_kwh, "carbon_intensity": carbon_intensity}
        logger.debug(f"Datos energéticos actualizados para {node_id}: Costo={cost_per_kwh}, Carbono={carbon_intensity}.")

    def get_optimal_nodes_for_task(self, task_capacity_needed: float) -> List[str]:
        """
        Sugiere los nodos más óptimos para una tarea basándose en la energía y la capacidad.
        Prioriza nodos activos con menor costo y menor intensidad de carbono.
        """
        active_nodes = self.scheduler.get_active_nodes() # Obtener nodos activos del scheduler
        
        if not active_nodes:
            logger.warning("No hay nodos activos para optimización energética.")
            return []

        # Filtrar nodos que pueden manejar la capacidad requerida (simplificado)
        eligible_nodes = [node for node in active_nodes if node.capacity >= task_capacity_needed]
        
        if not eligible_nodes:
            logger.warning(f"No hay nodos elegibles con capacidad suficiente ({task_capacity_needed}) para la tarea.")
            return []

        # Ordenar nodos por una métrica combinada de costo y carbono
        # Asumimos que menor costo y menor intensidad de carbono son mejores
        def sort_key(node):
            node_energy_data = self.energy_data.get(node.node_id, {"cost_per_kwh": 999.0, "carbon_intensity": 999.0})
            # Ponderar costo y carbono (ejemplo simple)
            return (node_energy_data["cost_per_kwh"] * 0.7) + (node_energy_data["carbon_intensity"] * 0.3)

        eligible_nodes.sort(key=sort_key)
        
        optimal_nodes = [node.node_id for node in eligible_nodes]
        logger.info(f"Nodos óptimos sugeridos para la tarea ({task_capacity_needed}): {optimal_nodes[:5]}...")
        return optimal_nodes

    def advise_task_pausing(self, node_id: str, current_cost_per_kwh: float, threshold_cost: float = 0.20) -> bool:
        """
        Aconseja pausar tareas en un nodo si el costo energético excede un umbral.
        """
        if current_cost_per_kwh > threshold_cost:
            logger.warning(f"Agente de Optimización Energética: Se recomienda pausar tareas en el nodo {node_id} debido al alto costo energético ({current_cost_per_kwh} > {threshold_cost}).")
            return True
        logger.info(f"Agente de Optimización Energética: No se requiere pausar tareas en el nodo {node_id}. Costo actual: {current_cost_per_kwh}.")
        return False

if __name__ == "__main__":
    # Inicializar un scheduler simulado y registrar algunos nodos
    scheduler = TrainingScheduler()
    scheduler.register_node("node_India", 100.0) # Capacidad en TFLOPs
    scheduler.register_node("node_Ethiopia", 80.0)
    scheduler.register_node("node_Germany", 120.0)
    scheduler.register_node("node_USA", 150.0)

    agent = EnergyOptimizationAgent(scheduler)

    # Actualizar datos energéticos para los nodos
    agent.update_energy_data("node_India", cost_per_kwh=0.08, carbon_intensity=0.4)
    agent.update_energy_data("node_Ethiopia", cost_per_kwh=0.01, carbon_intensity=0.1)
    agent.update_energy_data("node_Germany", cost_per_kwh=0.30, carbon_intensity=0.6)
    agent.update_energy_data("node_USA", cost_per_kwh=0.15, carbon_intensity=0.5)

    # Sugerir nodos óptimos para una tarea
    logger.info("\nSugiriendo nodos óptimos para una tarea de 50 TFLOPs...")
    optimal_nodes = agent.get_optimal_nodes_for_task(50.0)
    logger.info(f"Nodos óptimos: {optimal_nodes}")

    # Aconsejar pausar tareas
    logger.info("\nAconsejando pausar tareas en nodos...")
    agent.advise_task_pausing("node_Germany", 0.35)
    agent.advise_task_pausing("node_Ethiopia", 0.02)

    logger.info("energy_optimization_agent.py implementado y listo para optimizar energéticamente.")