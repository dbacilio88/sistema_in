"""
CLI para gestión de configuración
=================================

Command Line Interface para administrar la configuración del sistema de 
detección de infracciones desde la línea de comandos.
"""

import click
import asyncio
import yaml
import json
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import logging

from config_manager import (
    ConfigManager,
    MLModelConfig,
    CameraConfig,
    DetectionConfig,
    SystemConfig,
    ConfigFormat
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear gestor de configuración global
config_manager = ConfigManager()

def async_command(f):
    """Decorador para comandos async de Click"""
    @click.command()
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        return asyncio.run(f(ctx, *args, **kwargs))
    return wrapper

@click.group()
@click.option('--config-dir', default='config', help='Directorio de configuración')
@click.option('--verbose', '-v', is_flag=True, help='Modo verbose')
@click.pass_context
def cli(ctx, config_dir, verbose):
    """Sistema de gestión de configuración para Traffic Detection System"""
    ctx.ensure_object(dict)
    ctx.obj['config_dir'] = config_dir
    ctx.obj['verbose'] = verbose
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Configurar directorio de configuración
    config_manager.config_dir = Path(config_dir)

# Comandos de inicialización

@cli.command()
@click.pass_context
def init(ctx):
    """Inicializar configuración por defecto"""
    async def _init():
        try:
            click.echo(f"Inicializando configuración en {config_manager.config_dir}")
            await config_manager.load_configurations()
            click.echo("✅ Configuración inicializada correctamente")
        except Exception as e:
            click.echo(f"❌ Error al inicializar: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_init())

@cli.command()
@click.pass_context
def validate(ctx):
    """Validar todas las configuraciones"""
    async def _validate():
        try:
            await config_manager.load_configurations()
            errors = await config_manager.validate_configurations()
            
            if not errors:
                click.echo("✅ Todas las configuraciones son válidas")
                return
            
            click.echo("❌ Se encontraron errores de configuración:")
            for category, error_list in errors.items():
                click.echo(f"\n{category.upper()}:")
                for error in error_list:
                    click.echo(f"  - {error}")
            
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Error durante validación: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_validate())

# Comandos de configuración del sistema

@cli.group()
def system():
    """Gestionar configuración del sistema"""
    pass

@system.command('show')
@click.option('--format', type=click.Choice(['yaml', 'json']), default='yaml')
@click.pass_context
def show_system_config(ctx, format):
    """Mostrar configuración del sistema"""
    async def _show():
        try:
            await config_manager.load_configurations()
            config = config_manager.system_config
            
            if format == 'yaml':
                from dataclasses import asdict
                click.echo(yaml.dump(asdict(config), default_flow_style=False))
            else:
                from dataclasses import asdict
                click.echo(json.dumps(asdict(config), indent=2))
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_show())

@system.command('set')
@click.argument('key')
@click.argument('value')
@click.pass_context
def set_system_config(ctx, key, value):
    """Establecer valor de configuración del sistema"""
    async def _set():
        try:
            await config_manager.load_configurations()
            
            if hasattr(config_manager.system_config, key):
                # Convertir valor al tipo correcto
                current_value = getattr(config_manager.system_config, key)
                if isinstance(current_value, bool):
                    value = value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(current_value, int):
                    value = int(value)
                elif isinstance(current_value, float):
                    value = float(value)
                
                setattr(config_manager.system_config, key, value)
                await config_manager.save_system_config()
                
                click.echo(f"✅ {key} = {value}")
            else:
                click.echo(f"❌ Configuración '{key}' no encontrada", err=True)
                sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_set())

# Comandos de cámaras

@cli.group()
def cameras():
    """Gestionar configuración de cámaras"""
    pass

@cameras.command('list')
@click.option('--active-only', is_flag=True, help='Mostrar solo cámaras activas')
@click.pass_context
def list_cameras(ctx, active_only):
    """Listar cámaras configuradas"""
    async def _list():
        try:
            await config_manager.load_configurations()
            
            if active_only:
                cameras = config_manager.get_active_cameras()
            else:
                cameras = config_manager.get_all_cameras()
            
            if not cameras:
                click.echo("No hay cámaras configuradas")
                return
            
            click.echo(f"{'ID':<10} {'Nombre':<30} {'Estado':<10} {'Ubicación'}")
            click.echo("-" * 70)
            
            for cam_id, config in cameras.items():
                status = "Activa" if config.active else "Inactiva"
                location = f"{config.location['lat']:.4f}, {config.location['lon']:.4f}"
                click.echo(f"{cam_id:<10} {config.name:<30} {status:<10} {location}")
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_list())

