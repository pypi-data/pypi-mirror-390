"""
Model management commands for Ailoos CLI.
Handles model downloading, verification, listing, and management.
"""

import asyncio
import click
import json
import os
from pathlib import Path
from typing import Optional
from ...core.model_manager import ModelManager
from ...utils.logging import AiloosLogger


@click.group()
def model():
    """Model management commands."""
    pass


@model.command()
@click.option('--remote', is_flag=True, help='List remote models available')
@click.option('--local', is_flag=True, help='List locally downloaded models')
@click.option('--filter', help='Filter by name or type (e.g., "vision", "text")')
@click.option('--json', is_flag=True, help='Output in JSON format')
def list(remote, local, filter, json):
    """List available models."""
    if remote and local:
        click.echo("❌ Cannot use both --remote and --local")
        raise click.Abort()

    manager = ModelManager()

    if remote or (not remote and not local):
        # List remote models
        click.echo("🌐 Fetching available models from repository...")

        # Mock data - in real implementation this would call API
        models_data = [
            {
                "name": "empoorio-lm",
                "version": "v1.0.0",
                "status": "available",
                "size_gb": 1.2,
                "parameters": 1300000000,
                "description": "Modelo base soberano de lenguaje",
                "capabilities": ["text_generation", "classification"],
                "requirements": {
                    "min_memory_gb": 4,
                    "recommended_gpu": "RTX_3070"
                }
            },
            {
                "name": "tiny-mlp",
                "version": "v1.0.0",
                "status": "available",
                "size_gb": 0.045,
                "parameters": 50000,
                "description": "Modelo básico para pruebas",
                "capabilities": ["classification"],
                "requirements": {
                    "min_memory_gb": 0.5,
                    "recommended_gpu": None
                }
            },
            {
                "name": "vision-transformer",
                "version": "v2.1.0",
                "status": "available",
                "size_gb": 2.8,
                "parameters": 300000000,
                "description": "Modelo de visión computacional",
                "capabilities": ["image_classification", "object_detection"],
                "requirements": {
                    "min_memory_gb": 8,
                    "recommended_gpu": "RTX_3080"
                }
            }
        ]

        # Apply filter if specified
        if filter:
            models_data = [m for m in models_data
                          if filter.lower() in m['name'].lower()
                          or any(filter.lower() in cap.lower() for cap in m['capabilities'])]

    else:
        # List local models
        click.echo("💻 Scanning local models...")

        # Mock local models - in real implementation this would scan local directory
        models_data = [
            {
                "name": "tiny-mlp",
                "version": "v1.0.0",
                "status": "downloaded",
                "local_path": "./models/tiny-mlp-v1.0.0",
                "size_gb": 0.045,
                "last_used": "2024-01-01T10:30:00Z"
            }
        ]

    if json:
        click.echo(json.dumps({"models": models_data}, indent=2))
    else:
        if remote or (not remote and not local):
            click.echo("📦 Modelos Disponibles en Repositorio")
        else:
            click.echo("💾 Modelos Descargados Localmente")

        click.echo("=" * 80)
        click.echo("<15")
        click.echo("-" * 80)

        for model in models_data:
            if remote or (not remote and not local):
                status_emoji = "✅" if model['status'] == 'available' else "⏳"
                click.echo("<15")
            else:
                click.echo("<15")


