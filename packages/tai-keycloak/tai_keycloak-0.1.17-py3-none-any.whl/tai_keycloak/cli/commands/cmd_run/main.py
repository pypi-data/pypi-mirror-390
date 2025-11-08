import click
import signal
import sys
from .checks import check_docker_engine, check_database_connection, wait_for_keycloak_ready, monitor_containers
from .docker_compose import get_docker_compose_path, run_docker_compose_detached, cleanup_containers
from .display import show_service_info


@click.command()
@click.option('--build', is_flag=True, help='Forzar rebuild de la imagen')
@click.option('--skip-db-check', is_flag=True, help='Omitir verificación de base de datos')
def run(build: bool, skip_db_check: bool):
    """Comando para iniciar el servidor Keycloak con configuración automática."""
    
    click.echo("🚀 " + click.style("Iniciando keycloak...", fg='cyan', bold=True))
    click.echo()
    
    # Variable global para el path del docker-compose (para cleanup)
    compose_dir = None
    
    def signal_handler(signum, frame):
        """Manejar Ctrl+C para limpiar contenedores."""
        cleanup_containers(compose_dir)
        sys.exit(0)
    
    # Configurar manejo de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Paso 1: Verificar Docker Engine
        if not check_docker_engine():
            return
        
        # Paso 3: Verificar base de datos (opcional)
        if not skip_db_check:
            check_database_connection()
        
        # Paso 4: Ejecutar Docker Compose en modo detach
        compose_dir = get_docker_compose_path()
        if not compose_dir:
            return
        
        # Ejecutar docker-compose siempre en modo detach
        run_docker_compose_detached(compose_dir, build)
        
        # Paso 5: Esperar a que Keycloak esté completamente listo
        if wait_for_keycloak_ready():
            # Paso 6: Mostrar información del servicio
            show_service_info()
            
            # Paso 7: Mantener el proceso activo y monitorear contenedores
            click.echo("⏳ " + click.style("Servidor ejecutándose... Presiona Ctrl+C para detener", fg='cyan'))
            click.echo()
            
            monitor_containers(compose_dir)
        else:
            click.echo("❌ " + click.style("El servidor no se inició correctamente", fg='red'))
            cleanup_containers(compose_dir)
        
    except KeyboardInterrupt:
        cleanup_containers(compose_dir)
    except Exception as e:
        import logging
        logging.exception(e)
        click.echo(f"❌ Error inesperado: {e}")
        cleanup_containers(compose_dir)