@cameras.command('show')
@click.argument('camera_id')
@click.option('--format', type=click.Choice(['yaml', 'json']), default='yaml')
@click.pass_context
def show_camera_config(ctx, camera_id, format):
    """Mostrar configuración de una cámara"""
    async def _show():
        try:
            await config_manager.load_configurations()
            config = config_manager.get_camera_config(camera_id)
            
            if not config:
                click.echo(f"❌ Cámara '{camera_id}' no encontrada", err=True)
                sys.exit(1)
            
            if format == 'yaml':
                from dataclasses import asdict
                click.echo(yaml.dump(asdict(config), default_flow_style=False))
            else:
                from dataclasses import asdict
                click.echo(json.dumps(asdict(config), indent=2))
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_show())

@cameras.command('enable')
@click.argument('camera_id')
@click.pass_context
def enable_camera(ctx, camera_id):
    """Activar una cámara"""
    async def _enable():
        try:
            await config_manager.load_configurations()
            
            if camera_id not in config_manager.camera_configs:
                click.echo(f"❌ Cámara '{camera_id}' no encontrada", err=True)
                sys.exit(1)
            
            await config_manager.update_camera_status(camera_id, True)
            click.echo(f"✅ Cámara '{camera_id}' activada")
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_enable())

@cameras.command('disable')
@click.argument('camera_id')
@click.pass_context
def disable_camera(ctx, camera_id):
    """Desactivar una cámara"""
    async def _disable():
        try:
            await config_manager.load_configurations()
            
            if camera_id not in config_manager.camera_configs:
                click.echo(f"❌ Cámara '{camera_id}' no encontrada", err=True)
                sys.exit(1)
            
            await config_manager.update_camera_status(camera_id, False)
            click.echo(f"✅ Cámara '{camera_id}' desactivada")
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_disable())

@cameras.command('add')
@click.argument('camera_id')
@click.option('--name', required=True, help='Nombre de la cámara')
@click.option('--rtsp-url', required=True, help='URL RTSP de la cámara')
@click.option('--lat', type=float, required=True, help='Latitud')
@click.option('--lon', type=float, required=True, help='Longitud')
@click.option('--speed-limit', type=int, default=60, help='Límite de velocidad')
@click.pass_context
def add_camera(ctx, camera_id, name, rtsp_url, lat, lon, speed_limit):
    """Agregar nueva cámara"""
    async def _add():
        try:
            await config_manager.load_configurations()
            
            if camera_id in config_manager.camera_configs:
                click.echo(f"❌ Cámara '{camera_id}' ya existe", err=True)
                sys.exit(1)
            
            config = CameraConfig(
                camera_id=camera_id,
                name=name,
                rtsp_url=rtsp_url,
                location={"lat": lat, "lon": lon},
                speed_limit=speed_limit
            )
            
            config_manager.camera_configs[camera_id] = config
            await config_manager.save_camera_config(camera_id, config)
            
            click.echo(f"✅ Cámara '{camera_id}' agregada correctamente")
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_add())

# Comandos de modelos ML

@cli.group()
def models():
    """Gestionar configuración de modelos ML"""
    pass

@models.command('list')
@click.pass_context
def list_models(ctx):
    """Listar modelos ML configurados"""
    async def _list():
        try:
            await config_manager.load_configurations()
            
            if not config_manager.ml_configs:
                click.echo("No hay modelos ML configurados")
                return
            
            click.echo(f"{'Nombre':<20} {'Versión':<10} {'Confianza':<10} {'Dispositivo'}")
            click.echo("-" * 60)
            
            for model_name, config in config_manager.ml_configs.items():
                click.echo(f"{model_name:<20} {config.model_version:<10} {config.confidence_threshold:<10} {config.device}")
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_list())

@models.command('show')
@click.argument('model_name')
@click.option('--format', type=click.Choice(['yaml', 'json']), default='yaml')
@click.pass_context
def show_model_config(ctx, model_name, format):
    """Mostrar configuración de un modelo ML"""
    async def _show():
        try:
            await config_manager.load_configurations()
            config = config_manager.get_ml_config(model_name)
            
            if not config:
                click.echo(f"❌ Modelo '{model_name}' no encontrado", err=True)
                sys.exit(1)
            
            if format == 'yaml':
                from dataclasses import asdict
                click.echo(yaml.dump(asdict(config), default_flow_style=False))
            else:
                from dataclasses import asdict
                click.echo(json.dumps(asdict(config), indent=2))
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_show())

# Comandos de detección

@cli.group()
def detection():
    """Gestionar configuración de detección"""
    pass