@model.command()
@click.argument('model_name')
@click.option('--version', default='latest', help='Specific version to download')
@click.option('--force', is_flag=True, help='Force download even if exists')
@click.option('--verify', is_flag=True, help='Verify integrity after download')
@click.option('--output-dir', help='Custom output directory')
def download(model_name, version, force, verify, output_dir):
    """Download a model from the repository."""
    click.echo(f"📥 Downloading model: {model_name}")
    if version != 'latest':
        click.echo(f"📋 Version: {version}")
    if output_dir:
        click.echo(f"📁 Output directory: {output_dir}")

    manager = ModelManager()

    async def download_async():
        try:
            success = await manager.download_model(
                model_name=model_name,
                version=version,
                force=force,
                verify=verify,
                output_dir=output_dir
            )

            if success:
                click.echo("✅ Model downloaded successfully!")
                click.echo(f"📍 Location: {manager.get_model_path(model_name, version)}")
                if verify:
                    click.echo("🔐 Integrity verification: PASSED")
            else:
                click.echo("❌ Download failed")
                raise click.Abort()

        except Exception as e:
            click.echo(f"❌ Download error: {e}")
            raise click.ClickException(f"Model download failed: {e}")

    asyncio.run(download_async())


@model.command()
@click.argument('model_name')
@click.option('--version', default='latest', help='Model version')
@click.option('--json', is_flag=True, help='Output in JSON format')
def info(model_name, version, json):
    """Show detailed information about a model."""
    click.echo(f"ℹ️  Getting info for model: {model_name}")

    manager = ModelManager()

    # Mock model info - in real implementation this would fetch from API/local
    model_info = {
        "name": model_name,
        "version": version,
        "description": "Modelo de prueba básico para clasificación",
        "parameters": 50000,
        "size_gb": 0.045,
        "capabilities": ["classification"],
        "requirements": {
            "min_memory_gb": 0.5,
            "recommended_gpu": None,
            "python_version": ">=3.8"
        },
        "performance": {
            "accuracy": 0.89,
            "latency_ms": 15,
            "throughput_samples_per_sec": 1000
        },
        "training": {
            "dataset": "MNIST",
            "epochs": 10,
            "batch_size": 32,
            "optimizer": "Adam",
            "learning_rate": 0.001
        },
        "checksum": "sha256:abc123...",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

    if json:
        click.echo(json.dumps(model_info, indent=2))
    else:
        click.echo("📋 Model Information")
        click.echo("=" * 50)
        click.echo(f"🤖 Name: {model_info['name']}")
        click.echo(f"📋 Version: {model_info['version']}")
        click.echo(f"📝 Description: {model_info['description']}")
        click.echo(f"🧠 Parameters: {model_info['parameters']:,}")
        click.echo(f"💾 Size: {model_info['size_gb']} GB")

        click.echo(f"\n🎯 Capabilities:")
        for cap in model_info['capabilities']:
            click.echo(f"   • {cap}")

        click.echo(f"\n⚙️  Requirements:")
        req = model_info['requirements']
        click.echo(f"   RAM: {req['min_memory_gb']} GB minimum")
        if req['recommended_gpu']:
            click.echo(f"   GPU: {req['recommended_gpu']} recommended")
        click.echo(f"   Python: {req['python_version']}")

        click.echo(f"\n📊 Performance:")
        perf = model_info['performance']
        click.echo(f"   Accuracy: {perf['accuracy']:.2%}")
        click.echo(f"   Latency: {perf['latency_ms']}ms")
        click.echo(f"   Throughput: {perf['throughput_samples_per_sec']} samples/sec")


@model.command()
@click.argument('model_name')
@click.option('--version', default='latest', help='Model version')
@click.option('--force', is_flag=True, help='Skip confirmation')
def remove(model_name, version, force):
    """Remove a locally downloaded model."""
    if not force:
        if not click.confirm(f"Are you sure you want to remove model '{model_name}'?"):
            return

    click.echo(f"🗑️  Removing model: {model_name} v{version}")

    manager = ModelManager()

    try:
        success = manager.remove_model(model_name, version)
        if success:
            click.echo("✅ Model removed successfully")
        else:
            click.echo("❌ Model not found or removal failed")
            raise click.Abort()
    except Exception as e:
        click.echo(f"❌ Removal error: {e}")
        raise click.ClickException(f"Model removal failed: {e}")


@model.command()
@click.argument('model_name')
@click.option('--version', default='latest', help='Model version')
def verify(model_name, version):
    """Verify integrity of a downloaded model."""
    click.echo(f"🔐 Verifying model: {model_name} v{version}")

    manager = ModelManager()

    try:
        is_valid = manager.verify_model(model_name, version)
        if is_valid:
            click.echo("✅ Model integrity verified")
            click.echo("🔒 Checksum matches expected value")
        else:
            click.echo("❌ Model integrity check failed")
            click.echo("⚠️  Model may be corrupted - consider re-downloading")
            raise click.Abort()
    except Exception as e:
        click.echo(f"❌ Verification error: {e}")
        raise click.ClickException(f"Model verification failed: {e}")


@model.command()
@click.argument('model_name')
@click.option('--version', default='latest', help='Model version')
@click.option('--data-path', help='Path to test data')
@click.option('--batch-size', default=32, type=int, help='Batch size for testing')
def test(model_name, version, data_path, batch_size):
    """Test a downloaded model with sample data."""
    click.echo(f"🧪 Testing model: {model_name} v{version}")

    if not data_path:
        click.echo("❌ Data path is required for testing")
        raise click.Abort()

    manager = ModelManager()

    try:
        results = manager.test_model(
            model_name=model_name,
            version=version,
            data_path=data_path,
            batch_size=batch_size
        )

        click.echo("✅ Model testing completed")
        click.echo("📊 Results:")
        click.echo(f"   Accuracy: {results['accuracy']:.2%}")
        click.echo(f"   Loss: {results['loss']:.4f}")
        click.echo(f"   Samples tested: {results['samples_tested']}")
        click.echo(f"   Inference time: {results['avg_inference_time']:.2f}ms per sample")

    except Exception as e:
        click.echo(f"❌ Testing error: {e}")
        raise click.ClickException(f"Model testing failed: {e}")


@model.command()
@click.argument('source_model')
@click.argument('target_path')
@click.option('--format', type=click.Choice(['pytorch', 'onnx', 'tensorflow']),
              default='pytorch', help='Export format')
@click.option('--optimize', is_flag=True, help='Apply optimization for inference')
def export(source_model, target_path, format, optimize):
    """Export a model to different formats."""
    click.echo(f"📤 Exporting model: {source_model}")
    click.echo(f"🎯 Format: {format}")
    click.echo(f"📁 Target: {target_path}")

    manager = ModelManager()

    try:
        success = manager.export_model(
            model_name=source_model,
            target_path=target_path,
            format=format,
            optimize=optimize
        )

        if success:
            click.echo("✅ Model exported successfully")
            if optimize:
                click.echo("⚡ Optimizations applied for better inference performance")
        else:
            click.echo("❌ Export failed")
            raise click.Abort()

    except Exception as e:
        click.echo(f"❌ Export error: {e}")
        raise click.ClickException(f"Model export failed: {e}")


@model.command()
@click.option('--cache-dir', help='Cache directory to clean')
@click.option('--older-than', help='Remove models older than (e.g., "30d", "1w")')
@click.option('--dry-run', is_flag=True, help='Show what would be cleaned without doing it')
def clean(cache_dir, older_than, dry_run):
    """Clean up old or unused model files."""
    click.echo("🧹 Cleaning model cache...")

    if dry_run:
        click.echo("🔍 Dry run mode - no files will be deleted")

    manager = ModelManager()

    try:
        cleaned_info = manager.clean_cache(
            cache_dir=cache_dir,
            older_than=older_than,
            dry_run=dry_run
        )

        if dry_run:
            click.echo("📋 Would clean:")
        else:
            click.echo("✅ Cleaned:")

        click.echo(f"   Models: {cleaned_info['models_removed']}")
        click.echo(f"   Space freed: {cleaned_info['space_freed_gb']:.2f} GB")
        click.echo(f"   Errors: {cleaned_info['errors']}")

    except Exception as e:
        click.echo(f"❌ Clean error: {e}")
        raise click.ClickException(f"Cache cleaning failed: {e}")