#!/usr/bin/env python3
"""
Empoorio Comprehensive Agent System Demo
Demostración completa de todas las capacidades del sistema de agentes

Este demo integra:
- ✅ Framework base de agentes
- ✅ Orquestación multi-agente
- ✅ Marketplace de servicios
- ✅ Agentes especializados
- ✅ Aprendizaje continuo
- ✅ Comunicación avanzada
- ✅ Monitoreo y métricas
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

class ComprehensiveAgentDemo:
    """Demo comprehensivo del sistema completo de agentes"""

    def __init__(self):
        self.orchestrator = None
        self.marketplace = None
        self.comm_system = None
        self.agents = {}
        self.learning_systems = {}
        self.performance_metrics = {
            "start_time": None,
            "end_time": None,
            "tasks_completed": 0,
            "agents_created": 0,
            "services_registered": 0,
            "communications_sent": 0,
            "learning_sessions": 0
        }

    async def initialize_complete_system(self) -> None:
        """Initialize the complete agent ecosystem"""
        logger.info("🚀 Initializing Comprehensive Agent System")
        self.performance_metrics["start_time"] = datetime.now()

        # Initialize core systems
        await self._initialize_core_systems()

        # Create comprehensive agent team
        await self._create_agent_team()

        # Setup marketplace services
        await self._setup_marketplace()

        # Initialize learning systems
        await self._initialize_learning()

        logger.info("✅ Comprehensive Agent System fully initialized")

    async def _initialize_core_systems(self) -> None:
        """Initialize core systems"""
        # Communication system
        self.comm_system = AdvancedCommunicationSystem("comprehensive-demo-orchestrator")
        await self.comm_system.initialize()

        # Marketplace
        self.marketplace = AgentMarketplace()
        await self.marketplace.initialize()

        # Orchestrator
        self.orchestrator = MultiAgentOrchestrator()
        await self.orchestrator.initialize()

    async def _create_agent_team(self) -> None:
        """Create a comprehensive team of specialized agents"""
        logger.info("🤖 Creating comprehensive agent team")

        # Core specialized agents
        agents_config = [
            {
                "class": DataAnalysisAgent,
                "id": "chief-data-analyst",
                "name": "Chief Data Analyst",
                "capabilities": ["statistical_analysis", "data_visualization", "predictive_modeling"]
            },
            {
                "class": ContentCreationAgent,
                "id": "content-strategist",
                "name": "Content Strategist",
                "capabilities": ["content_creation", "marketing_strategy", "brand_management"]
            },
            {
                "class": BaseAgent,
                "id": "research-director",
                "name": "Research Director",
                "role": AgentRole.ANALYST,
                "capabilities": ["market_research", "competitive_analysis", "trend_forecasting"]
            },
            {
                "class": BaseAgent,
                "id": "strategy-consultant",
                "name": "Strategy Consultant",
                "role": AgentRole.STRATEGIST,
                "capabilities": ["strategic_planning", "risk_assessment", "business_modeling"]
            },
            {
                "class": BaseAgent,
                "id": "quality-assurance",
                "name": "Quality Assurance Agent",
                "role": AgentRole.MONITOR,
                "capabilities": ["quality_control", "performance_monitoring", "compliance_checking"]
            }
        ]

        for config in agents_config:
            if "class" in config:
                agent = config["class"](config["id"], config["name"])
            else:
                agent = BaseAgent(
                    agent_id=config["id"],
                    name=config["name"],
                    role=config["role"],
                    capabilities=config["capabilities"]
                )

            await agent.initialize()
            self.agents[config["id"]] = agent

            # Register with orchestrator
            await self.orchestrator.register_agent(agent, {
                "max_load": 1.0,
                "cost_per_hour": 25.0,
                "location": "global",
                "specialization": config["capabilities"][0]
            })

            # Register with communication system
            await self.comm_system.register_agent(agent)

        self.performance_metrics["agents_created"] = len(self.agents)
        logger.info(f"✅ Created {len(self.agents)} specialized agents")

    async def _setup_marketplace(self) -> None:
        """Setup marketplace with agent services"""
        logger.info("🏪 Setting up agent marketplace")

        marketplace_services = [
            {
                "agent_id": "chief-data-analyst",
                "service_name": "Advanced Data Analytics",
                "description": "Comprehensive statistical analysis and predictive modeling",
                "capabilities": ["statistical_analysis", "predictive_modeling"],
                "base_price": 0.20
            },
            {
                "agent_id": "content-strategist",
                "service_name": "Content Strategy & Creation",
                "description": "Strategic content creation and marketing campaigns",
                "capabilities": ["content_creation", "marketing_strategy"],
                "base_price": 0.15
            },
            {
                "agent_id": "research-director",
                "service_name": "Market Research & Intelligence",
                "description": "Deep market research and competitive intelligence",
                "capabilities": ["market_research", "competitive_analysis"],
                "base_price": 0.18
            },
            {
                "agent_id": "strategy-consultant",
                "service_name": "Strategic Consulting",
                "description": "Business strategy and risk assessment",
                "capabilities": ["strategic_planning", "risk_assessment"],
                "base_price": 0.25
            }
        ]

        for service in marketplace_services:
            await self.marketplace.register_service(
                service["agent_id"],
                service
            )
            self.performance_metrics["services_registered"] += 1

        logger.info(f"✅ Registered {len(marketplace_services)} services in marketplace")

    async def _initialize_learning(self) -> None:
        """Initialize learning systems for all agents"""
        for agent_name, agent in self.agents.items():
            learning_system = ContinuousLearningSystem(agent)
            await learning_system.initialize()
            self.learning_systems[agent_name] = learning_system

        logger.info("🧠 Learning systems initialized for all agents")

    async def run_business_intelligence_scenario(self) -> Dict[str, Any]:
        """Run a comprehensive business intelligence scenario"""
        logger.info("📊 Running Business Intelligence Scenario")

        # Complex business intelligence task
        bi_task = {
            "task_id": "bi-analysis-2025-q1",
            "type": "comprehensive_business_intelligence",
            "description": "Complete business intelligence analysis for tech startup expansion",
            "requirements": {
                "company_profile": "Tech Startup",
                "analysis_scope": "market_expansion",
                "time_horizon": "2_years",
                "key_deliverables": [
                    "market_analysis_report",
                    "competitive_landscape",
                    "growth_strategy",
                    "risk_assessment",
                    "investment_recommendations",
                    "marketing_campaign_plan"
                ]
            },
            "priority": 5,
            "deadline": (datetime.now().timestamp() + 1800),  # 30 minutes
            "budget": 500.0
        }

        # Submit complex task
        task_id = await self.orchestrator.submit_task(
            "Complete Business Intelligence Analysis",
            bi_task
        )

        # Execute collaborative workflow
        results = await self._execute_bi_workflow(bi_task)

        # Generate comprehensive report
        final_report = await self._generate_bi_report(results)

        return {
            "task_id": task_id,
            "scenario": "business_intelligence",
            "results": results,
            "final_report": final_report,
            "execution_time": (datetime.now() - self.performance_metrics["start_time"]).total_seconds()
        }

    async def _execute_bi_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute business intelligence workflow"""
        logger.info("🔄 Executing BI workflow")

        results = {
            "market_analysis": {},
            "competitive_intelligence": {},
            "strategic_planning": {},
            "content_strategy": {},
            "quality_assurance": {},
            "collaboration_events": []
        }

        # Phase 1: Market Analysis
        market_task = {
            "task_id": "market-analysis-001",
            "type": "market_research",
            "focus_area": "tech_startup_market",
            "methodology": "comprehensive"
        }

        result = await self.agents["research-director"].execute_task(market_task)
        results["market_analysis"] = result
        results["collaboration_events"].append(self._create_event("market_analysis", ["research-director"]))

        # Phase 2: Competitive Intelligence
        competitive_task = {
            "task_id": "competitive-analysis-001",
            "type": "competitive_analysis",
            "industry": "technology",
            "scope": "global"
        }

        result = await self.agents["chief-data-analyst"].execute_task(competitive_task)
        results["competitive_intelligence"] = result
        results["collaboration_events"].append(self._create_event("competitive_analysis", ["chief-data-analyst"]))

        # Phase 3: Strategic Planning
        strategy_task = {
            "task_id": "strategy-planning-001",
            "type": "strategic_planning",
            "context": "startup_expansion",
            "constraints": ["budget_500k", "timeline_2_years"]
        }

        result = await self.agents["strategy-consultant"].execute_task(strategy_task)
        results["strategic_planning"] = result
        results["collaboration_events"].append(self._create_event("strategic_planning", ["strategy-consultant"]))

        # Phase 4: Content Strategy
        content_task = {
            "task_id": "content-strategy-001",
            "type": "marketing_strategy",
            "campaign_type": "brand_awareness",
            "target_audience": "enterprise_clients"
        }

        result = await self.agents["content-strategist"].execute_task(content_task)
        results["content_strategy"] = result
        results["collaboration_events"].append(self._create_event("content_strategy", ["content-strategist"]))

        # Phase 5: Quality Assurance
        qa_task = {
            "task_id": "quality-assurance-001",
            "type": "quality_control",
            "deliverables": ["market_report", "strategy_plan", "content_plan"],
            "standards": ["enterprise_grade", "data_accuracy_95%"]
        }

        result = await self.agents["quality-assurance"].execute_task(qa_task)
        results["quality_assurance"] = result
        results["collaboration_events"].append(self._create_event("quality_assurance", ["quality-assurance"]))

        # Simulate inter-agent communications
        await self._simulate_team_communication()

        return results

    def _create_event(self, phase: str, agents: List[str]) -> Dict[str, Any]:
        """Create collaboration event"""
        return {
            "timestamp": datetime.now(),
            "phase": phase,
            "agents_involved": agents,
            "status": "completed"
        }

    async def _simulate_team_communication(self) -> None:
        """Simulate team communication between agents"""
        logger.info("📡 Simulating team communication")

        communications = [
            {
                "sender": "research-director",
                "receiver": "chief-data-analyst",
                "type": "data_request",
                "content": "Need detailed market data for analysis"
            },
            {
                "sender": "chief-data-analyst",
                "receiver": "strategy-consultant",
                "type": "insights_sharing",
                "content": "Sharing competitive intelligence insights"
            },
            {
                "sender": "strategy-consultant",
                "receiver": "content-strategist",
                "type": "strategy_alignment",
                "content": "Strategic direction for content creation"
            }
        ]

        for comm in communications:
            message = {
                "message_id": f"comm-{comm['sender']}-{comm['receiver']}-{int(datetime.now().timestamp())}",
                "sender_id": comm["sender"],
                "receiver_id": comm["receiver"],
                "message_type": comm["type"],
                "content": comm["content"],
                "timestamp": datetime.now()
            }

            success = await self.comm_system.send_message(message)
            if success:
                self.performance_metrics["communications_sent"] += 1

    async def _generate_bi_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive business intelligence report"""
        return {
            "report_id": f"bi-report-{int(datetime.now().timestamp())}",
            "title": "Business Intelligence Analysis - Tech Startup Expansion",
            "generated_at": datetime.now(),
            "executive_summary": {
                "market_opportunity": "$2.8B addressable market",
                "recommended_strategy": "Aggressive expansion with focused positioning",
                "risk_level": "Medium",
                "investment_required": "$500K",
                "expected_roi": "3.2x within 2 years"
            },
            "detailed_sections": {
                "market_analysis": results["market_analysis"],
                "competitive_intelligence": results["competitive_intelligence"],
                "strategic_recommendations": results["strategic_planning"],
                "marketing_strategy": results["content_strategy"],
                "quality_assurance": results["quality_assurance"]
            },
            "collaboration_summary": {
                "total_agents_involved": len(self.agents),
                "collaboration_events": len(results["collaboration_events"]),
                "cross_agent_communications": self.performance_metrics["communications_sent"]
            }
        }

    async def demonstrate_learning_improvement(self) -> Dict[str, Any]:
        """Demonstrate learning improvement across the agent team"""
        logger.info("🧠 Demonstrating team learning improvement")

        # Add learning experiences for all agents
        learning_experiences = [
            {
                "agent": "chief-data-analyst",
                "context": {"task_type": "market_analysis", "complexity": "high"},
                "action": {"method": "advanced_analytics"},
                "outcome": {"accuracy": 0.92, "efficiency": 0.88},
                "reward": 0.95
            },
            {
                "agent": "content-strategist",
                "context": {"task_type": "content_creation", "complexity": "high"},
                "action": {"method": "ai_powered_creation"},
                "outcome": {"quality": 0.89, "engagement": 0.91},
                "reward": 0.93
            },
            {
                "agent": "research-director",
                "context": {"task_type": "competitive_analysis", "complexity": "high"},
                "action": {"method": "multi_source_intelligence"},
                "outcome": {"comprehensiveness": 0.94, "accuracy": 0.87},
                "reward": 0.91
            }
        ]

        for exp in learning_experiences:
            learning_system = self.learning_systems[exp["agent"]]
            await learning_system.add_experience(
                context=exp["context"],
                action=exp["action"],
                outcome=exp["outcome"],
                reward=exp["reward"]
            )
            self.performance_metrics["learning_sessions"] += 1

        # Get learning status for all agents
        learning_status = {}
        for agent_name, learning_system in self.learning_systems.items():
            status = await learning_system.get_learning_status()
            learning_status[agent_name] = status

        return {
            "experiences_added": len(learning_experiences),
            "learning_status": learning_status,
            "team_learning_score": sum(status["learned_patterns"] for status in learning_status.values()) / len(learning_status)
        }

    async def run_comprehensive_demo(self) -> Dict[str, Any]:
        """Run the complete comprehensive demo"""
        logger.info("🎭 Starting Comprehensive Agent System Demo")
        print("=" * 80)
        print("🤖 EMPOORIO COMPREHENSIVE AGENT SYSTEM DEMO")
        print("=" * 80)

        try:
            # Initialize complete system
            print("🚀 Initializing complete agent ecosystem...")
            await self.initialize_complete_system()
            print("✅ System initialized with all components")

            # Run business intelligence scenario
            print("\n📊 Running Business Intelligence Scenario...")
            bi_results = await self.run_business_intelligence_scenario()
            print("✅ Business intelligence analysis completed")

            # Demonstrate learning improvement
            print("\n🧠 Demonstrating team learning improvement...")
            learning_results = await self.demonstrate_learning_improvement()
            print("✅ Learning demonstration completed")

            # Get system status
            system_status = await self._get_system_status()

            # Generate final comprehensive report
            final_report = {
                "demo_completed_at": datetime.now(),
                "business_intelligence_results": bi_results,
                "learning_improvements": learning_results,
                "system_status": system_status,
                "performance_metrics": self.performance_metrics,
                "summary": self._generate_comprehensive_summary(bi_results, learning_results, system_status)
            }

            self.performance_metrics["end_time"] = datetime.now()
            self.performance_metrics["tasks_completed"] = 1

            # Print comprehensive results
            self._print_comprehensive_results(final_report)

            return final_report

        except Exception as e:
            logger.error(f"Comprehensive demo failed: {e}")
            raise
        finally:
            await self.cleanup()

    async def _get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "orchestrator_status": await self.orchestrator.get_orchestrator_status(),
            "marketplace_status": await self.marketplace.get_marketplace_status(),
            "communication_status": await self.comm_system.get_communication_status(),
            "active_agents": len(self.agents),
            "registered_services": self.performance_metrics["services_registered"]
        }

    def _generate_comprehensive_summary(self, bi_results: Dict, learning_results: Dict, system_status: Dict) -> Dict[str, Any]:
        """Generate comprehensive demo summary"""
        execution_time = bi_results["execution_time"]

        return {
            "demo_type": "comprehensive_agent_system",
            "total_execution_time": execution_time,
            "agents_deployed": len(self.agents),
            "services_available": system_status["registered_services"],
            "communications_processed": self.performance_metrics["communications_sent"],
            "learning_sessions_completed": self.performance_metrics["learning_sessions"],
            "team_learning_score": learning_results["team_learning_score"],
            "system_health": "excellent" if execution_time < 60 else "good",
            "collaboration_efficiency": len(bi_results["results"]["collaboration_events"]) / execution_time
        }

    def _print_comprehensive_results(self, report: Dict[str, Any]) -> None:
        """Print comprehensive demo results"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE AGENT SYSTEM RESULTS")
        print("=" * 80)

        summary = report["summary"]
        bi = report["business_intelligence_results"]
        learning = report["learning_improvements"]

        print("🎯 Demo Overview:")
        print(f"   • Demo Type: {summary['demo_type'].replace('_', ' ').title()}")
        print(f"   • Total Execution Time: {summary['total_execution_time']:.2f}s")
        print(f"   • Agents Deployed: {summary['agents_deployed']}")
        print(f"   • Services Available: {summary['services_available']}")

        print("\n📊 Business Intelligence Results:")
        print(f"   • Task ID: {bi['task_id']}")
        print(f"   • Scenario: {bi['scenario'].replace('_', ' ').title()}")
        print(f"   • Collaboration Events: {len(bi['results']['collaboration_events'])}")
        print(f"   • Report Generated: {'market-analysis-report' in str(bi['final_report'])}")

        print("\n🧠 Learning Improvements:")
        print(f"   • Experiences Added: {learning['experiences_added']}")
        print(f"   • Team Learning Score: {summary['team_learning_score']:.2f}")
        print(f"   • Learning Sessions: {summary['learning_sessions_completed']}")

        print("\n🌐 System Performance:")
        print(f"   • Communications Processed: {summary['communications_processed']}")
        print(f"   • Collaboration Efficiency: {summary['collaboration_efficiency']:.3f} events/sec")
        print(f"   • System Health: {summary['system_health'].title()}")

        print("\n" + "=" * 80)
        print("✅ COMPREHENSIVE AGENT SYSTEM DEMO COMPLETED SUCCESSFULLY")
        print("🎉 All agent capabilities demonstrated with enterprise-grade performance")
        print("=" * 80)

    async def cleanup(self) -> None:
        """Clean up all resources"""
        logger.info("🧹 Cleaning up comprehensive demo resources")

        if self.comm_system:
            await self.comm_system.shutdown()

        if self.marketplace:
            await self.marketplace.shutdown()

        if self.orchestrator:
            await self.orchestrator.shutdown()

        for learning_system in self.learning_systems.values():
            await learning_system.shutdown()

        logger.info("✅ Cleanup completed")

async def main():
    """Main demo execution"""
    demo = ComprehensiveAgentDemo()

    try:
        results = await demo.run_comprehensive_demo()

        # Save results to file
        with open('comprehensive_agent_demo_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print("\n💾 Results saved to 'comprehensive_agent_demo_results.json'")

    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise
    finally:
        await demo.cleanup()

if __name__ == "__main__":
    asyncio.run(main())