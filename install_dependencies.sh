#!/bin/bash

echo "🔧 Instalando dependencias para LangGraph Customer Support Bot"
echo "=" * 70

# Verificar si estamos en un entorno virtual
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ No estás en un entorno virtual"
    echo "💡 Activa tu entorno virtual primero:"
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

# Actualizar pip
echo "📦 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias básicas primero
echo "📦 Instalando dependencias básicas..."
pip install python-dotenv openai

# Instalar langchain-core primero
echo "📦 Instalando langchain-core..."
pip install "langchain-core>=0.2.0"

# Instalar langchain-openai
echo "📦 Instalando langchain-openai..."
pip install "langchain-openai>=0.1.0"

# Instalar langchain-community
echo "📦 Instalando langchain-community..."
pip install "langchain-community>=0.2.0"

# Instalar langchain
echo "📦 Instalando langchain..."
pip install "langchain>=0.2.0"

# Instalar langgraph
echo "📦 Instalando langgraph..."
pip install "langgraph>=0.5.0"

# Verificar instalación
echo "🧪 Verificando instalación..."
python test_customer_bot.py

echo "✅ Instalación completada!"
echo "💡 Ahora puedes ejecutar:"
echo "   python modern_customer_support.py (Recomendado - LangGraph 0.5.x)"
echo "   python simple_customer_support.py" 