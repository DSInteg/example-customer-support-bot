#!/usr/bin/env python3.13
"""
Script para verificar dónde está disponible ToolExecutor
"""

import sys
import importlib

def check_import_locations():
    """Verificar diferentes ubicaciones donde podría estar ToolExecutor."""
    
    possible_locations = [
        'langchain_core.tools',
        'langchain.tools', 
        'langgraph.prebuilt',
        'langchain.agents',
        'langchain_core.agents'
    ]
    
    print("🔍 Verificando ubicaciones de ToolExecutor...")
    
    for location in possible_locations:
        try:
            module = importlib.import_module(location)
            if hasattr(module, 'ToolExecutor'):
                print(f"✅ ToolExecutor encontrado en: {location}")
                return location
            else:
                print(f"❌ ToolExecutor NO encontrado en: {location}")
        except ImportError as e:
            print(f"❌ No se puede importar: {location} - {e}")
        except Exception as e:
            print(f"⚠️ Error al verificar {location}: {e}")
    
    return None

def check_available_classes():
    """Verificar qué clases están disponibles en langchain_core.tools."""
    try:
        import langchain_core.tools as tools_module
        print("\n📋 Clases disponibles en langchain_core.tools:")
        
        for item in dir(tools_module):
            if not item.startswith('_'):
                print(f"   - {item}")
                
    except Exception as e:
        print(f"❌ Error al verificar langchain_core.tools: {e}")

def check_available_classes_langchain_tools():
    """Verificar qué clases están disponibles en langchain.tools."""
    try:
        import langchain.tools as tools_module
        print("\n📋 Clases disponibles en langchain.tools:")
        
        for item in dir(tools_module):
            if not item.startswith('_'):
                print(f"   - {item}")
                
    except Exception as e:
        print(f"❌ Error al verificar langchain.tools: {e}")

def check_versions():
    """Verificar versiones de las librerías instaladas."""
    print("\n📦 Versiones instaladas:")
    
    packages = ['langchain', 'langchain-core', 'langchain-openai', 'langgraph']
    
    for package in packages:
        try:
            module = importlib.import_module(package)
            if hasattr(module, '__version__'):
                print(f"   - {package}: {module.__version__}")
            else:
                print(f"   - {package}: versión no disponible")
        except Exception as e:
            print(f"   - {package}: error - {e}")

if __name__ == "__main__":
    print("🔧 Verificando ToolExecutor y alternativas")
    print("=" * 60)
    
    check_versions()
    location = check_import_locations()
    check_available_classes()
    check_available_classes_langchain_tools()
    
    if location:
        print(f"\n✅ ToolExecutor está disponible en: {location}")
        print("💡 Actualiza las importaciones en los archivos del proyecto")
    else:
        print("\n❌ ToolExecutor no encontrado en ninguna ubicación")
        print("💡 Puede que necesites usar una alternativa o actualizar las dependencias")
    
    print("\n" + "=" * 60) 