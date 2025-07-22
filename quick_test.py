#!/usr/bin/env python3.13
"""
Prueba rápida de dependencias básicas
"""

def quick_test():
    """Prueba rápida de las dependencias más importantes."""
    print("🚀 Prueba rápida de dependencias")
    print("=" * 50)
    
    tests = [
        ("langchain_core", "langchain_core"),
        ("langchain_openai", "langchain_openai"),
        ("langgraph", "langgraph"),
        ("dotenv", "dotenv"),
        ("openai", "openai")
    ]
    
    all_passed = True
    
    for name, module_name in tests:
        try:
            __import__(module_name)
            print(f"✅ {name}: OK")
        except ImportError as e:
            print(f"❌ {name}: FALLA - {e}")
            all_passed = False
    
    if all_passed:
        print("\n🎉 Todas las dependencias básicas están instaladas")
        print("💡 Puedes probar el chatbot con:")
        print("   python simple_customer_support.py")
    else:
        print("\n❌ Faltan algunas dependencias")
        print("💡 Ejecuta: bash install_dependencies.sh")
    
    return all_passed

if __name__ == "__main__":
    quick_test() 