# 🔐 Configuración Segura de Variables de Entorno

## ⚠️ Importante: Seguridad de API Keys

**NUNCA** subas archivos `.env` o similares que contengan API keys reales a repositorios públicos.

---

## 🚀 Configuración Inicial

### 1. **Crear archivo `.env`**

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Crear archivo .env
touch .env
```

### 2. **Configurar variables de entorno**

Edita el archivo `.env` con tus credenciales:

```env
# OpenAI Configuration
OPENAI_API_KEY=tu_api_key_real_aqui

# LLM Configuration
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7

# Debug Mode
DEBUG_MODE=False
```

### 3. **Verificar que `.env` está en `.gitignore`**

El archivo `.gitignore` ya incluye:
```
.env
*.env
```

---

## 🔒 Protección Automática

### **GitHub Push Protection**

GitHub automáticamente detecta y bloquea:
- ✅ API Keys de OpenAI
- ✅ Tokens de acceso
- ✅ Claves privadas
- ✅ Credenciales de base de datos

### **Si recibes un error de Push Protection:**

1. **Eliminar archivos sensibles:**
   ```bash
   rm .env .env.backup
   git add .
   git commit -m "Remove sensitive files"
   ```

2. **Limpiar historial de Git:**
   ```bash
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch .env .env.backup' --prune-empty --tag-name-filter cat -- --all
   ```

3. **Forzar push:**
   ```bash
   git push --force-with-lease
   ```

---

## 📋 Archivos de Ejemplo

### **env_example.txt**
Contiene un ejemplo de configuración sin valores reales:

```env
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
DEBUG_MODE=False
```

---

## 🛠️ Scripts de Configuración

### **setup_environment.sh**
Script que verifica y configura el entorno:

```bash
bash setup_environment.sh
```

### **test_customer_bot.py**
Verifica que la configuración sea correcta:

```bash
python test_customer_bot.py
```

---

## ✅ Verificación de Seguridad

### **Antes de hacer commit:**

1. **Verificar archivos sensibles:**
   ```bash
   git status
   ```

2. **Verificar que `.env` no está en staging:**
   ```bash
   git diff --cached
   ```

3. **Verificar `.gitignore`:**
   ```bash
   cat .gitignore | grep env
   ```

---

## 🚨 En Caso de Emergencia

### **Si accidentalmente subiste una API key:**

1. **Revocar la API key inmediatamente** en OpenAI
2. **Generar una nueva API key**
3. **Limpiar el historial de Git** (ver arriba)
4. **Actualizar el archivo `.env`** con la nueva key

---

## 📚 Recursos Adicionales

- [GitHub Secret Scanning](https://docs.github.com/code-security/secret-scanning)
- [OpenAI API Key Management](https://platform.openai.com/api-keys)
- [Git Filter-Branch Documentation](https://git-scm.com/docs/git-filter-branch)

---

**¡Recuerda: La seguridad de tus credenciales es tu responsabilidad!** 🔐 