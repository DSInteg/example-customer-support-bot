#!/bin/bash

echo "🔧 Configurando entorno virtual para LangGraph Customer Support Bot"
echo "=" * 60

# Verificar si estamos en un entorno virtual
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ No estás en un entorno virtual"
    echo "💡 Crea y activa un entorno virtual primero:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    exit 1
fi

echo "✅ Entorno virtual activado: $VIRTUAL_ENV"

# Desinstalar paquetes conflictivos
echo "🧹 Limpiando paquetes conflictivos..."
pip uninstall -y langgraph langchain langchain-openai langchain-community langchain-core langchain-text-splitters langgraph-prebuilt

# Limpiar cache de pip
echo "🗑️ Limpiando cache de pip..."
pip cache purge

# Instalar dependencias actualizadas
echo "📦 Instalando dependencias actualizadas..."
pip install -r requirements.txt

# Verificar instalación
echo "🧪 Verificando instalación..."
python test_imports.py

echo "✅ Configuración completada!"
echo "💡 Ahora puedes ejecutar:"
echo "   python configurable_customer_support.py" 