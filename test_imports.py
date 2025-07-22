"""
Script de prueba para verificar que todas las importaciones funcionan correctamente
"""

def test_imports():
    """Prueba todas las importaciones necesarias."""
    print("🧪 Probando importaciones...")
    
    try:
        print("✅ Importando langgraph...")
        from langgraph.graph import StateGraph, END
        print("   - StateGraph y END importados correctamente")
        
        print("✅ Importando langchain_core...")
        from langchain_core.tools import ToolExecutor
        print("   - ToolExecutor importado correctamente")
        
        print("✅ Importando langchain_openai...")
        from langchain_openai import ChatOpenAI
        print("   - ChatOpenAI importado correctamente")
        
        print("✅ Importando langchain_core...")
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
        print("💡 Solución: Ejecuta 'pip install -r requirements.txt' para instalar las dependencias")
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
        
        # Probar ToolExecutor
        from langchain_core.tools import ToolExecutor
        
        def test_tool():
            return "Test tool executed"
        
        tools = [test_tool]
        tool_executor = ToolExecutor(tools)
        print("✅ ToolExecutor creado correctamente")
        
        print("🎉 ¡Funcionalidad básica funciona correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en funcionalidad básica: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de importación y funcionalidad")
    print("=" * 60)
    
    imports_ok = test_imports()
    
    if imports_ok:
        functionality_ok = test_basic_functionality()
        
        if functionality_ok:
            print("\n✅ ¡Todo está funcionando correctamente!")
            print("💡 Puedes ejecutar el chatbot con:")
            print("   python configurable_customer_support.py")
        else:
            print("\n❌ Hay problemas con la funcionalidad básica")
    else:
        print("\n❌ Hay problemas con las importaciones")
    
    print("\n" + "=" * 60) 