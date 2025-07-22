#!/usr/bin/env python3
"""
Script de prueba para verificar la instalación del chatbot
Verifica todas las importaciones necesarias
"""

import sys
import os

def check_python_version():
    """Verificar que estamos usando Python 3.x."""
    print(f"🐍 Python version: {sys.version}")
    if not sys.version.startswith("3"):
        print("⚠️  Advertencia: Se recomienda usar Python 3.x")
    else:
        print("✅ Python 3.x detectado correctamente")

def check_virtual_env():
    """Verificar que estamos en un entorno virtual."""
    venv = os.environ.get('VIRTUAL_ENV', '')
    print(f"🔧 Entorno virtual: {venv}")
    
    if venv:
        print("✅ Entorno virtual detectado")
        return True
    else:
        print("❌ No estás en un entorno virtual")
        print("💡 Activa tu entorno virtual:")
        print("   source venv/bin/activate")
        return False

def test_imports():
    """Prueba todas las importaciones necesarias."""
    print("\n🧪 Probando importaciones...")
    
    try:
        print("✅ Importando langgraph...")
        from langgraph.graph import StateGraph, END
        print("   - StateGraph y END importados correctamente")
        
        print("✅ Importando langchain_core...")
        # ToolExecutor puede no estar disponible en todas las versiones
        try:
            from langchain_core.tools import ToolExecutor
            print("   - ToolExecutor importado correctamente")
        except ImportError:
            print("   - ToolExecutor no disponible, usando implementación alternativa")
            print("   - La versión simplificada funcionará correctamente")
        
        print("✅ Importando langchain_openai...")
        from langchain_openai import ChatOpenAI
        print("   - ChatOpenAI importado correctamente")
        
        print("✅ Importando langchain_core messages...")
        from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        print("   - Mensajes y prompts importados correctamente")
        
        print("✅ Importando langchain.tools...")
        from langchain.tools import tool
        print("   - Decorador @tool importado correctamente")
        
        print("✅ Importando dotenv...")
        from dotenv import load_dotenv
        print("   - load_dotenv importado correctamente")
        
        print("✅ Importando openai...")
        import openai
        print("   - openai importado correctamente")
        
        print("\n🎉 ¡Todas las importaciones funcionan correctamente!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("💡 Solución: Ejecuta 'bash setup_environment.sh' para configurar el entorno")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False

def test_basic_functionality():
    """Prueba funcionalidad básica."""
    print("\n🔧 Probando funcionalidad básica...")
    
    try:
        # Probar creación de un grafo simple
        from langgraph.graph import StateGraph
        
        # Definir un estado simple
        from typing import TypedDict, Annotated, Sequence
        from langchain_core.messages import BaseMessage
        
        class SimpleState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], "The messages"]
        
        # Crear grafo
        workflow = StateGraph(SimpleState)
        print("✅ StateGraph creado correctamente")
        
        # Probar ToolExecutor (opcional)
        try:
            from langchain_core.tools import ToolExecutor
            
            def test_tool():
                return "Test tool executed"
            
            tools = [test_tool]
            tool_executor = ToolExecutor(tools)
            print("✅ ToolExecutor creado correctamente")
        except ImportError:
            print("✅ ToolExecutor no disponible, pero la versión simplificada funcionará")
        
        print("🎉 ¡Funcionalidad básica funciona correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en funcionalidad básica: {e}")
        return False

def test_config_file():
    """Prueba que el archivo de configuración funciona."""
    print("\n⚙️ Probando archivo de configuración...")
    
    try:
        from config import get_config, get_environment_config
        
        config = get_config()
        env_config = get_environment_config()
        
        print("✅ Configuración cargada correctamente")
        print(f"   - Modelo: {env_config.get('model', 'No configurado')}")
        print(f"   - API Key configurada: {'Sí' if env_config.get('openai_api_key') else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del chatbot")
    print("=" * 70)
    
    # Verificar versión de Python
    check_python_version()
    
    # Verificar entorno virtual
    venv_ok = check_virtual_env()
    
    if venv_ok:
        # Probar importaciones
        imports_ok = test_imports()
        
        if imports_ok:
            # Probar funcionalidad básica
            functionality_ok = test_basic_functionality()
            
            # Probar configuración
            config_ok = test_config_file()
            
            if functionality_ok and config_ok:
                print("\n✅ ¡Todo está funcionando correctamente!")
                print("💡 Puedes ejecutar el chatbot con:")
                print("   python enhanced_customer_support.py (Recomendado)")
                print("   python simple_customer_support.py")
                print("   python configurable_customer_support.py")
            else:
                print("\n❌ Hay problemas con la funcionalidad o configuración")
        else:
            print("\n❌ Hay problemas con las importaciones")
    else:
        print("\n❌ Problema con el entorno virtual")
    
    print("\n" + "=" * 70) 