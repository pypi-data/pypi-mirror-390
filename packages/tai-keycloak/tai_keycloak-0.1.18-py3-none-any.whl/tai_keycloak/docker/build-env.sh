#!/bin/bash

# Script para generar variables ENV durante el build de Dockerfile
# Ejecuta parser.sh y convierte la salida en líneas ENV válidas para Dockerfile

set -e

# Función para logging (a stderr para no interferir con la salida)
log_info() {
    echo "[BUILD-ENV] $*" >&2
}

# Obtener argumentos del dockerfile (ARGs)
MAIN_DATABASE_URL="${1:-}"
MAIN_KEYCLOAK_URL="${2:-}"

log_info "🏗️  Generando configuración ENV para buildtime..."
log_info "📊 MAIN_DATABASE_URL: ${MAIN_DATABASE_URL:-'(vacío)'}"
log_info "👤 MAIN_KEYCLOAK_URL: ${MAIN_KEYCLOAK_URL:-'(vacío)'}"

# Determinar la ubicación del parser.sh
PARSER_PATH=""
if [[ -f "/opt/keycloak/bin/parser.sh" ]]; then
    PARSER_PATH="/opt/keycloak/bin/parser.sh"
elif [[ -f "./parser.sh" ]]; then
    PARSER_PATH="./parser.sh"
else
    log_info "❌ No se encontró parser.sh"
    exit 1
fi

# Ejecutar parser en modo env y capturar solo las líneas ENV
PARSER_OUTPUT=$($PARSER_PATH "$MAIN_DATABASE_URL" "$MAIN_KEYCLOAK_URL" "env" 2>/tmp/parser_errors.log)
ENV_OUTPUT=$(echo "$PARSER_OUTPUT" | grep "^ENV " || true)

if [[ -n "$ENV_OUTPUT" ]]; then
    echo "$ENV_OUTPUT"
    log_info "✅ Variables ENV generadas correctamente"
else
    log_info "⚠️  No se pudieron generar variables ENV, usando defaults mínimos"
    log_info "Parser output: $PARSER_OUTPUT"
    echo "ENV KEYCLOAK_ADMIN='admin'"
    echo "ENV KEYCLOAK_ADMIN_PASSWORD='admin'"
    echo "ENV KC_DB_URL_DATABASE='keycloak'"
fi

log_info "🎯 Configuración ENV lista para Dockerfile"