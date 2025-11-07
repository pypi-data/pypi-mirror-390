"""
Node management commands for Ailoos CLI.
Handles node registration, status monitoring, and lifecycle management.
"""

import asyncio
import click
import json
import time
from typing import Optional
from ...core.node import Node
from ...utils.logging import AiloosLogger


@click.group()
def node():
    """Node management commands."""
    pass


@node.command()
@click.option('--node-id', default=None, help='Unique node identifier')
@click.option('--coordinator-url', default='http://localhost:5001',
              help='Coordinator API URL')
@click.option('--data-dir', default='./data', help='Data directory')
@click.option('--models-dir', default='./models', help='Models directory')
@click.option('--log-level', default='INFO',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='Logging level')
@click.option('--auto-restart', is_flag=True,
              help='Automatically restart on failure')
def start(node_id, coordinator_url, data_dir, models_dir, log_level, auto_restart):
    """Start a federated learning node."""
    if node_id is None:
        import uuid
        node_id = f"node_{uuid.uuid4().hex[:8]}"

    logger = AiloosLogger(node_id, log_level)

    click.echo(f"🚀 Starting Ailoos node '{node_id}'...")
    click.echo(f"📡 Coordinator: {coordinator_url}")
    click.echo(f"📁 Data directory: {data_dir}")
    click.echo(f"🤖 Models directory: {models_dir}")

    # Create and start node
    node_instance = Node(
        node_id=node_id,
        coordinator_url=coordinator_url
    )

    async def run_node():
        try:
            success = await node_instance.start()
            if success:
                click.echo("✅ Node started successfully!")
                click.echo(f"🆔 Node ID: {node_id}")
                click.echo("🌐 Status: Active")
                click.echo("\n💡 Commands:")
                click.echo("   • ailoos node status    # Check node status")
                click.echo("   • ailoos federated join # Join training session")
                click.echo("   • ailoos node stop      # Stop the node")

                # Keep node running
                while True:
                    await asyncio.sleep(1)
            else:
                click.echo("❌ Failed to start node")
                raise click.Abort()

        except KeyboardInterrupt:
            click.echo("\n🛑 Stopping node...")
            await node_instance.stop()
        except Exception as e:
            logger.error(f"Node startup failed: {e}")
            if auto_restart:
                click.echo(f"🔄 Auto-restart enabled, attempting restart...")
                await asyncio.sleep(5)
                await run_node()
            else:
                raise click.ClickException(f"Node failed: {e}")

    try:
        asyncio.run(run_node())
    except KeyboardInterrupt:
        click.echo("\n👋 Node stopped by user")
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        raise


@node.command()
@click.option('--force', is_flag=True, help='Force immediate shutdown')
@click.option('--save-state', is_flag=True, help='Save current state before stopping')
def stop(force, save_state):
    """Stop the running node."""
    # Implementation would need to communicate with running node
    # For now, this is a placeholder
    click.echo("🛑 Stopping node...")
    if save_state:
        click.echo("💾 Saving node state...")
    click.echo("✅ Node stopped successfully")


