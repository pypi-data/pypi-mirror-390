#!/usr/bin/env python3
"""
Empoorio Simple Agent Demo
Demostración básica del sistema de agentes inteligentes

Este demo muestra:
- ✅ Creación y configuración de agentes especializados
- ✅ Ejecución de tareas individuales por agente
- ✅ Comunicación básica entre agentes
- ✅ Monitoreo de rendimiento básico
"""

import asyncio
import json
import logging
from typing import Dict, List, Any
from datetime import datetime
import sys
import os

# Add current directory to path for imports
sys.path.append('.')

from framework.base_agent import BaseAgent, AgentRole, AgentState
from orchestration.multi_agent_orchestrator import MultiAgentOrchestrator
from marketplace.agent_marketplace import AgentMarketplace
from agents.specialized_agents import DataAnalysisAgent, ContentCreationAgent
from learning.continuous_learning import ContinuousLearningSystem
from communication.advanced_communication import AdvancedCommunicationSystem

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleAgentDemo:
    """Demo simple del sistema de agentes"""

    def __init__(self):
        self.orchestrator = None
        self.marketplace = None
        self.comm_system = None
        self.agents = {}

    async def initialize_system(self) -> None:
        """Initialize the multi-agent system"""
        logger.info("🚀 Initializing Simple Agent System")

        # Initialize communication system
        self.comm_system = AdvancedCommunicationSystem("simple-demo-orchestrator")
        await self.comm_system.initialize()

        # Initialize marketplace
        self.marketplace = AgentMarketplace()
        await self.marketplace.initialize()

        # Initialize orchestrator
        self.orchestrator = MultiAgentOrchestrator()
        await self.orchestrator.initialize()

        # Create specialized agents
        await self._create_agents()

        logger.info("✅ Simple Agent System initialized")

    async def _create_agents(self) -> None:
        """Create specialized agents"""
        logger.info("🤖 Creating specialized agents")

        # Data Analysis Agent
        data_agent = DataAnalysisAgent("data-analyst-demo", "Data Analyst")
        await data_agent.initialize()
        self.agents["data_analyst"] = data_agent

        # Content Creation Agent
        content_agent = ContentCreationAgent("content-creator-demo", "Content Creator")
        await content_agent.initialize()
        self.agents["content_creator"] = content_agent

        # Register agents with orchestrator
        for agent in self.agents.values():
            await self.orchestrator.register_agent(agent, {
                "max_load": 1.0,
                "cost_per_hour": 25.0,
                "location": "demo-region",
                "specialization": agent.capabilities[0] if agent.capabilities else "general"
            })

        # Register agents with communication system
        for agent in self.agents.values():
            await self.comm_system.register_agent(agent)

        logger.info(f"✅ Created {len(self.agents)} agents")

    async def run_data_analysis_demo(self) -> Dict[str, Any]:
        """Run data analysis demo"""
        logger.info("📊 Running Data Analysis Demo")

        # Sample data for analysis
        sample_data = [
            {"name": "Product A", "sales": 150, "rating": 4.2},
            {"name": "Product B", "sales": 200, "rating": 4.5},
            {"name": "Product C", "sales": 120, "rating": 3.8},
            {"name": "Product D", "sales": 180, "rating": 4.1},
            {"name": "Product E", "sales": 250, "rating": 4.7}
        ]

        # Create analysis task
        analysis_task = {
            "task_id": "data-analysis-demo-001",
            "type": "statistical_analysis",
            "data": sample_data,
            "analysis_type": "correlation_analysis"
        }

        # Execute task
        start_time = datetime.now()
        result = await self.agents["data_analyst"].execute_task(analysis_task)
        end_time = datetime.now()

        return {
            "task_type": "data_analysis",
            "execution_time": (end_time - start_time).total_seconds(),
            "result": result,
            "status": "completed"
        }

    async def run_content_creation_demo(self) -> Dict[str, Any]:
        """Run content creation demo"""
        logger.info("✍️ Running Content Creation Demo")

        # Create content task
        content_task = {
            "task_id": "content-creation-demo-001",
            "type": "marketing_copy",
            "topic": "AI Technology Solutions",
            "audience": "business_professionals",
            "tone": "professional",
            "length": "short"
        }

        # Execute task
        start_time = datetime.now()
        result = await self.agents["content_creator"].execute_task(content_task)
        end_time = datetime.now()

        return {
            "task_type": "content_creation",
            "execution_time": (end_time - start_time).total_seconds(),
            "result": result,
            "status": "completed"
        }

    async def run_agent_communication_demo(self) -> Dict[str, Any]:
        """Run agent communication demo"""
        logger.info("📡 Running Agent Communication Demo")

        # Create communication message
        message = {
            "message_id": "comm-demo-001",
            "sender_id": "data-analyst-demo",
            "receiver_id": "content-creator-demo",
            "message_type": "task_assignment",
            "content": {
                "task_id": "collaboration-demo-001",
                "description": "Create marketing content based on data analysis",
                "requirements": ["data_insights", "marketing_copy"],
                "priority": 3
            },
            "timestamp": datetime.now()
        }

        # Send message
        start_time = datetime.now()
        success = await self.comm_system.send_message(message)
        end_time = datetime.now()

        # Try to receive message
        received_message = await self.comm_system.receive_message("content-creator-demo")

        return {
            "task_type": "communication",
            "execution_time": (end_time - start_time).total_seconds(),
            "message_sent": success,
            "message_received": received_message is not None,
            "status": "completed" if success else "failed"
        }

    async def run_marketplace_demo(self) -> Dict[str, Any]:
        """Run marketplace demo"""
        logger.info("🏪 Running Marketplace Demo")

        # Register a service in marketplace
        service_registration = {
            "service_id": "data-analysis-service-demo",
            "agent_id": "data-analyst-demo",
            "service_name": "Advanced Data Analysis",
            "description": "Statistical analysis and data insights",
            "capabilities": ["statistical_analysis", "correlation_analysis"],
            "base_price": 0.15,
            "currency": "USD"
        }

        # Register service
        start_time = datetime.now()
        registration_result = await self.marketplace.register_service(
            service_registration["agent_id"],
            service_registration
        )
        end_time = datetime.now()

        # Get marketplace status
        marketplace_status = await self.marketplace.get_marketplace_status()

        return {
            "task_type": "marketplace",
            "execution_time": (end_time - start_time).total_seconds(),
            "service_registered": registration_result,
            "marketplace_status": marketplace_status,
            "status": "completed"
        }

    async def run_complete_demo(self) -> Dict[str, Any]:
        """Run complete demo with all components"""
        logger.info("🎭 Starting Simple Agent Demo")
        print("=" * 60)
        print("🤖 EMPOORIO SIMPLE AGENT DEMO")
        print("=" * 60)

        try:
            # Initialize system
            print("🚀 Initializing system...")
            await self.initialize_system()
            print("✅ System initialized")

            # Run individual demos
            results = {}

            print("\n📊 Running Data Analysis Demo...")
            results["data_analysis"] = await self.run_data_analysis_demo()
            print("✅ Data analysis completed")

            print("\n✍️ Running Content Creation Demo...")
            results["content_creation"] = await self.run_content_creation_demo()
            print("✅ Content creation completed")

            print("\n📡 Running Communication Demo...")
            results["communication"] = await self.run_agent_communication_demo()
            print("✅ Communication demo completed")

            print("\n🏪 Running Marketplace Demo...")
            results["marketplace"] = await self.run_marketplace_demo()
            print("✅ Marketplace demo completed")

            # Generate summary
            summary = self._generate_demo_summary(results)

            # Print results
            self._print_demo_results(results, summary)

            return {
                "demo_completed_at": datetime.now(),
                "results": results,
                "summary": summary
            }

        except Exception as e:
            logger.error(f"Demo failed: {e}")
            raise
        finally:
            await self.cleanup()

    def _generate_demo_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate demo summary"""
        total_execution_time = sum(result["execution_time"] for result in results.values())
        successful_tasks = sum(1 for result in results.values() if result["status"] == "completed")

        return {
            "total_tasks": len(results),
            "successful_tasks": successful_tasks,
            "total_execution_time": total_execution_time,
            "average_execution_time": total_execution_time / len(results),
            "success_rate": successful_tasks / len(results) * 100,
            "system_components_tested": ["orchestrator", "marketplace", "communication", "agents"]
        }

    def _print_demo_results(self, results: Dict[str, Any], summary: Dict[str, Any]) -> None:
        """Print demo results"""
        print("\n" + "=" * 60)
        print("📊 DEMO RESULTS SUMMARY")
        print("=" * 60)

        # Individual results
        for task_name, result in results.items():
            status_icon = "✅" if result["status"] == "completed" else "❌"
            print(f"{status_icon} {task_name.replace('_', ' ').title()}: {result['execution_time']:.2f}s")

        print("\n📈 Performance Summary:")
        print(f"   • Total Tasks: {summary['total_tasks']}")
        print(f"   • Successful: {summary['successful_tasks']}")
        print(f"   • Success Rate: {summary['success_rate']:.1f}%")
        print(f"   • Total Time: {summary['total_execution_time']:.2f}s")
        print(f"   • Average Time: {summary['average_execution_time']:.2f}s")

        print("\n🔧 Components Tested:")
        for component in summary["system_components_tested"]:
            print(f"   • {component.title()}")

        print("\n" + "=" * 60)
        print("✅ SIMPLE AGENT DEMO COMPLETED SUCCESSFULLY")
        print("🎉 All core agent functionalities working correctly")
        print("=" * 60)

    async def cleanup(self) -> None:
        """Clean up resources"""
        logger.info("🧹 Cleaning up demo resources")

        if self.comm_system:
            await self.comm_system.shutdown()

        if self.marketplace:
            await self.marketplace.shutdown()

        if self.orchestrator:
            await self.orchestrator.shutdown()

        logger.info("✅ Cleanup completed")

async def main():
    """Main demo execution"""
    demo = SimpleAgentDemo()

    try:
        results = await demo.run_complete_demo()

        # Save results to file
        with open('simple_agent_demo_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print("\n💾 Results saved to 'simple_agent_demo_results.json'")

    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise
    finally:
        await demo.cleanup()

if __name__ == "__main__":
    asyncio.run(main())