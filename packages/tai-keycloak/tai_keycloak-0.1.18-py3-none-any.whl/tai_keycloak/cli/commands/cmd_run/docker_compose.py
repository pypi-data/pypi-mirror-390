"""
Gestión de Docker Compose para el comando run
"""
import os
import subprocess
from pathlib import Path
import click


def get_docker_compose_path() -> Path:
    """Encontrar el archivo docker-compose.yml."""
    # Buscar desde el directorio actual hacia arriba
    current_dir = Path.cwd()
    
    # Posibles ubicaciones del docker-compose
    possible_paths = [
        current_dir / "keycloak" / "docker" / "docker-compose.yml",
        current_dir / "keycloak" / "docker-compose.yml",
        current_dir / "docker" / "docker-compose.yml",
        Path(__file__).parent.parent.parent.parent / "docker" / "docker-compose.yml"
    ]
    
    for path in possible_paths:
        if path.exists():
            return path.parent  # Retornar el directorio que contiene docker-compose.yml
    
    click.echo("❌ " + click.style("No se encontró docker-compose.yml", fg='red'))
    click.echo("💡 Ejecuta este comando desde la raíz del proyecto tai-keycloak")
    return None


def run_docker_compose(compose_dir: Path, detach: bool, build: bool):
    """Ejecutar docker-compose."""
    click.echo("🐳 " + click.style("Iniciando contenedores...", fg='yellow'), nl=False)
    
    # Cambiar al directorio del docker-compose
    original_dir = os.getcwd()
    os.chdir(compose_dir)
    
    try:
        # Construir comando
        cmd = ['docker-compose', 'up']
        if detach:
            cmd.append('-d')
        if build:
            cmd.append('--build')
        
        # Ejecutar docker-compose
        if detach:
            # En modo detach, capturar salida
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                click.echo("\r   ✅ " + click.style("Contenedores iniciados en segundo plano", fg='green') + " " * 20)
                click.echo()
            else:
                click.echo("\r   ❌ " + click.style("Error iniciando contenedores:", fg='red') + " " * 20)
                click.echo(result.stderr)
                click.echo()
                return
        else:
            # En modo interactivo, mostrar salida en tiempo real
            click.echo("\r   📋 " + click.style("Logs del contenedor:", fg='cyan') + " " * 20)
            click.echo()
            subprocess.run(cmd)
    
    finally:
        # Volver al directorio original
        os.chdir(original_dir)


def run_docker_compose_detached(compose_dir: Path, build: bool):
    """Ejecutar docker-compose siempre en modo detach."""
    click.echo("🐳 " + click.style("Iniciando contenedores en segundo plano...", fg='yellow'), nl=False)
    
    # Cambiar al directorio del docker-compose
    original_dir = os.getcwd()
    os.chdir(compose_dir)
    
    try:
        # Construir comando - siempre detach
        cmd = ['docker-compose', 'up', '-d']
        if build:
            cmd.append('--build')
        
        # Ejecutar docker-compose
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            click.echo("\r   ✅ " + click.style("Contenedores iniciados exitosamente", fg='green') + " " * 20)
            click.echo()
        else:
            click.echo("\r   ❌ " + click.style("Error iniciando contenedores:", fg='red') + " " * 20)
            click.echo(result.stderr)
            click.echo()
            raise Exception("Error al iniciar contenedores")
    
    finally:
        # Volver al directorio original
        os.chdir(original_dir)


def cleanup_containers(compose_dir: Path):
    """Limpiar contenedores y volúmenes."""
    if compose_dir:
        click.echo("\n🧹 " + click.style("Limpiando contenedores y volúmenes...", fg='yellow'), nl=False)
        original_dir = os.getcwd()
        try:
            os.chdir(compose_dir)
            subprocess.run(['docker-compose', 'down', '-v'], 
                         capture_output=True, text=True)
            click.echo("\r   ✅ " + click.style("Limpieza completada", fg='green') + " " * 20)
            click.echo()
        except Exception as e:
            click.echo(f"\r   ❌ Error durante limpieza: {e}" + " " * 20)
            click.echo()
        finally:
            os.chdir(original_dir)