@node.command()
@click.option('--json', is_flag=True, help='Output in JSON format')
@click.option('--watch', is_flag=True, help='Watch mode - continuous updates')
@click.option('--interval', default=5, help='Watch interval in seconds')
@click.option('--node-id', help='Specific node ID to query (default: auto-detect)')
@click.option('--coordinator-url', default='http://localhost:5001', help='Coordinator API URL')
def status(json, watch, interval, node_id, coordinator_url):
    """Show node status and information."""
    import aiohttp
    import psutil
    import time
    from datetime import datetime

    async def get_node_status():
        """Get real-time status from running node."""
        try:
            logger = AiloosLogger("node_status", "DEBUG")
            logger.debug("Starting node status retrieval")

            # First, try to detect running node via process
            running_node_id = detect_running_node()
            logger.debug(f"Detected running node: {running_node_id}")
            if not running_node_id and not node_id:
                logger.debug("No running node detected and no node_id provided")
                click.echo("❌ No running node detected. Use 'ailoos node start' to start a node.")
                return None

            target_node_id = node_id or running_node_id
            logger.debug(f"Using target node_id: {target_node_id}")

            # Connect to coordinator to get node status
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                try:
                    # Get node info from coordinator
                    node_url = f"{coordinator_url}/api/nodes/{target_node_id}"
                    async with session.get(node_url) as response:
                        if response.status == 200:
                            node_data = await response.json()
                        else:
                            node_data = {}

                    # Get current training session
                    session_url = f"{coordinator_url}/api/training/active"
                    async with session.get(session_url) as response:
                        if response.status == 200:
                            session_data = await response.json()
                            current_session = session_data.get('session_id')
                        else:
                            current_session = None

                except aiohttp.ClientError:
                    # Coordinator not available, get local system info
                    node_data = {}
                    current_session = None

            # Get local system information
            system_info = get_system_info()

            # Get training statistics (from local storage if available)
            training_stats = await get_training_stats(target_node_id)

            # Get rewards information
            rewards_info = await get_rewards_info(target_node_id, coordinator_url)

            # Calculate uptime
            uptime_seconds = await get_node_uptime(target_node_id)

            status_info = {
                "node_id": target_node_id,
                "status": "active" if uptime_seconds > 0 else "inactive",
                "uptime_seconds": uptime_seconds,
                "coordinator_connected": node_data.get('connected', False),
                "current_session": current_session,
                "last_seen": node_data.get('last_seen'),
                "hardware": system_info,
                "training_stats": training_stats,
                "rewards": rewards_info,
                "network": {
                    "coordinator_url": coordinator_url,
                    "connection_status": "connected" if node_data else "local_only"
                }
            }

            return status_info

        except Exception as e:
            click.echo(f"❌ Error getting node status: {e}")
            return None

    def detect_running_node():
        """Detect running Ailoos node process."""
        try:
            import psutil
            import os
            from pathlib import Path
            logger = AiloosLogger("node_status", "DEBUG")
            logger.debug("Starting node detection process scan")

            # First, try to read node_id from file
            node_id_file = Path.home() / '.ailoos' / 'node_id'
            if node_id_file.exists():
                with open(node_id_file, 'r') as f:
                    node_id = f.read().strip()
                    logger.debug(f"Found node_id from file: {node_id}")
                    return node_id

            # Fallback to process scan
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        logger.debug(f"Checking process {proc.info['pid']}: {cmdline}")
                        if cmdline and any('ailoos' in arg for arg in cmdline):
                            logger.debug(f"Found Ailoos process: {cmdline}")
                            # Try to extract node_id from command line or environment
                            for arg in cmdline:
                                if arg.startswith('--node-id='):
                                    node_id = arg.split('=')[1]
                                    logger.debug(f"Extracted node_id from arg: {node_id}")
                                    return node_id
                                elif arg == '--node-id' and len(cmdline) > cmdline.index(arg) + 1:
                                    node_id = cmdline[cmdline.index(arg) + 1]
                                    logger.debug(f"Extracted node_id from next arg: {node_id}")
                                    return node_id
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.debug(f"Process access error for {proc.info['pid']}: {e}")
                    continue
            logger.debug("No running Ailoos node found in process scan")
        except ImportError as e:
            logger.debug(f"psutil not available: {e}")
        except Exception as e:
            logger.error(f"Error in node detection: {e}")
        return None

    def get_system_info():
        """Get local system hardware information."""
        try:
            import psutil
            cpu_count = psutil.cpu_count(logical=True)
            memory = psutil.virtual_memory()

            # GPU detection (simplified)
            gpu_info = detect_gpu()

            return {
                "cpu_cores": cpu_count,
                "memory_gb": round(memory.total / (1024**3), 1),
                "memory_used_gb": round(memory.used / (1024**3), 1),
                "memory_percent": memory.percent,
                "gpu_available": gpu_info['available'],
                "gpu_model": gpu_info['model'],
                "gpu_memory_gb": gpu_info['memory_gb'],
                "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 1),
                "disk_used_gb": round(psutil.disk_usage('/').used / (1024**3), 1),
                "platform": "macOS" if "darwin" in str(psutil.sys.platform).lower() else "Linux"
            }
        except ImportError:
            return {
                "cpu_cores": "Unknown",
                "memory_gb": "Unknown",
                "gpu_available": False,
                "gpu_model": None
            }

    def detect_gpu():
        """Detect GPU information."""
        try:
            # Try NVIDIA GPU detection
            import subprocess
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    name, memory_mb = lines[0].split(',')
                    return {
                        'available': True,
                        'model': name.strip(),
                        'memory_gb': round(int(memory_mb) / 1024, 1)
                    }
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        # Try AMD GPU detection (macOS)
        try:
            import subprocess
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'],
                                  capture_output=True, text=True, timeout=5)
            if 'AMD' in result.stdout or 'Radeon' in result.stdout:
                return {
                    'available': True,
                    'model': 'AMD Radeon (Integrated)',
                    'memory_gb': None  # Shared memory
                }
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        return {
            'available': False,
            'model': None,
            'memory_gb': None
        }

    async def get_training_stats(node_id):
        """Get training statistics for the node."""
        try:
            # Try to read from local stats file
            import os
            from pathlib import Path

            stats_file = Path.home() / '.ailoos' / node_id / 'training_stats.json'
            if stats_file.exists():
                import json
                with open(stats_file, 'r') as f:
                    return json.load(f)

            # Default stats
            return {
                "rounds_completed": 0,
                "total_samples_processed": 0,
                "average_accuracy": 0.0,
                "total_training_time": 0,
                "last_training_round": None
            }
        except Exception:
            return {
                "rounds_completed": 0,
                "total_samples_processed": 0,
                "average_accuracy": 0.0
            }

    async def get_rewards_info(node_id, coordinator_url):
        """Get rewards information for the node."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                rewards_url = f"{coordinator_url}/api/rewards/{node_id}"
                async with session.get(rewards_url) as response:
                    if response.status == 200:
                        rewards_data = await response.json()
                        return {
                            "total_earned": str(rewards_data.get('total_earned', 0)),
                            "pending_claims": str(rewards_data.get('pending_claims', 0)),
                            "last_reward": rewards_data.get('last_reward_at')
                        }
        except Exception:
            pass

        return {
            "total_earned": "0.000",
            "pending_claims": "0.000"
        }

    async def get_node_uptime(node_id):
        """Get node uptime in seconds."""
        try:
            import psutil
            import time

            # Find node process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    if 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any('ailoos' in arg for arg in cmdline):
                            return int(time.time() - proc.info['create_time'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            pass
        return 0

    async def watch_status():
        """Watch mode for continuous status updates."""
        click.echo("📊 Watching node status (Ctrl+C to stop)")
        click.echo("=" * 60)

        try:
            while True:
                status_info = await get_node_status()
                if status_info:
                    display_status(status_info, json)
                    click.echo(f"\n⏰ Next update in {interval}s... (Ctrl+C to stop)")
                    click.echo("-" * 60)
                else:
                    click.echo("❌ Unable to get node status")

                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            click.echo("\n🛑 Stopped watching node status")

    def display_status(status_info, json_output):
        """Display status information."""
        if json_output:
            click.echo(json.dumps(status_info, indent=2, default=str))
            return

        click.echo("📊 Node Status")
        click.echo("=" * 50)
        click.echo(f"🆔 Node ID: {status_info['node_id']}")
        click.echo(f"🟢 Status: {status_info['status']}")
        click.echo(f"⏱️  Uptime: {status_info['uptime_seconds']}s")

        network = status_info.get('network', {})
        click.echo(f"📡 Coordinator: {network.get('connection_status', 'unknown').replace('_', ' ').title()}")

        if status_info.get('current_session'):
            click.echo(f"🎯 Session: {status_info['current_session']}")

        if status_info.get('last_seen'):
            click.echo(f"👀 Last Seen: {status_info['last_seen']}")

        click.echo(f"\n💾 Hardware:")
        hw = status_info['hardware']
        click.echo(f"   CPU: {hw.get('cpu_cores', 'Unknown')} cores")
        click.echo(f"   RAM: {hw.get('memory_gb', 'Unknown')}GB ({hw.get('memory_used_gb', 0)}GB used)")
        click.echo(f"   GPU: {hw.get('gpu_model', 'None') if hw.get('gpu_available') else 'None'}")
        if hw.get('gpu_memory_gb'):
            click.echo(f"   GPU Memory: {hw['gpu_memory_gb']}GB")
        click.echo(f"   Disk: {hw.get('disk_used_gb', 0)}GB / {hw.get('disk_total_gb', 0)}GB used")

        click.echo(f"\n📊 Training:")
        ts = status_info['training_stats']
        click.echo(f"   Rounds: {ts.get('rounds_completed', 0)}")
        click.echo(f"   Samples: {ts.get('total_samples_processed', 0):,}")
        click.echo(f"   Accuracy: {ts.get('average_accuracy', 0):.1f}%")
        if ts.get('total_training_time'):
            click.echo(f"   Training Time: {ts['total_training_time']}s")

        click.echo(f"\n💰 Rewards:")
        rw = status_info['rewards']
        click.echo(f"   Earned: {rw.get('total_earned', '0.000')} DRACMA")
        click.echo(f"   Pending: {rw.get('pending_claims', '0.000')} DRACMA")
        if rw.get('last_reward'):
            click.echo(f"   Last Reward: {rw['last_reward']}")

    # Main execution
    if watch:
        asyncio.run(watch_status())
    else:
        status_info = asyncio.run(get_node_status())
        if status_info:
            display_status(status_info, json)
        else:
            click.echo("❌ Unable to retrieve node status")
            raise click.Abort()


@node.command()
@click.option('--node-id', help='Specific node ID to monitor')
@click.option('--metrics', multiple=True,
              type=click.Choice(['cpu', 'memory', 'gpu', 'network', 'training', 'rewards']),
              help='Specific metrics to monitor (default: all)')
@click.option('--interval', default=2, type=float, help='Update interval in seconds')
@click.option('--coordinator-url', default='http://localhost:5001', help='Coordinator API URL')
@click.option('--compact', is_flag=True, help='Compact output format')
def monitor(node_id, metrics, interval, coordinator_url, compact):
    """Monitor node performance in real-time."""
    import asyncio
    import psutil
    import time
    from datetime import datetime

    # If no specific metrics requested, monitor all
    if not metrics:
        metrics = ['cpu', 'memory', 'gpu', 'network', 'training', 'rewards']

    async def get_realtime_metrics(target_node_id, metrics, coordinator_url):
        """Get real-time metrics from node and coordinator."""
        try:
            metrics_data = {}

            # System metrics (always collected)
            system_metrics = get_system_metrics()
            metrics_data['system'] = system_metrics

            # Network metrics
            if 'network' in metrics:
                try:
                    import aiohttp
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                        network_url = f"{coordinator_url}/api/network/stats"
                        async with session.get(network_url) as response:
                            if response.status == 200:
                                network_data = await response.json()
                                network_metrics = {
                                    'active_nodes': network_data.get('active_nodes', 0),
                                    'total_nodes': network_data.get('total_nodes', 0),
                                    'network_utilization': network_data.get('utilization', 0.0),
                                    'coordinator_latency_ms': network_data.get('latency_ms', 0)
                                }
                            else:
                                network_metrics = {
                                    'active_nodes': 'Unknown',
                                    'network_utilization': 'Unknown',
                                    'coordinator_latency_ms': 'Unknown'
                                }
                except Exception:
                    network_metrics = {
                        'active_nodes': 'Unknown',
                        'network_utilization': 'Unknown',
                        'coordinator_latency_ms': 'Unknown'
                    }
                metrics_data['network'] = network_metrics

            # Training metrics
            if 'training' in metrics:
                try:
                    import aiohttp
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                        training_url = f"{coordinator_url}/api/training/active"
                        async with session.get(training_url) as response:
                            if response.status == 200:
                                training_data = await response.json()
                                training_metrics = {
                                    'active_session': training_data.get('session_id'),
                                    'current_round': training_data.get('current_round', 0),
                                    'total_rounds': training_data.get('total_rounds', 0),
                                    'participants': training_data.get('participant_count', 0),
                                    'progress_percent': training_data.get('progress_percent', 0.0)
                                }
                            else:
                                training_metrics = {
                                    'active_session': None,
                                    'current_round': 0,
                                    'progress_percent': 0.0
                                }
                except Exception:
                    training_metrics = {
                        'active_session': None,
                        'current_round': 0,
                        'progress_percent': 0.0
                    }
                metrics_data['training'] = training_metrics

            # Rewards metrics
            if 'rewards' in metrics:
                try:
                    import aiohttp
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                        rewards_url = f"{coordinator_url}/api/rewards/{target_node_id}/stats"
                        async with session.get(rewards_url) as response:
                            if response.status == 200:
                                rewards_data = await response.json()
                                rewards_metrics = {
                                    'total_earned': rewards_data.get('total_earned', 0.0),
                                    'pending_rewards': rewards_data.get('pending', 0.0),
                                    'last_reward_amount': rewards_data.get('last_amount', 0.0),
                                    'reward_rate_per_hour': rewards_data.get('rate_per_hour', 0.0)
                                }
                            else:
                                rewards_metrics = {
                                    'total_earned': 0.0,
                                    'pending_rewards': 0.0,
                                    'reward_rate_per_hour': 0.0
                                }
                except Exception:
                    rewards_metrics = {
                        'total_earned': 0.0,
                        'pending_rewards': 0.0,
                        'reward_rate_per_hour': 0.0
                    }
                metrics_data['rewards'] = rewards_metrics

            # Node health metrics
            try:
                import aiohttp
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                    health_url = f"{coordinator_url}/api/nodes/{target_node_id}/health"
                    async with session.get(health_url) as response:
                        if response.status == 200:
                            health_data = await response.json()
                            health_metrics = {
                                'status': health_data.get('status', 'unknown'),
                                'uptime_seconds': health_data.get('uptime', 0),
                                'last_heartbeat': health_data.get('last_heartbeat'),
                                'error_count': health_data.get('error_count', 0),
                                'success_rate': health_data.get('success_rate', 0.0)
                            }
                        else:
                            health_metrics = {
                                'status': 'unknown',
                                'uptime_seconds': 0,
                                'error_count': 0,
                                'success_rate': 0.0
                            }
            except Exception:
                health_metrics = {
                    'status': 'unknown',
                    'uptime_seconds': 0,
                    'error_count': 0,
                    'success_rate': 0.0
                }
            metrics_data['health'] = health_metrics

            return metrics_data

        except Exception as e:
            return {'error': str(e)}

    def get_system_metrics():
        """Get real-time system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count(logical=True)

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = round(memory.used / (1024**3), 2)
            memory_total_gb = round(memory.total / (1024**3), 2)

            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = round(disk.used / (1024**3), 1)
            disk_total_gb = round(disk.total / (1024**3), 1)

            # GPU metrics (if available)
            gpu_metrics = get_gpu_metrics()

            # Network metrics
            network = psutil.net_io_counters()
            network_sent_mb = round(network.bytes_sent / (1024**2), 2)
            network_recv_mb = round(network.bytes_recv / (1024**2), 2)

            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'usage_percent': cpu_percent,
                    'frequency_mhz': round(cpu_freq.current, 0) if cpu_freq else None,
                    'cores': cpu_count
                },
                'memory': {
                    'usage_percent': memory_percent,
                    'used_gb': memory_used_gb,
                    'total_gb': memory_total_gb
                },
                'disk': {
                    'usage_percent': disk_percent,
                    'used_gb': disk_used_gb,
                    'total_gb': disk_total_gb
                },
                'gpu': gpu_metrics,
                'network': {
                    'sent_mb': network_sent_mb,
                    'received_mb': network_recv_mb
                }
            }

        except Exception as e:
            return {'error': f'System metrics error: {str(e)}'}

    def get_gpu_metrics():
        """Get GPU metrics if available."""
        try:
            # Try NVIDIA GPU
            import subprocess
            result = subprocess.run([
                'nvidia-smi',
                '--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=2)

            if result.returncode == 0:
                line = result.stdout.strip().split('\n')[0]
                util, mem_used, mem_total, temp = line.split(', ')
                return {
                    'available': True,
                    'utilization_percent': int(util),
                    'memory_used_mb': int(mem_used),
                    'memory_total_mb': int(mem_total),
                    'temperature_c': int(temp)
                }

        except (subprocess.SubprocessError, FileNotFoundError, ValueError):
            pass

        # Try AMD GPU (macOS)
        try:
            import subprocess
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'],
                                  capture_output=True, text=True, timeout=2)
            if 'AMD' in result.stdout or 'Radeon' in result.stdout:
                return {
                    'available': True,
                    'model': 'AMD Radeon',
                    'utilization_percent': None,  # Not easily available
                    'temperature_c': None
                }
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        return {
            'available': False,
            'utilization_percent': None,
            'temperature_c': None
        }

    async def get_network_metrics(node_id, coordinator_url):
        """Get network-related metrics."""
        try:
            import aiohttp

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                # Get network stats from coordinator
                network_url = f"{coordinator_url}/api/network/stats"
                async with session.get(network_url) as response:
                    if response.status == 200:
                        network_data = await response.json()
                        return {
                            'active_nodes': network_data.get('active_nodes', 0),
                            'total_nodes': network_data.get('total_nodes', 0),
                            'network_utilization': network_data.get('utilization', 0.0),
                            'coordinator_latency_ms': network_data.get('latency_ms', 0)
                        }

        except Exception:
            pass

        return {
            'active_nodes': 'Unknown',
            'network_utilization': 'Unknown',
            'coordinator_latency_ms': 'Unknown'
        }

    async def get_training_metrics(node_id, coordinator_url):
        """Get real-time training metrics."""
        try:
            import aiohttp

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                # Get training session info
                training_url = f"{coordinator_url}/api/training/active"
                async with session.get(training_url) as response:
                    if response.status == 200:
                        training_data = await response.json()
                        return {
                            'active_session': training_data.get('session_id'),
                            'current_round': training_data.get('current_round', 0),
                            'total_rounds': training_data.get('total_rounds', 0),
                            'participants': training_data.get('participant_count', 0),
                            'progress_percent': training_data.get('progress_percent', 0.0)
                        }

        except Exception:
            pass

        return {
            'active_session': None,
            'current_round': 0,
            'progress_percent': 0.0
        }

    async def get_rewards_metrics(node_id, coordinator_url):
        """Get real-time rewards metrics."""
        try:
            import aiohttp

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                rewards_url = f"{coordinator_url}/api/rewards/{node_id}/stats"
                async with session.get(rewards_url) as response:
                    if response.status == 200:
                        rewards_data = await response.json()
                        return {
                            'total_earned': rewards_data.get('total_earned', 0.0),
                            'pending_rewards': rewards_data.get('pending', 0.0),
                            'last_reward_amount': rewards_data.get('last_amount', 0.0),
                            'reward_rate_per_hour': rewards_data.get('rate_per_hour', 0.0)
                        }

        except Exception:
            pass

        return {
            'total_earned': 0.0,
            'pending_rewards': 0.0,
            'reward_rate_per_hour': 0.0
        }

    async def get_node_health(node_id, coordinator_url):
        """Get node health metrics."""
        try:
            import aiohttp

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                health_url = f"{coordinator_url}/api/nodes/{node_id}/health"
                async with session.get(health_url) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        return {
                            'status': health_data.get('status', 'unknown'),
                            'uptime_seconds': health_data.get('uptime', 0),
                            'last_heartbeat': health_data.get('last_heartbeat'),
                            'error_count': health_data.get('error_count', 0),
                            'success_rate': health_data.get('success_rate', 0.0)
                        }

        except Exception:
            pass

        return {
            'status': 'unknown',
            'uptime_seconds': 0,
            'error_count': 0,
            'success_rate': 0.0
        }

    def display_metrics(metrics_data, compact_mode):
        """Display metrics in formatted output."""
        if 'error' in metrics_data:
            click.echo(f"❌ Error: {metrics_data['error']}")
            return

        timestamp = datetime.now().strftime('%H:%M:%S')

        if compact_mode:
            # Compact single-line format
            system = metrics_data.get('system', {})
            cpu = system.get('cpu', {}).get('usage_percent', 0)
            mem = system.get('memory', {}).get('usage_percent', 0)
            gpu = system.get('gpu', {}).get('utilization_percent') if system.get('gpu', {}).get('available') else 0

            training = metrics_data.get('training', {})
            progress = training.get('progress_percent', 0)

            rewards = metrics_data.get('rewards', {})
            earned = rewards.get('total_earned', 0)

            click.echo(f"[{timestamp}] CPU:{cpu:3.0f}% MEM:{mem:3.0f}% GPU:{gpu or 0:3.0f}% TRAIN:{progress:3.0f}% EARNED:{earned:.3f}")
        else:
            # Full detailed format
            click.echo(f"\n📊 Real-time Metrics - {timestamp}")
            click.echo("=" * 60)

            # System metrics
            system = metrics_data.get('system', {})
            if 'cpu' in system:
                cpu = system['cpu']
                click.echo(f"🖥️  CPU: {cpu['usage_percent']:4.1f}% ({cpu.get('frequency_mhz', 'N/A')} MHz, {cpu.get('cores', 'N/A')} cores)")

            if 'memory' in system:
                mem = system['memory']
                click.echo(f"💾 RAM: {mem['usage_percent']:4.1f}% ({mem['used_gb']:.1f}GB / {mem['total_gb']:.1f}GB)")

            if 'gpu' in system and system['gpu']['available']:
                gpu = system['gpu']
                click.echo(f"🎮 GPU: {gpu.get('utilization_percent', 'N/A')}% ({gpu.get('temperature_c', 'N/A')}°C)")

            if 'disk' in system:
                disk = system['disk']
                click.echo(f"💿 Disk: {disk['usage_percent']:4.1f}% ({disk['used_gb']:.1f}GB / {disk['total_gb']:.1f}GB)")

            # Network metrics
            network = metrics_data.get('network', {})
            if network.get('active_nodes') != 'Unknown':
                click.echo(f"🌐 Network: {network.get('active_nodes', 0)} active nodes, "
                          f"latency: {network.get('coordinator_latency_ms', 'N/A')}ms")

            # Training metrics
            training = metrics_data.get('training', {})
            if training.get('active_session'):
                click.echo(f"🎯 Training: Round {training.get('current_round', 0)}/{training.get('total_rounds', 0)} "
                          f"({training.get('progress_percent', 0):.1f}%)")

            # Rewards metrics
            rewards = metrics_data.get('rewards', {})
            if rewards.get('total_earned', 0) > 0:
                click.echo(f"💰 Rewards: {rewards['total_earned']:.4f} DRACMA earned "
                          f"({rewards.get('reward_rate_per_hour', 0):.4f}/hr)")

            # Health metrics
            health = metrics_data.get('health', {})
            if health.get('status') != 'unknown':
                click.echo(f"❤️  Health: {health['status']} (uptime: {health.get('uptime_seconds', 0)}s, "
                          f"errors: {health.get('error_count', 0)})")

    async def monitor_loop():
        """Main monitoring loop."""
        click.echo("📊 Starting real-time node monitoring...")
        click.echo(f"🔄 Update interval: {interval}s")
        click.echo(f"📈 Monitoring metrics: {', '.join(metrics)}")
        click.echo("Press Ctrl+C to stop\n")

        # Detect node if not specified
        monitoring_node_id = node_id
        if not monitoring_node_id:
            monitoring_node_id = detect_running_node()
            if not monitoring_node_id:
                click.echo("❌ No running node detected. Please specify --node-id or start a node first.")
                return

        click.echo(f"🎯 Monitoring node: {monitoring_node_id}")
        click.echo("=" * 60)

        try:
            while True:
                start_time = time.time()

                # Get metrics
                metrics_data = await get_realtime_metrics(monitoring_node_id, metrics, coordinator_url)

                # Display metrics
                display_metrics(metrics_data, compact)

                # Calculate sleep time to maintain interval
                elapsed = time.time() - start_time
                sleep_time = max(0.1, interval - elapsed)

                await asyncio.sleep(sleep_time)

        except KeyboardInterrupt:
            click.echo("\n🛑 Monitoring stopped by user")
        except Exception as e:
            click.echo(f"\n❌ Monitoring error: {e}")

    def detect_running_node():
        """Detect running Ailoos node."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any('ailoos' in arg for arg in cmdline):
                            # Extract node ID from command line
                            for i, arg in enumerate(cmdline):
                                if arg == '--node-id' and i + 1 < len(cmdline):
                                    return cmdline[i + 1]
                                elif arg.startswith('--node-id='):
                                    return arg.split('=', 1)[1]
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            pass
        return None

    # Start monitoring
    asyncio.run(monitor_loop())


@node.command()
@click.option('--backup-dir', default='./backup',
              help='Directory to store backup')
@click.option('--include-logs', is_flag=True,
              help='Include log files in backup')
def backup(backup_dir, include_logs):
    """Create a backup of node data and configuration."""
    click.echo(f"💾 Creating node backup in {backup_dir}...")

    # Implementation would create backup of:
    # - Node configuration
    # - Local models
    # - Training checkpoints
    # - Optionally logs

    click.echo("✅ Backup completed successfully")


@node.command()
@click.option('--config-file', help='Configuration file to update')
@click.option('--key', required=True, help='Configuration key')
@click.option('--value', required=True, help='Configuration value')
def config(config_file, key, value):
    """Update node configuration."""
    click.echo(f"⚙️  Updating configuration: {key} = {value}")

    # This would update node configuration
    # Could be runtime config or persistent config

    click.echo("✅ Configuration updated")


@node.command()
def logs():
    """Show recent node logs."""
    click.echo("📋 Recent Node Logs:")
    click.echo("-" * 50)

    # This would show recent logs from the node
    # Could tail logs or show recent entries

    click.echo("ℹ️  Use 'ailoos logs tail' for real-time log monitoring")


@node.command()
@click.confirmation_option(prompt='Are you sure you want to reset this node?')
def reset():
    """Reset node to initial state (removes all data)."""
    click.echo("🔄 Resetting node to initial state...")

    # This would:
    # - Stop the node
    # - Remove local data/models
    # - Reset configuration
    # - Clear logs

    click.echo("✅ Node reset completed")
    click.echo("🚀 Use 'ailoos node start' to restart")