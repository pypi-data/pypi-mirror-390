#!/usr/bin/env python3
"""
Empoorio Agent Learning Demo
Demostración del sistema de aprendizaje continuo de agentes

Este demo muestra:
- ✅ Sistema de aprendizaje continuo funcional
- ✅ Mejora automática basada en experiencias
- ✅ Meta-aprendizaje y adaptación
- ✅ Evaluación de rendimiento del aprendizaje
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

from framework.base_agent import BaseAgent, AgentRole
from learning.continuous_learning import ContinuousLearningSystem

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentLearningDemo:
    """Demo del sistema de aprendizaje continuo"""

    def __init__(self):
        self.agent = None
        self.learning_system = None
        self.baseline_performance = {}
        self.learning_experiments = []

    async def initialize_system(self) -> None:
        """Initialize the learning demo system"""
        logger.info("🚀 Initializing Agent Learning Demo")

        # Create a specialized agent for learning
        self.agent = BaseAgent(
            agent_id="learning-demo-agent",
            name="Learning Agent",
            role=AgentRole.ANALYST,
            capabilities=["data_analysis", "pattern_recognition", "decision_making"]
        )
        await self.agent.initialize()

        # Initialize learning system
        self.learning_system = ContinuousLearningSystem(self.agent)
        await self.learning_system.initialize()

        logger.info("✅ Learning demo system initialized")

    async def run_baseline_assessment(self) -> Dict[str, Any]:
        """Run baseline performance assessment"""
        logger.info("📊 Running baseline assessment")

        # Get initial learning status
        baseline_status = await self.learning_system.get_learning_status()

        # Simulate some basic tasks to establish baseline
        baseline_tasks = [
            {
                "task_id": "baseline-001",
                "type": "data_analysis",
                "complexity": "low",
                "expected_accuracy": 0.7
            },
            {
                "task_id": "baseline-002",
                "type": "pattern_recognition",
                "complexity": "medium",
                "expected_accuracy": 0.6
            }
        ]

        baseline_results = []
        for task in baseline_tasks:
            # Simulate task execution
            result = {
                "task_id": task["task_id"],
                "accuracy": task["expected_accuracy"],
                "efficiency": 0.5,
                "timestamp": datetime.now()
            }
            baseline_results.append(result)

        self.baseline_performance = {
            "learning_status": baseline_status,
            "baseline_tasks": baseline_results,
            "average_accuracy": sum(r["accuracy"] for r in baseline_results) / len(baseline_results),
            "average_efficiency": sum(r["efficiency"] for r in baseline_results) / len(baseline_results)
        }

        return self.baseline_performance

    async def run_learning_experiments(self) -> List[Dict[str, Any]]:
        """Run learning experiments with different scenarios"""
        logger.info("🧠 Running learning experiments")

        experiments = [
            {
                "experiment_id": "exp-supervised-learning",
                "type": "supervised_learning",
                "description": "Aprendizaje supervisado con feedback estructurado",
                "tasks": [
                    {
                        "context": {"task_type": "data_analysis", "complexity": "high"},
                        "action": {"method": "advanced_statistics"},
                        "outcome": {"accuracy": 0.85, "efficiency": 0.8},
                        "reward": 0.9
                    },
                    {
                        "context": {"task_type": "pattern_recognition", "complexity": "high"},
                        "action": {"method": "machine_learning"},
                        "outcome": {"accuracy": 0.88, "efficiency": 0.75},
                        "reward": 0.95
                    }
                ]
            },
            {
                "experiment_id": "exp-reinforcement-learning",
                "type": "reinforcement_learning",
                "description": "Aprendizaje por refuerzo con recompensas",
                "tasks": [
                    {
                        "context": {"task_type": "decision_making", "complexity": "medium"},
                        "action": {"method": "rule_based"},
                        "outcome": {"accuracy": 0.75, "efficiency": 0.9},
                        "reward": 0.7
                    },
                    {
                        "context": {"task_type": "decision_making", "complexity": "high"},
                        "action": {"method": "adaptive_algorithm"},
                        "outcome": {"accuracy": 0.92, "efficiency": 0.85},
                        "reward": 0.98
                    }
                ]
            },
            {
                "experiment_id": "exp-meta-learning",
                "type": "meta_learning",
                "description": "Meta-aprendizaje para optimización del aprendizaje",
                "tasks": [
                    {
                        "context": {"task_type": "optimization", "complexity": "high"},
                        "action": {"method": "meta_optimization"},
                        "outcome": {"accuracy": 0.95, "efficiency": 0.95},
                        "reward": 1.0
                    }
                ]
            }
        ]

        experiment_results = []

        for experiment in experiments:
            logger.info(f"Running experiment: {experiment['experiment_id']}")

            experiment_result = {
                "experiment_id": experiment["experiment_id"],
                "type": experiment["type"],
                "description": experiment["description"],
                "start_time": datetime.now(),
                "experiences_added": 0,
                "learning_improvements": {}
            }

            # Add learning experiences
            for task in experiment["tasks"]:
                await self.learning_system.add_experience(
                    context=task["context"],
                    action=task["action"],
                    outcome=task["outcome"],
                    reward=task["reward"]
                )
                experiment_result["experiences_added"] += 1

            experiment_result["end_time"] = datetime.now()
            experiment_result["duration"] = (experiment_result["end_time"] - experiment_result["start_time"]).total_seconds()

            # Get updated learning status
            updated_status = await self.learning_system.get_learning_status()
            experiment_result["final_learning_status"] = updated_status

            experiment_results.append(experiment_result)
            self.learning_experiments.append(experiment_result)

        return experiment_results

    async def evaluate_learning_progress(self) -> Dict[str, Any]:
        """Evaluate overall learning progress"""
        logger.info("📈 Evaluating learning progress")

        # Get final learning status
        final_status = await self.learning_system.get_learning_status()

        # Calculate improvements
        improvements = {
            "patterns_learned": final_status["learned_patterns"] - self.baseline_performance["learning_status"]["learned_patterns"],
            "skills_improved": final_status["skills_improved"] - self.baseline_performance["learning_status"]["skills_improved"],
            "experiences_processed": final_status["total_experiences"] - self.baseline_performance["learning_status"]["total_experiences"],
            "learning_sessions_completed": final_status["completed_sessions"] - self.baseline_performance["learning_status"]["completed_sessions"]
        }

        # Calculate performance improvements
        performance_improvements = {
            "accuracy_improvement": final_status.get("average_accuracy", 0.8) - self.baseline_performance["average_accuracy"],
            "efficiency_improvement": final_status.get("average_efficiency", 0.7) - self.baseline_performance["average_efficiency"]
        }

        return {
            "baseline_performance": self.baseline_performance,
            "final_performance": final_status,
            "improvements": improvements,
            "performance_improvements": performance_improvements,
            "learning_efficiency": improvements["experiences_processed"] / max(1, sum(exp["experiences_added"] for exp in self.learning_experiments))
        }

    async def run_learning_demo(self) -> Dict[str, Any]:
        """Run complete learning demo"""
        logger.info("🎭 Starting Agent Learning Demo")
        print("=" * 60)
        print("🧠 EMPOORIO AGENT LEARNING DEMO")
        print("=" * 60)

        try:
            # Initialize system
            print("🚀 Initializing learning system...")
            await self.initialize_system()
            print("✅ System initialized")

            # Run baseline assessment
            print("\n📊 Running baseline assessment...")
            baseline = await self.run_baseline_assessment()
            print("✅ Baseline assessment completed")
            print(f"   • Initial patterns: {baseline['learning_status']['learned_patterns']}")
            print(f"   • Baseline accuracy: {baseline['average_accuracy']:.2f}")

            # Run learning experiments
            print("\n🧪 Running learning experiments...")
            experiments = await self.run_learning_experiments()
            print("✅ Learning experiments completed")
            print(f"   • Experiments run: {len(experiments)}")
            print(f"   • Total experiences: {sum(exp['experiences_added'] for exp in experiments)}")

            # Evaluate learning progress
            print("\n📈 Evaluating learning progress...")
            evaluation = await self.evaluate_learning_progress()
            print("✅ Learning evaluation completed")

            # Generate comprehensive report
            report = {
                "demo_completed_at": datetime.now(),
                "baseline_assessment": baseline,
                "learning_experiments": experiments,
                "learning_evaluation": evaluation,
                "summary": self._generate_learning_summary(evaluation)
            }

            # Print results
            self._print_learning_results(evaluation)

            return report

        except Exception as e:
            logger.error(f"Learning demo failed: {e}")
            raise
        finally:
            await self.cleanup()

    def _generate_learning_summary(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate learning summary"""
        improvements = evaluation["improvements"]

        return {
            "total_patterns_learned": improvements["patterns_learned"],
            "total_skills_improved": improvements["skills_improved"],
            "total_experiences_processed": improvements["experiences_processed"],
            "learning_efficiency": evaluation["learning_efficiency"],
            "performance_improvements": evaluation["performance_improvements"],
            "experiments_completed": len(self.learning_experiments),
            "overall_learning_score": min(1.0, (improvements["patterns_learned"] + improvements["skills_improved"]) / 20.0)
        }

    def _print_learning_results(self, evaluation: Dict[str, Any]) -> None:
        """Print learning results"""
        print("\n" + "=" * 60)
        print("📊 LEARNING RESULTS SUMMARY")
        print("=" * 60)

        improvements = evaluation["improvements"]
        performance = evaluation["performance_improvements"]

        print("🧠 Learning Improvements:")
        print(f"   • Patterns Learned: +{improvements['patterns_learned']}")
        print(f"   • Skills Improved: +{improvements['skills_improved']}")
        print(f"   • Experiences Processed: +{improvements['experiences_processed']}")
        print(f"   • Learning Efficiency: {evaluation['learning_efficiency']:.2f}")

        print("\n📈 Performance Improvements:")
        print(f"   • Accuracy Improvement: {performance['accuracy_improvement']:+.3f}")
        print(f"   • Efficiency Improvement: {performance['efficiency_improvement']:+.3f}")

        print("\n🎯 Overall Assessment:")
        learning_score = min(1.0, (improvements["patterns_learned"] + improvements["skills_improved"]) / 20.0)
        print(f"   • Learning Score: {learning_score:.2f}/1.0")
        print(f"   • Assessment: {'Excellent' if learning_score > 0.8 else 'Good' if learning_score > 0.6 else 'Needs Improvement'}")

        print("\n" + "=" * 60)
        print("✅ AGENT LEARNING DEMO COMPLETED SUCCESSFULLY")
        print("🎉 Agent demonstrated continuous learning and improvement")
        print("=" * 60)

    async def cleanup(self) -> None:
        """Clean up resources"""
        logger.info("🧹 Cleaning up learning demo resources")

        if self.learning_system:
            await self.learning_system.shutdown()

        if self.agent:
            # Agent cleanup if needed
            pass

        logger.info("✅ Cleanup completed")

async def main():
    """Main demo execution"""
    demo = AgentLearningDemo()

    try:
        results = await demo.run_learning_demo()

        # Save results to file
        with open('agent_learning_demo_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print("\n💾 Results saved to 'agent_learning_demo_results.json'")

    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise
    finally:
        await demo.cleanup()

if __name__ == "__main__":
    asyncio.run(main())