@detection.command('show')
@click.option('--format', type=click.Choice(['yaml', 'json']), default='yaml')
@click.pass_context
def show_detection_config(ctx, format):
    """Mostrar configuración de detección"""
    async def _show():
        try:
            await config_manager.load_configurations()
            config = config_manager.detection_config
            
            if format == 'yaml':
                from dataclasses import asdict
                click.echo(yaml.dump(asdict(config), default_flow_style=False))
            else:
                from dataclasses import asdict
                click.echo(json.dumps(asdict(config), indent=2))
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_show())

@detection.command('set-threshold')
@click.argument('threshold_type', type=click.Choice([
    'speed_threshold_warning',
    'speed_threshold_violation',
    'ocr_confidence_threshold'
]))
@click.argument('value', type=float)
@click.pass_context
def set_detection_threshold(ctx, threshold_type, value):
    """Establecer umbral de detección"""
    async def _set():
        try:
            await config_manager.load_configurations()
            await config_manager.update_detection_threshold(threshold_type, value)
            click.echo(f"✅ {threshold_type} = {value}")
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_set())

# Comandos de importación/exportación

@cli.group()
def config():
    """Importar/exportar configuración"""
    pass

@config.command('export')
@click.option('--format', type=click.Choice(['yaml', 'json']), default='yaml')
@click.option('--output', '-o', help='Archivo de salida')
@click.pass_context
def export_config(ctx, format, output):
    """Exportar configuración completa"""
    async def _export():
        try:
            await config_manager.load_configurations()
            
            config_format = ConfigFormat(format)
            content = config_manager.export_configuration(config_format)
            
            if output:
                with open(output, 'w') as f:
                    f.write(content)
                click.echo(f"✅ Configuración exportada a {output}")
            else:
                click.echo(content)
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_export())

@config.command('import')
@click.argument('file_path')
@click.option('--format', type=click.Choice(['yaml', 'json']), default='yaml')
@click.pass_context
def import_config(ctx, file_path, format):
    """Importar configuración desde archivo"""
    async def _import():
        try:
            if not Path(file_path).exists():
                click.echo(f"❌ Archivo no encontrado: {file_path}", err=True)
                sys.exit(1)
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            config_format = ConfigFormat(format)
            await config_manager.import_configuration(content, config_format)
            
            click.echo(f"✅ Configuración importada desde {file_path}")
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_import())

@config.command('backup')
@click.option('--output-dir', default='backups', help='Directorio de backups')
@click.pass_context
def backup_config(ctx, output_dir):
    """Crear backup de la configuración"""
    async def _backup():
        try:
            await config_manager.load_configurations()
            
            # Crear directorio de backup
            backup_dir = Path(output_dir)
            backup_dir.mkdir(exist_ok=True)
            
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"config_backup_{timestamp}.yaml"
            
            # Exportar configuración
            content = config_manager.export_configuration(ConfigFormat.YAML)
            
            with open(backup_file, 'w') as f:
                f.write(content)
            
            click.echo(f"✅ Backup creado: {backup_file}")
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_backup())

# Comandos de monitoreo

@cli.command()
@click.option('--watch', '-w', is_flag=True, help='Modo watch')
@click.pass_context
def status(ctx, watch):
    """Mostrar estado del sistema de configuración"""
    async def _status():
        try:
            await config_manager.load_configurations()
            
            # Mostrar estadísticas
            click.echo("📊 Estado del Sistema de Configuración")
            click.echo("=" * 40)
            
            # Sistema
            click.echo(f"Sistema: {config_manager.system_config.system_name}")
            click.echo(f"Versión: {config_manager.system_config.version}")
            click.echo(f"Entorno: {config_manager.system_config.environment}")
            click.echo()
            
            # Cámaras
            total_cameras = len(config_manager.camera_configs)
            active_cameras = len(config_manager.get_active_cameras())
            click.echo(f"Cámaras: {active_cameras}/{total_cameras} activas")
            
            # Modelos ML
            click.echo(f"Modelos ML: {len(config_manager.ml_configs)} configurados")
            
            # Validación
            errors = await config_manager.validate_configurations()
            if errors:
                error_count = sum(len(error_list) for error_list in errors.values())
                click.echo(f"❌ {error_count} errores de configuración")
            else:
                click.echo("✅ Configuración válida")
            
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    if watch:
        import time
        while True:
            try:
                click.clear()
                asyncio.run(_status())
                time.sleep(5)
            except KeyboardInterrupt:
                break
    else:
        asyncio.run(_status())

if __name__ == '__main__':
    cli()