#!/bin/bash

# Script para parsear MAIN_DATABASE_URL y MAIN_KEYCLOAK_URL y generar variables ENV para Keycloak
# Convierte URLs de base de datos y Keycloak en variables de entorno para usar en Dockerfile

# Usar set -e pero no -u (no pipefail) para ser más tolerante durante el build
set -e

# Función para mostrar ayuda
show_help() {
    cat << EOF
Uso: $0 [MAIN_DATABASE_URL] [MAIN_KEYCLOAK_URL] [output_mode]

Este script parsea las URLs de base de datos y Keycloak y genera variables ENV para Keycloak.

Argumentos:
    MAIN_DATABASE_URL     URL de base de datos (opcional, puede estar vacío)
    MAIN_KEYCLOAK_URL     URL con credenciales de Keycloak (opcional, puede estar vacío)
    output_mode           'env' para formato ENV de Dockerfile, 'file' para archivo .env (por defecto: env)

Opciones:
    -h, --help           Muestra esta ayuda

Variables generadas:
    KC_DB               - Tipo de base de datos (postgres, mysql, etc.)
    KC_DB_URL           - URL JDBC para Keycloak
    KC_DB_USERNAME      - Usuario de la base de datos
    KC_DB_PASSWORD      - Contraseña de la base de datos
    KC_DB_URL_DATABASE  - Nombre de la base de datos (siempre 'keycloak')
    KEYCLOAK_ADMIN      - Usuario administrador de Keycloak
    KEYCLOAK_ADMIN_PASSWORD - Contraseña del administrador

Formato esperado de MAIN_DATABASE_URL:
    driver://username:password@host:port/database

Formato esperado de MAIN_KEYCLOAK_URL:
    [protocol://][username[:password]@]host[:port]

Ejemplos:
    $0 "" ""                                                    # Solo valores por defecto
    $0 "postgresql://user:pass@localhost:5432/mydb" ""         # Solo BD, admin por defecto
    $0 "" "admin:secret@localhost:8080"                        # Solo admin, BD H2
    $0 "postgresql://user:pass@db:5432/app" "admin:pwd@host"   # Ambos configurados

Nota: El nombre de la base de datos siempre se fuerza a 'keycloak'
EOF
}

# Variables de entrada
MAIN_DATABASE_URL="${1:-}"
MAIN_KEYCLOAK_URL="${2:-}"
OUTPUT_MODE="${3:-env}"

# Procesar argumentos de línea de comandos
if [[ $# -gt 0 ]]; then
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
    esac
fi

# Función para logging
log_info() {
    echo "[INFO] $*" >&2
}

# Función para URL decode
url_decode() {
    local url_encoded="${1//+/ }"
    printf '%b' "${url_encoded//%/\\x}"
}

# Función para parsear MAIN_KEYCLOAK_URL y extraer credenciales de admin
parse_keycloak_url() {
    local url="$1"
    
    # Si la URL está vacía, usar valores por defecto
    if [[ -z "$url" ]]; then
        log_info "No se proporcionó MAIN_KEYCLOAK_URL, usando admin/admin"
        return 0
    fi
    
    log_info "Parseando URL de Keycloak..."
    
    # Patrón más simple para bash: [protocol://][user[:password]@]host[:port]
    # Usar regex compatible con bash (sin non-capturing groups)
    if [[ "$url" =~ ^(([^:]+)://)?((([^:@]+)(:([^@]+))?@)?([^:/]+)(:([0-9]+))?)$ ]]; then
        local protocol="${BASH_REMATCH[2]:-}"
        local username="${BASH_REMATCH[5]:-}"
        local password="${BASH_REMATCH[7]:-}"
        local host="${BASH_REMATCH[8]:-}"
        local port="${BASH_REMATCH[10]:-}"
        
        # Validar que al menos tengamos host
        if [[ -z "$host" ]]; then
            echo "Error: Host no especificado en MAIN_KEYCLOAK_URL" >&2
            return 1
        fi
        
        # Decodificar credenciales si existen
        if [[ -n "$username" ]]; then
            username=$(url_decode "$username")
            KEYCLOAK_ADMIN="$username"
            log_info "Usuario administrador extraído de MAIN_KEYCLOAK_URL"
        fi
        
        if [[ -n "$password" ]]; then
            password=$(url_decode "$password")
            KEYCLOAK_ADMIN_PASSWORD="$password"
            log_info "Contraseña de administrador extraída de MAIN_KEYCLOAK_URL"
        fi
        
        return 0
    else
        echo "Error: No se pudo parsear MAIN_KEYCLOAK_URL: $url" >&2
        return 1
    fi
}

# Variables globales para almacenar resultados parseados
KC_DB=""
KC_DB_URL=""
KC_DB_USERNAME=""
KC_DB_PASSWORD=""
KC_DB_URL_DATABASE="keycloak"
KEYCLOAK_ADMIN="admin"
KEYCLOAK_ADMIN_PASSWORD="admin"

# Función para parsear la URL de base de datos
parse_database_url() {
    local url="$1"
    
    # Si la URL está vacía, usar valores por defecto (H2)
    if [[ -z "$url" ]]; then
        log_info "No se proporcionó MAIN_DATABASE_URL, usando H2 (desarrollo)"
        return 0
    fi
    
    log_info "Parseando URL de base de datos..."
    
    # Verificar formato básico
    if [[ ! "$url" =~ :// ]]; then
        echo "Error: URL debe tener el formato driver://user:pass@host:port/db" >&2
        return 1
    fi
    
    # Extraer componentes usando regex
    if [[ "$url" =~ ^([^:]+)://((([^:@]+)(:([^@]*))?@)?([^:/]+)(:([0-9]+))?)?(/(.*))?(\?(.*))?$ ]]; then
        local driver="${BASH_REMATCH[1]}"
        local username="${BASH_REMATCH[4]}"
        local password="${BASH_REMATCH[6]}"
        local host="${BASH_REMATCH[7]}"
        local port="${BASH_REMATCH[9]}"
        local database_part="${BASH_REMATCH[11]}"
        local query_params="${BASH_REMATCH[13]}"
        
        # Reemplazar localhost con host.docker.internal para contenedores Docker
        if [[ "$host" == "localhost" ]]; then
            host="host.docker.internal"
            log_info "Host cambiado de localhost a host.docker.internal para compatibilidad con Docker"
        fi
        
        # Validar componentes esenciales
        if [[ -z "$driver" ]]; then
            echo "Error: Driver no especificado en la URL" >&2
            return 1
        fi
        
        if [[ -z "$host" ]]; then
            echo "Error: Host no especificado en la URL" >&2
            return 1
        fi
        
        # Decodificar URL para username y password si existen
        if [[ -n "$username" ]]; then
            username=$(url_decode "$username")
        fi
        
        if [[ -n "$password" ]]; then
            password=$(url_decode "$password")
        fi
        
        # Asignar puertos por defecto si no se especifica
        if [[ -z "$port" ]]; then
            case "$driver" in
                postgresql|postgres)
                    port=5432
                    ;;
                mysql)
                    port=3306
                    ;;
                sqlite)
                    port=""
                    ;;
                mssql)
                    port=1433
                    ;;
                oracle)
                    port=1521
                    ;;
            esac
        fi
        
        # Mapear driver a tipo de KC_DB
        case "$driver" in
            postgresql|postgres)
                KC_DB="postgres"
                ;;
            mysql)
                KC_DB="mysql"
                ;;
            sqlite)
                KC_DB="sqlite"
                ;;
            *)
                echo "Advertencia: Driver '$driver' no soportado, usando H2 por defecto" >&2
                return 0
                ;;
        esac
        
        # Construir URL JDBC para Keycloak (siempre usa database 'keycloak')
        if [[ -n "$KC_DB" && "$KC_DB" != "sqlite" ]]; then
            KC_DB_URL="jdbc:${driver}://${host}"
            if [[ -n "$port" ]]; then
                KC_DB_URL="${KC_DB_URL}:${port}"
            fi
            KC_DB_URL="${KC_DB_URL}/keycloak"
            
            # Agregar parámetros de query si existen
            if [[ -n "$query_params" ]]; then
                KC_DB_URL="${KC_DB_URL}?${query_params}"
            fi
        fi
        
        # Asignar credenciales
        KC_DB_USERNAME="$username"
        KC_DB_PASSWORD="$password"
        
        log_info "Variables de base de datos configuradas para driver: $driver"
        
        return 0
    else
        echo "Error: No se pudo parsear la URL de base de datos" >&2
        return 1
    fi
}

# Función para generar salida en formato ENV o archivo
output_env_vars() {
    local mode="$1"
    
    if [[ "$mode" == "env" ]]; then
        # Formato para usar en Dockerfile con ENV
        echo "# Variables de Keycloak generadas automáticamente"
        [[ -n "$KC_DB" ]] && echo "ENV KC_DB='$KC_DB'"
        [[ -n "$KC_DB_URL" ]] && echo "ENV KC_DB_URL='$KC_DB_URL'"
        [[ -n "$KC_DB_USERNAME" ]] && echo "ENV KC_DB_USERNAME='$KC_DB_USERNAME'"
        [[ -n "$KC_DB_PASSWORD" ]] && echo "ENV KC_DB_PASSWORD='$KC_DB_PASSWORD'"
        [[ -n "$KC_DB_URL_DATABASE" ]] && echo "ENV KC_DB_URL_DATABASE='$KC_DB_URL_DATABASE'"
        echo "ENV KEYCLOAK_ADMIN='$KEYCLOAK_ADMIN'"
        echo "ENV KEYCLOAK_ADMIN_PASSWORD='$KEYCLOAK_ADMIN_PASSWORD'"
    else
        # Formato de archivo .env tradicional (para compatibilidad)
        echo "# Variables de Keycloak generadas automáticamente"
        [[ -n "$KC_DB" ]] && echo "export KC_DB='$KC_DB'"
        [[ -n "$KC_DB_URL" ]] && echo "export KC_DB_URL='$KC_DB_URL'"
        [[ -n "$KC_DB_USERNAME" ]] && echo "export KC_DB_USERNAME='$KC_DB_USERNAME'"
        [[ -n "$KC_DB_PASSWORD" ]] && echo "export KC_DB_PASSWORD='$KC_DB_PASSWORD'"
        [[ -n "$KC_DB_URL_DATABASE" ]] && echo "export KC_DB_URL_DATABASE='$KC_DB_URL_DATABASE'"
        echo "export KEYCLOAK_ADMIN='$KEYCLOAK_ADMIN'"
        echo "export KEYCLOAK_ADMIN_PASSWORD='$KEYCLOAK_ADMIN_PASSWORD'"
    fi
}

# Función principal
main() {
    log_info "🔧 Iniciando parsing de configuración de Keycloak..."
    
    # Procesar URLs de base de datos
    if [[ -n "$MAIN_DATABASE_URL" ]]; then
        log_info "Procesando MAIN_DATABASE_URL..."
        if ! parse_database_url "$MAIN_DATABASE_URL"; then
            echo "Warning: No se pudo procesar MAIN_DATABASE_URL, continuando con defaults" >&2
        fi
    else
        log_info "MAIN_DATABASE_URL no proporcionada, usando H2 (desarrollo)"
    fi
    
    # Procesar URL de Keycloak
    if [[ -n "$MAIN_KEYCLOAK_URL" ]]; then
        log_info "Procesando MAIN_KEYCLOAK_URL..."
        if ! parse_keycloak_url "$MAIN_KEYCLOAK_URL"; then
            echo "Warning: No se pudo procesar MAIN_KEYCLOAK_URL, usando valores por defecto" >&2
        fi
    else
        log_info "MAIN_KEYCLOAK_URL no proporcionada, usando admin/admin"
    fi
    
    # Generar salida
    output_env_vars "$OUTPUT_MODE"
    
    log_info "✅ Configuración de Keycloak generada exitosamente!"
}

# Ejecutar función principal
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi