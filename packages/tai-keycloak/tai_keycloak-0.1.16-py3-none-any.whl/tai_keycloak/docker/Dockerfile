# Dockerfile para instancia de Keycloak preconfigurada
FROM quay.io/keycloak/keycloak:24.0.0

# Metadatos
LABEL maintainer="MateoSaezMata <msaez@triplealpha.in>"
LABEL description="Keycloak instance with preconfigured environment"
LABEL version="0.1.0"

# Definir argumentos de construcción
# Variables para URLs que serán parseadas automáticamente
ARG MAIN_DATABASE_URL
ARG MAIN_KEYCLOAK_URL
ARG KEYCLOAK_API_CLIENT_SECRET=misupersecreto

# Establecer variables de entorno base
ENV KC_HTTP_ENABLED=true
# ENV KC_HOSTNAME=localhost
ENV KC_HOSTNAME_STRICT=false
ENV KC_HOSTNAME_STRICT_HTTPS=false
ENV KC_PROXY_HEADERS=xforwarded
ENV KC_HTTP_PORT=8090
ENV KC_LOG_LEVEL=INFO
ENV KC_HEALTH_ENABLED=true
ENV KEYCLOAK_API_CLIENT_SECRET=${KEYCLOAK_API_CLIENT_SECRET}

# Copiar realm preconfigurado y scripts de configuración
COPY main-realm.json /opt/keycloak/data/import/
COPY parser.sh /opt/keycloak/bin/
COPY build-env.sh /opt/keycloak/bin/

# Crear directorio para logs y configurar permisos
USER root
RUN mkdir -p /opt/keycloak/logs && chown keycloak:keycloak /opt/keycloak/logs

# Hacer ejecutables los scripts
RUN chmod +x /opt/keycloak/bin/parser.sh && \
    chmod +x /opt/keycloak/bin/build-env.sh

# Ejecutar parsing de configuración en buildtime y generar archivo de variables
RUN /opt/keycloak/bin/build-env.sh "${MAIN_DATABASE_URL}" "${MAIN_KEYCLOAK_URL}" > /opt/keycloak/buildtime_vars.env && \
    echo "# Variables generadas en buildtime:" && cat /opt/keycloak/buildtime_vars.env

# Convertir las líneas ENV en export para que puedan ser sourced
RUN sed 's/^ENV /export /' /opt/keycloak/buildtime_vars.env > /opt/keycloak/buildtime_exports.env && \
    chown keycloak:keycloak /opt/keycloak/buildtime_exports.env

# Copiar script de entrada simplificado
COPY start-keycloak.sh /opt/keycloak/bin/start-keycloak.sh
RUN chmod +x /opt/keycloak/bin/start-keycloak.sh && \
    chown keycloak:keycloak /opt/keycloak/bin/start-keycloak.sh

# Volver al usuario keycloak
USER keycloak

# Exponer puerto configurado (por defecto 80 para Azure Web Apps)
EXPOSE ${KC_HTTP_PORT}

# Sobrescribir ENTRYPOINT y usar nuestro script
ENTRYPOINT []
CMD ["/opt/keycloak/bin/start-keycloak.sh"]

# Healthcheck adaptativo según el puerto configurado
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD { printf 'HEAD /health/ready HTTP/1.0\r\n\r\n' >&0; grep 'HTTP/1.0 200'; } 0<>/dev/tcp/localhost/${KC_HTTP_PORT:-80}