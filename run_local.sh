#!/bin/bash
# Script para ejecutar el bot en local con logs visibles

# Cargar variables de entorno
export $(cat .env | grep -v '^#' | xargs)

# Mostrar el token del bot (para verificar)
echo "🤖 Iniciando bot con token: ${TELEGRAM_BOT_TOKEN:0:20}..."

# Ejecutar el bot
python3 -m src.bot.main
