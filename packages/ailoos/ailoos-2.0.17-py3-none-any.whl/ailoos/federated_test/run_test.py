"""
Script principal para ejecutar pruebas de entrenamiento federado.
Configura y ejecuta nodos de prueba en diferentes máquinas.
"""

import asyncio
import logging
import sys
import time
from typing import List, Dict, Any

try:
    from .nodo_simple import SimpleFederatedNode
except ImportError:
    # Para ejecución directa
    from nodo_simple import SimpleFederatedNode


async def run_single_node_test(node_id: str, hardware_type: str) -> Dict[str, Any]:
    """
    Ejecuta una prueba de un solo nodo.

    Args:
        node_id: ID del nodo
        hardware_type: Tipo de hardware

    Returns:
        Resultados de la prueba
    """
    print(f"\n🧪 Ejecutando prueba de nodo único: {node_id} ({hardware_type})")

    # Para pruebas locales, usar localhost
    coordinator_url = "http://localhost:5001"

    # Crear nodo
    node = SimpleFederatedNode(node_id, coordinator_url, hardware_type)

    try:
        # Ejecutar prueba completa
        start_time = time.time()
        results = await node.run_federated_training(num_rounds=3)
        total_time = time.time() - start_time

        results["total_time"] = total_time
        results["node_id"] = node_id
        results["hardware_type"] = hardware_type
        results["status"] = "success"

        print(f"✅ Prueba completada exitosamente en {total_time:.2f}s")
        return results

    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return {
            "node_id": node_id,
            "hardware_type": hardware_type,
            "status": "error",
            "error": str(e)
        }


async def run_multi_node_simulation(num_nodes: int = 2) -> List[Dict[str, Any]]:
    """
    Simula múltiples nodos ejecutándose concurrentemente.
    Útil para pruebas locales antes de usar máquinas físicas.

    Args:
        num_nodes: Número de nodos a simular

    Returns:
        Lista de resultados por nodo
    """
    print(f"\n🎭 Ejecutando simulación multi-nodo: {num_nodes} nodos")

    tasks = []
    hardware_types = ["macbook_2012", "macbook_m4", "macbook_pro", "imac"]

    for i in range(num_nodes):
        node_id = f"node_sim_{i+1}"
        hw_type = hardware_types[i % len(hardware_types)]
        task = run_single_node_test(node_id, hw_type)
        tasks.append(task)

    # Ejecutar todos los nodos concurrentemente
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Procesar resultados
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "node_id": f"node_sim_{i+1}",
                "status": "error",
                "error": str(result)
            })
        else:
            processed_results.append(result)

    return processed_results


async def run_real_hardware_test():
    """
    Configuración para pruebas con hardware real (MacBooks físicos).
    Esta función se ejecutaría en cada MacBook física.
    """
    print("\n🔧 Configuración para pruebas con hardware real")

    # Detectar automáticamente el tipo de hardware
    import platform
    system = platform.system()

    if system == "Darwin":  # macOS
        # Intentar detectar modelo de Mac
        try:
            import subprocess
            result = subprocess.run(['sysctl', 'hw.model'], capture_output=True, text=True)
            model = result.stdout.strip().split(': ')[1]

            if "MacBookPro" in model:
                # Detectar año aproximado por modelo
                if "8" in model or "9" in model or "10" in model:
                    hardware_type = "macbook_2012"
                elif "14" in model or "15" in model:
                    hardware_type = "macbook_m4"
                else:
                    hardware_type = "macbook_unknown"
            else:
                hardware_type = "mac_unknown"
        except:
            hardware_type = "mac_unknown"
    else:
        hardware_type = f"{system}_unknown"

    print(f"🔍 Hardware detectado: {hardware_type}")

    # Generar ID único basado en timestamp y hardware
    node_id = f"{hardware_type}_{int(time.time())}"

    # URL del coordinador (cambiar a Google Cloud en producción)
    coordinator_url = "http://localhost:5001"  # Cambiar a: "http://34.102.XXX.XXX:5000"

    print(f"🌐 Conectando a coordinador: {coordinator_url}")
    print(f"🆔 Node ID: {node_id}")

    # Ejecutar prueba
    results = await run_single_node_test(node_id, hardware_type)

    # Guardar resultados en archivo
    import json
    with open(f"results_{node_id}.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"💾 Resultados guardados en results_{node_id}.json")
    return results


def print_usage():
    """Imprime instrucciones de uso."""
    print("""
🚀 AILOOS FEDERATED TRAINING TEST SUITE
=========================================

Uso: python run_test.py [modo] [opciones]

MODOS:
  single          Ejecuta un solo nodo de prueba
  multi           Simula múltiples nodos concurrentemente
  real            Configuración para hardware real (MacBooks físicos)

EJEMPLOS:

# Prueba de un solo nodo
python run_test.py single node_test_1 macbook_m4

# Simulación multi-nodo (2 nodos)
python run_test.py multi 2

# Configuración para hardware real
python run_test.py real

# Usar valores por defecto
python run_test.py

CONFIGURACIÓN:
- Coordinador: http://localhost:5001 (cambiar para Google Cloud)
- Rondas: 3
- Epochs locales: 2
- Dataset: 500 muestras MNIST por nodo

RESULTADOS:
- Se guardan automáticamente en archivos JSON
- Incluyen métricas de rendimiento y tiempo
""")


async def main():
    """Función principal."""
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Parsear argumentos
    args = sys.argv[1:]

    if len(args) == 0:
        # Modo por defecto: simulación multi-nodo
        print("🎯 Ejecutando modo por defecto: simulación multi-nodo")
        results = await run_multi_node_simulation(2)

    elif args[0] == "single":
        # Modo single node
        if len(args) >= 3:
            node_id = args[1]
            hardware_type = args[2]
        else:
            node_id = f"node_single_{int(time.time())}"
            hardware_type = "macbook_unknown"

        results = [await run_single_node_test(node_id, hardware_type)]

    elif args[0] == "multi":
        # Modo multi-nodo
        num_nodes = int(args[1]) if len(args) > 1 else 2
        results = await run_multi_node_simulation(num_nodes)

    elif args[0] == "real":
        # Modo hardware real
        results = [await run_real_hardware_test()]

    elif args[0] in ["help", "-h", "--help"]:
        print_usage()
        return

    else:
        print(f"❌ Modo desconocido: {args[0]}")
        print_usage()
        return

    # Mostrar resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*60)

    successful_tests = 0
    total_time = 0

    for result in results:
        status = result.get("status", "unknown")
        node_id = result.get("node_id", "unknown")
        hw_type = result.get("hardware_type", "unknown")

        if status == "success":
            successful_tests += 1
            time_taken = result.get("total_time", 0)
            total_time += time_taken
            accuracy = result.get("final_accuracy", 0)

            print(f"✅ {node_id} ({hw_type}): {accuracy:.2f}% acc, {time_taken:.2f}s")
        else:
            error = result.get("error", "Unknown error")
            print(f"❌ {node_id} ({hw_type}): {error}")

    print(f"\n🎯 Tests exitosos: {successful_tests}/{len(results)}")
    if successful_tests > 0:
        print(f"⏱️ Tiempo promedio: {total_time/successful_tests:.2f}s")
        print("🎉 ¡Pruebas de entrenamiento federado completadas!")

    # Guardar resumen completo
    summary = {
        "timestamp": time.time(),
        "total_tests": len(results),
        "successful_tests": successful_tests,
        "results": results
    }

    import json
    with open("federated_test_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("💾 Resumen guardado en federated_test_summary.json")


if __name__ == "__main__":
    asyncio.run(main())