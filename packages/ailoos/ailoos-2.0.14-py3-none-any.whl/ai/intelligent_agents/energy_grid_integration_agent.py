import logging
import random
from typing import Dict, Any, Optional
from infrastructure.energy_module.energy_market_integration import EnergyMarketIntegrator
from intelligent_agents.energy_optimization_agent import EnergyOptimizationAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnergyGridIntegrationAgent:
    """
    Agente inteligente que simula la integración con la red eléctrica inteligente
    para optimizar el consumo de energía de los nodos en tiempo real.
    """
    def __init__(self, 
                 energy_market_integrator: EnergyMarketIntegrator, 
                 energy_optimization_agent: EnergyOptimizationAgent):
        self.energy_market_integrator = energy_market_integrator
        self.energy_optimization_agent = energy_optimization_agent
        logger.info("EnergyGridIntegrationAgent inicializado.")

    def get_grid_status(self) -> Dict[str, Any]:
        """
        Simula la obtención del estado actual de la red eléctrica.
        """
        renewable_percentage = random.uniform(0.2, 0.9)
        grid_stability = random.choice(["stable", "unstable", "stressed"])
        logger.info(f"Estado de la red: Renovables {renewable_percentage:.1%}, Estabilidad: {grid_stability}.")
        return {"renewable_percentage": renewable_percentage, "grid_stability": grid_stability}

    def adjust_node_consumption(self, node_id: str, current_consumption_kwh: float):
        """
        Ajusta el consumo de energía de un nodo basándose en el estado de la red.
        """
        grid_status = self.get_grid_status()
        current_price = self.energy_market_integrator.get_current_energy_price("off_peak_hour") # Usar un precio base

        if grid_status["grid_stability"] == "stressed" or current_price > 0.20: # Precio alto o red estresada
            logger.warning(f"Agente de Integración con Red: Red estresada o precio alto para {node_id}. Reduciendo consumo.")
            # Simular reducción de consumo
            self.energy_optimization_agent.advise_task_pausing(node_id, current_price) # Aconsejar pausar tareas
            return current_consumption_kwh * 0.8 # Reducir 20%
        elif grid_status["renewable_percentage"] > 0.7 and current_price < 0.10: # Mucha renovable y precio bajo
            logger.info(f"Agente de Integración con Red: Excedente renovable y precio bajo para {node_id}. Aumentando consumo.")
            # Simular aumento de consumo (e.g., para tareas de baja prioridad o almacenamiento de energía)
            return current_consumption_kwh * 1.2 # Aumentar 20%
        else:
            logger.info(f"Nodo {node_id}: Consumo normal. Estado de la red equilibrado.")
            return current_consumption_kwh

if __name__ == "__main__":
    # Inicializar dependencias simuladas
    from infrastructure.control.scheduler import TrainingScheduler
    scheduler = TrainingScheduler()
    energy_optimization_agent = EnergyOptimizationAgent(scheduler)
    energy_market_integrator = EnergyMarketIntegrator(energy_optimization_agent)

    agent = EnergyGridIntegrationAgent(energy_market_integrator, energy_optimization_agent)

    # Registrar un nodo para la simulación
    scheduler.register_node("node_grid_test", 100.0)
    energy_optimization_agent.update_energy_data("node_grid_test", 0.15, 0.4) # Datos iniciales

    # Simular ajuste de consumo
    logger.info("\nSimulando ajuste de consumo de energía...")
    initial_consumption = 50.0 # kWh
    adjusted_consumption = agent.adjust_node_consumption("node_grid_test", initial_consumption)
    logger.info(f"Consumo inicial: {initial_consumption:.2f} kWh, Consumo ajustado: {adjusted_consumption:.2f} kWh.")

    logger.info("energy_grid_integration_agent.py implementado y listo para simular la integración con la red eléctrica.")
