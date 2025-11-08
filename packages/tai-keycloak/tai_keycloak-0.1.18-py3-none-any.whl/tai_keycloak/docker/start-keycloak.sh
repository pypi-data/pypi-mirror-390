#!/bin/bash

# Función para logging
log_info() {
    echo "[INFO] $*" >&2
}

log_info "� Starting Keycloak with buildtime configuration..."

# Cargar variables de configuración generadas en buildtime
if [ -f "/opt/keycloak/buildtime_exports.env" ]; then
    log_info "� Loading buildtime configuration..."
    source /opt/keycloak/buildtime_exports.env
    log_info "✅ Configuration loaded successfully"
else
    log_info "⚠️  No buildtime configuration found, using minimal defaults"
    export KEYCLOAK_ADMIN='admin'
    export KEYCLOAK_ADMIN_PASSWORD='admin'
fi

echo "🔍 Database configuration check:"
echo "  KC_DB: ${KC_DB:-'not set'}"
echo "  KC_DB_URL: ${KC_DB_URL:-'not set'}"
echo ""

if [ -z "${KC_DB}" ]; then
    echo "🏃 Starting Keycloak in development mode (H2 database)..."
    
    # Intentar con import primero, si falla, continuar sin import
    if [ -f "/opt/keycloak/data/import/main-realm.json" ]; then
        echo "📥 Attempting to import realm configuration..."
        if ! /opt/keycloak/bin/kc.sh start-dev --import-realm --http-port=${KC_HTTP_PORT}; then
            echo "⚠️  Import failed, starting without import..."
            # exec /opt/keycloak/bin/kc.sh start-dev --http-port=${KC_HTTP_PORT}
            /opt/keycloak/bin/kc.sh start-dev --import-realm --http-port=${KC_HTTP_PORT} --verbose
        fi
    else
        echo "ℹ️  No realm configuration found, starting clean..."
        exec /opt/keycloak/bin/kc.sh start-dev --http-port=${KC_HTTP_PORT}
    fi
else
    echo "🏭 Starting Keycloak in production mode with external database..."
    echo "🔧 Building configuration for ${KC_DB}..."
    
    if ! /opt/keycloak/bin/kc.sh build --db=${KC_DB}; then
        echo "❌ Failed to build configuration for ${KC_DB}"
        exit 1
    fi
    
    if [ -f "/opt/keycloak/data/import/main-realm.json" ]; then
        echo "📥 Starting with realm import..."
        if ! /opt/keycloak/bin/kc.sh start --import-realm --http-port=${KC_HTTP_PORT}; then
            echo "⚠️  Import failed, starting without import..."  
            exec /opt/keycloak/bin/kc.sh start --http-port=${KC_HTTP_PORT}
        fi
    else
        echo "ℹ️  No realm configuration found, starting clean..."
        exec /opt/keycloak/bin/kc.sh start --http-port=${KC_HTTP_PORT}
    fi
fi