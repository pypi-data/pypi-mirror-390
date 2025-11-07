"""
Mostrar información del servicio iniciado
"""
import os
import re
from urllib.parse import unquote
import click

def parse_keycloak_url():
    """
    Parsea MAIN_KEYCLOAK_URL para extraer protocolo, credenciales, host y puerto.
    Formato esperado: [protocol://][username[:password]@]host[:port]
    
    Returns:
        tuple: (username, password, protocol, host, port) - por defecto ('admin', 'admin', 'http', 'localhost', '8090')
    """
    url = os.environ.get('MAIN_KEYCLOAK_URL', '').strip()
    
    # Si no hay URL, usar valores por defecto
    if not url:
        return 'admin', 'admin', 'http', 'localhost', '8090', False
    
    # Patrón regex para parsear la URL: [protocol://][user[:password]@]host[:port]
    pattern = r'^(([^:]+)://)?((([^:@]+)(:([^@]+))?@)?([^:/]+)(:([0-9]+))?)$'
    match = re.match(pattern, url)
    
    if not match:
        # Si no se puede parsear, usar valores por defecto
        return 'admin', 'admin', 'http', 'localhost', '8090', False
    
    protocol = match.group(2) or 'http'
    username = match.group(5) or ''
    password = match.group(7) or ''
    host = match.group(8) or 'localhost'
    port = match.group(10) or ''
    
    # URL decode de las credenciales
    if username:
        username = unquote(username)
    if password:
        password = unquote(password)
    
    # Si no hay credenciales en la URL, usar valores por defecto
    if not username:
        username = 'admin'
    if not password:
        password = 'admin'
    
    # Si no hay host, usar localhost
    if not host:
        host = 'localhost'
    
    # Si no hay puerto, devolver None para indicar que no debe mostrarse
    if not port:
        port = None
    
    return username, password, protocol, host, port, True

def show_service_info():
    """Mostrar información del servicio iniciado."""
    click.echo()
    click.echo("🎉 " + click.style("¡Keycloak iniciado exitosamente!", fg='green', bold=True))
    click.echo()
    
    # Parsear URL de Keycloak para obtener protocolo, host, puerto y credenciales
    admin_user, admin_password, protocol, host, port, from_env = parse_keycloak_url()
    
    # Construir base_url con el protocolo extraído
    if port is None:
        base_url = f"{protocol}://{host}"
    else:
        base_url = f"{protocol}://{host}:{port}"
    
    # URLs útiles
    admin_url = f"{base_url}/admin"
    realms_url = f"{base_url}/realms/master"
    
    # Mostrar origen de la configuración
    if from_env:
        config_source = click.style("MAIN_KEYCLOAK_URL", fg='yellow', bold=True)
        config_icon = "🔧"
    else:
        config_source = click.style("valores por defecto", fg='cyan')
        config_icon = "⚙️"
    
    click.echo(f"{config_icon} " + click.style("Configuración:", fg='cyan', bold=True) + f" {config_source}")
    click.echo()
    
    click.echo("🔗 " + click.style("URLs del servicio:", fg='cyan', bold=True))
    click.echo(f"   🏠 Página principal: {click.style(base_url, fg='blue', underline=True)}")
    click.echo(f"   👨‍💼 Consola de admin: {click.style(admin_url, fg='blue', underline=True)}")
    click.echo(f"   🔐 Realm master:     {click.style(realms_url, fg='blue', underline=True)}")
    click.echo()
    
    click.echo("🔑 " + click.style("Credenciales de administrador:", fg='cyan', bold=True))
    click.echo(f"   👤 Usuario: {click.style(admin_user, fg='green')}")
    
    # Mejorar el mensaje de la contraseña según el origen
    if from_env:
        if admin_password == 'admin':
            click.echo(f"   🔒 Password: {click.style(admin_password, fg='green')} (desde MAIN_KEYCLOAK_URL)")
        else:
            masked = '*' * len(admin_password)
            click.echo(f"   🔒 Password: {click.style(masked, fg='green')} (desde MAIN_KEYCLOAK_URL)")
    else:
        click.echo(f"   🔒 Password: {click.style(admin_password, fg='green')} (por defecto - desarrollo)")
    
    click.echo()
    
    # Comandos útiles
    click.echo("📋 " + click.style("Control del servidor:", fg='cyan', bold=True))
    click.echo("   ✋ Detener servidor: Presiona Ctrl+C (limpia automáticamente)")
    click.echo("   📝 Ver logs manualmente: docker-compose logs -f")
    click.echo()
    
    # Tips adicionales según el origen de la configuración
    click.echo("💡 " + click.style("Tips:", fg='magenta', bold=True))
    click.echo("   🌐 El servidor puede tardar unos segundos en estar completamente listo")
    click.echo("   📊 Los logs se capturan internamente pero no se muestran")
    click.echo("   🔧 Este proceso mantendrá el servidor activo hasta que lo detengas")
    
    if from_env:
        click.echo("   🔄 Configuración obtenida de MAIN_KEYCLOAK_URL")
        click.echo("   📝 Para cambiar la configuración, modifica la variable MAIN_KEYCLOAK_URL")
    else:
        click.echo("   🚀 Usando configuración por defecto (desarrollo)")
        click.echo("   📝 Para personalizar, establece MAIN_KEYCLOAK_URL en tu entorno")
        click.echo("   📋 Formato: [https://][usuario[:password]@]host[:puerto]")
    
    click.echo()