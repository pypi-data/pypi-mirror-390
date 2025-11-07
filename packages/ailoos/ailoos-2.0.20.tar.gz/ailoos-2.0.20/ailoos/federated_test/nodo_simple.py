"""
Nodo simple para pruebas de entrenamiento federado.
Implementa un cliente básico que se conecta al coordinador y participa en rondas de entrenamiento.
"""

import asyncio
import json
import logging
import time
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, Optional, Any, List
import aiohttp

try:
    from .modelo_basico import TinyModel, FederatedMetrics
    from .dataset_reducido import create_federated_datasets, create_data_loaders
except ImportError:
    # Para ejecución directa
    from modelo_basico import TinyModel, FederatedMetrics
    from dataset_reducido import create_federated_datasets, create_data_loaders

logger = logging.getLogger(__name__)


class SimpleFederatedNode:
    """
    Nodo simple para pruebas federadas.
    Se conecta al coordinador y participa en rondas de entrenamiento.
    """

    def __init__(
        self,
        node_id: str,
        coordinator_url: str = "http://34.102.XXX.XXX:5000",  # Google Cloud IP
        hardware_type: str = "unknown"
    ):
        """
        Args:
            node_id: Identificador único del nodo
            coordinator_url: URL del coordinador central
            hardware_type: Tipo de hardware (macbook_2012, macbook_m4, etc.)
        """
        self.node_id = node_id
        self.coordinator_url = coordinator_url
        self.hardware_type = hardware_type
        self.session_id: Optional[str] = None
        self.model = TinyModel()
        self.metrics = FederatedMetrics()
        self.is_registered = False

        # Configuración de entrenamiento
        self.learning_rate = 0.01
        self.batch_size = 32
        self.local_epochs = 2

        logger.info(f"🚀 Nodo {node_id} inicializado ({hardware_type})")

    async def register_with_coordinator(self) -> bool:
        """Registra el nodo con el coordinador central."""
        try:
            payload = {
                "node_id": self.node_id,
                "ip_address": "127.0.0.1",  # En pruebas locales
                "hardware_info": {
                    "cpu": f"Apple M4 ({self.hardware_type})",
                    "ram": "16GB",
                    "gpu": "Integrated" if "m4" in self.hardware_type.lower() else "None",
                    "platform": "macOS"
                },
                "location": "Madrid, Spain"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.coordinator_url}/api/node/register",
                    json=payload
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ Nodo {self.node_id} registrado exitosamente")
                        self.is_registered = True
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"❌ Error registrando nodo: {error}")
                        return False

        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False

    async def start_training_session(self) -> bool:
        """Inicia una sesión de entrenamiento con el coordinador."""
        if not self.is_registered:
            logger.error("❌ Nodo no registrado")
            return False

        try:
            payload = {
                "node_id": self.node_id,
                "session_id": f"session_{int(time.time())}_{self.node_id}",
                "model_version": "1.0.0"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.coordinator_url}/api/training/start",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.session_id = data.get("session_id")
                        logger.info(f"✅ Sesión de entrenamiento iniciada: {self.session_id}")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"❌ Error iniciando sesión: {error}")
                        return False

        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False

    def prepare_local_data(self):
        """Prepara datos locales para el nodo."""
        # Crear dataset pequeño para este nodo
        datasets = create_federated_datasets(
            num_nodes=1,  # Solo este nodo
            samples_per_node=500,
            train=True
        )

        # Crear data loader
        loaders = create_data_loaders(
            datasets,
            batch_size=self.batch_size,
            shuffle=True
        )

        self.train_loader = loaders[0]
        logger.info(f"📊 Datos locales preparados: {len(self.train_loader)} batches")

    def train_local_model(self, global_weights: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """
        Entrena el modelo localmente con pesos globales iniciales.

        Args:
            global_weights: Pesos del modelo global

        Returns:
            Diccionario con pesos actualizados y métricas
        """
        # Cargar pesos globales
        self.model.load_state_dict(global_weights)

        # Configurar optimizador y pérdida
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        criterion = nn.CrossEntropyLoss()

        # Entrenamiento local
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0

        start_time = time.time()

        for epoch in range(self.local_epochs):
            epoch_loss = 0
            epoch_correct = 0
            epoch_total = 0

            for batch_data, batch_labels in self.train_loader:
                optimizer.zero_grad()

                outputs = self.model(batch_data)
                loss = criterion(outputs, batch_labels)

                loss.backward()
                optimizer.step()

                # Métricas
                epoch_loss += loss.item()
                _, predicted = outputs.max(1)
                epoch_total += batch_labels.size(0)
                epoch_correct += predicted.eq(batch_labels).sum().item()

            # Promedios de la época
            avg_loss = epoch_loss / len(self.train_loader)
            accuracy = 100. * epoch_correct / epoch_total

            logger.info(f"   Epoch {epoch+1}/{self.local_epochs}: Loss={avg_loss:.4f}, Acc={accuracy:.2f}%")

            total_loss += avg_loss
            correct += epoch_correct
            total += epoch_total

        training_time = time.time() - start_time
        final_accuracy = 100. * correct / total
        avg_loss = total_loss / self.local_epochs

        logger.info(f"🏁 Entrenamiento local completado: Acc={final_accuracy:.2f}%, Time={training_time:.2f}s")

        return {
            "weights": self.model.state_dict(),
            "accuracy": final_accuracy,
            "loss": avg_loss,
            "training_time": training_time,
            "samples_processed": len(self.train_loader) * self.batch_size
        }

    async def send_weights_to_coordinator(self, local_results: Dict[str, Any]):
        """Envía los pesos entrenados al coordinador."""
        if not self.session_id:
            logger.error("❌ No hay sesión activa")
            return False

        try:
            # Serializar pesos del modelo para envío
            weights_serialized = {}
            for key, tensor in local_results["weights"].items():
                # Convertir tensor a lista para serialización JSON
                weights_serialized[key] = tensor.detach().cpu().numpy().tolist()

            payload = {
                "session_id": self.session_id,
                "node_id": self.node_id,
                "local_weights": weights_serialized,
                "metrics": {
                    "accuracy": local_results["accuracy"],
                    "loss": local_results["loss"],
                    "training_time": local_results["training_time"],
                    "samples_processed": local_results["samples_processed"]
                },
                "hardware_info": {
                    "type": self.hardware_type,
                    "batch_size": self.batch_size,
                    "learning_rate": self.learning_rate
                },
                "status": "completed"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.coordinator_url}/api/training/submit_weights",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Pesos enviados al coordinador - Round: {data.get('round', 'N/A')}")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"❌ Error enviando pesos: {error}")
                        return False

        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False

    async def wait_for_global_weights(self) -> Optional[Dict[str, torch.Tensor]]:
        """Espera pesos globales actualizados del coordinador."""
        if not self.session_id:
            logger.error("❌ No hay sesión activa para recibir pesos globales")
            return None

        logger.info("⏳ Esperando pesos globales del coordinador...")

        try:
            # Polling periódico para obtener pesos globales actualizados
            max_attempts = 30  # Máximo 5 minutos (30 * 10s)
            attempt = 0

            while attempt < max_attempts:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.coordinator_url}/api/training/weights/{self.session_id}"
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            weights_data = data.get("global_weights")

                            if weights_data:
                                # Convertir pesos serializados de vuelta a tensores PyTorch
                                global_weights = {}
                                for key, tensor_data in weights_data.items():
                                    # Asumir que los pesos vienen como listas de números
                                    if isinstance(tensor_data, list):
                                        tensor = torch.tensor(tensor_data)
                                    else:
                                        # Si vienen como bytes serializados o formato diferente
                                        tensor = torch.tensor(tensor_data)
                                    global_weights[key] = tensor

                                logger.info("✅ Pesos globales recibidos del coordinador")
                                return global_weights
                            else:
                                logger.info(f"⏳ Pesos globales no disponibles aún (intento {attempt + 1})")
                        elif response.status == 404:
                            logger.info(f"⏳ Sesión no encontrada, esperando inicialización (intento {attempt + 1})")
                        else:
                            error = await response.text()
                            logger.warning(f"⚠️ Error obteniendo pesos: {error}")

                # Esperar 10 segundos antes del siguiente intento
                await asyncio.sleep(10)
                attempt += 1

            logger.error("❌ Timeout esperando pesos globales del coordinador")
            return None

        except Exception as e:
            logger.error(f"❌ Error recibiendo pesos globales: {e}")
            return None

    async def run_federated_training(self, num_rounds: int = 3):
        """
        Ejecuta el entrenamiento federado completo con lógica real de federated learning.

        Args:
            num_rounds: Número de rondas federadas
        """
        logger.info(f"🚀 Iniciando entrenamiento federado: {num_rounds} rondas")

        # Preparar datos locales
        self.prepare_local_data()

        # Inicializar pesos globales (primera ronda)
        if not hasattr(self, 'global_weights') or self.global_weights is None:
            # Para la primera ronda, inicializar con pesos aleatorios o del modelo base
            self.global_weights = self.model.state_dict()
            logger.info("🎯 Inicializando pesos globales para primera ronda")

        for round_num in range(num_rounds):
            logger.info(f"\n🎯 RONDA {round_num + 1}/{num_rounds}")

            # 1. Recibir pesos globales (desde ronda 2 en adelante)
            if round_num > 0:
                global_weights = await self.wait_for_global_weights()
                if global_weights is None:
                    logger.error("❌ No se pudieron obtener pesos globales")
                    break
                self.global_weights = global_weights

            # 2. Entrenar localmente con pesos globales actuales
            start_time = time.time()
            local_results = self.train_local_model(self.global_weights)
            round_time = time.time() - start_time

            # 3. Registrar métricas
            self.metrics.add_round_metrics(
                round_num + 1,
                local_results["accuracy"],
                local_results["loss"],
                round_time
            )

            # 4. Enviar pesos locales al coordinador para agregación
            success = await self.send_weights_to_coordinator(local_results)
            if not success:
                logger.warning(f"⚠️ Falló envío de pesos en ronda {round_num + 1}, continuando...")

            # 5. Esperar confirmación de que el coordinador recibió los pesos
            await self.wait_for_round_completion(round_num + 1)

        # Mostrar resultados finales
        summary = self.metrics.get_summary()
        logger.info("\n🎉 ENTRENAMIENTO FEDERADO COMPLETADO")
        logger.info(f"📊 Rondas completadas: {summary['total_rounds']}")
        logger.info(f"🎯 Accuracy final: {summary['final_accuracy']:.2f}%")
        logger.info(f"📉 Loss final: {summary['final_loss']:.4f}")
        logger.info(f"⏱️ Tiempo total: {summary['total_time']:.2f}s")
        logger.info(f"📈 Mejor accuracy: {summary['best_accuracy']:.2f}%")

        return summary

    async def wait_for_round_completion(self, round_number: int):
        """Espera confirmación de que la ronda fue completada por el coordinador."""
        try:
            max_attempts = 60  # 10 minutos máximo
            attempt = 0

            while attempt < max_attempts:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                    async with session.get(
                        f"{self.coordinator_url}/api/training/round/{self.session_id}/{round_number}/status"
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get('completed', False):
                                logger.info(f"✅ Ronda {round_number} completada por coordinador")
                                return True
                            else:
                                logger.debug(f"⏳ Ronda {round_number} aún en progreso")
                        elif response.status == 404:
                            # Ronda no existe aún, esperar
                            logger.debug(f"⏳ Ronda {round_number} no disponible aún")
                        else:
                            logger.warning(f"⚠️ Error obteniendo status de ronda: HTTP {response.status}")

                await asyncio.sleep(10)  # Esperar 10 segundos
                attempt += 1

            logger.warning(f"⚠️ Timeout esperando completación de ronda {round_number}")
            return False

        except Exception as e:
            logger.error(f"❌ Error esperando completación de ronda: {e}")
            return False

    async def start(self):
        """Inicia el nodo y comienza el entrenamiento."""
        logger.info(f"🔌 Conectando nodo {self.node_id} al coordinador...")

        # Registrar con coordinador
        if not await self.register_with_coordinator():
            logger.error("❌ Falló registro con coordinador")
            return

        # Iniciar sesión de entrenamiento
        if not await self.start_training_session():
            logger.error("❌ Falló inicio de sesión de entrenamiento")
            return

        # Ejecutar entrenamiento federado
        await self.run_federated_training(num_rounds=3)

        logger.info(f"✅ Nodo {self.node_id} completó su participación")


async def main():
    """Función principal para ejecutar el nodo."""
    import sys

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Obtener ID del nodo desde argumentos
    node_id = sys.argv[1] if len(sys.argv) > 1 else f"node_{int(time.time())}"
    hardware_type = sys.argv[2] if len(sys.argv) > 2 else "macbook_unknown"

    # Para pruebas locales, usar localhost
    coordinator_url = "http://localhost:5001"  # Cambiar a Google Cloud en producción

    # Crear y ejecutar nodo
    node = SimpleFederatedNode(node_id, coordinator_url, hardware_type)
    await node.start()


if __name__ == "__main__":
    asyncio.run(main())