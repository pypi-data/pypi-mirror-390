# 📦 INSTALAR BIOQL ASSISTANT v4.9.8 EN VSCODE

## ✅ INSTALACIÓN MANUAL (RECOMENDADO):

### 1️⃣ **Abrir VSCode**

### 2️⃣ **Ir a Extensions**
- Presiona `Cmd+Shift+X` (Mac) o `Ctrl+Shift+X` (Windows/Linux)
- O haz clic en el ícono de Extensions en la barra lateral

### 3️⃣ **Instalar desde VSIX**
- Haz clic en el menú `...` (tres puntos) en la esquina superior derecha del panel Extensions
- Selecciona **"Install from VSIX..."**
- Navega a: `/Users/heinzjungbluth/Desktop/Server_bioql/vscode_extension/bioql-assistant/`
- Selecciona: `bioql-assistant-4.9.8.vsix`
- Haz clic en **Install**

### 4️⃣ **Recargar VSCode**
- Cuando termine la instalación, haz clic en **"Reload Required"**
- O presiona `Cmd+Shift+P` → "Developer: Reload Window"

---

## 🔍 VERIFICAR INSTALACIÓN:

### Opción 1: Ver extensiones activas
```
Cmd+Shift+P → "Developer: Show Running Extensions"
Busca "bioql-assistant" → Debe aparecer ACTIVADA ✅
```

### Opción 2: Verificar en lista de extensiones
```
Cmd+Shift+X → Busca "bioql"
Debe aparecer "BioQL Code Assistant v4.9.8" instalado
```

---

## 🚀 USAR @bioql EN CHAT:

1. Abre el panel de chat en VSCode
2. Escribe: `@bioql Design a drug for diabetes`
3. El asistente debe responder con código BioQL

---

## ⚙️ CONFIGURACIÓN (Opcional):

### Abrir Settings:
```
Cmd+, (o Ctrl+,)
Busca "BioQL"
```

### Configuraciones importantes:
```json
{
  "bioql.enableChat": true,
  "bioql.mode": "modal",
  "bioql.modalUrl": "https://spectrix--bioql-agent-create-fastapi-app.modal.run",
  "bioql.apiKey": "bioql_3EI7-xILRTsxWtjPnkzWjXYV0W_zXgAfH7hVn4VH_CA"
}
```

---

## 📊 NUEVAS FEATURES EN v4.9.8:

✅ **Pharmaceutical Scoring**
- Lipinski Rule of 5 compliance
- QED Score (0-1 drug-likeness)
- SA Score (1-10 synthetic accessibility)
- PAINS detection

✅ **Auto SMILES Neutralization**
- Detecta y neutraliza átomos cargados (N+, O-)
- Fix automático para moléculas complejas

✅ **Better Error Logging**
- Traceback completo de errores
- Mensajes claros de problemas

✅ **Production Drug Design**
- Ki/IC50 calculation
- Provenance tracking
- Artifact management

---

## 🐛 TROUBLESHOOTING:

### Si @bioql no aparece:
1. Verifica que la extensión esté instalada y activada
2. Recarga VSCode: `Cmd+Shift+P` → "Developer: Reload Window"
3. Revisa Developer Tools: `Cmd+Shift+P` → "Developer: Toggle Developer Tools"
4. Busca errores en la consola relacionados con "bioql"

### Si da error "No activated agent":
1. Cierra VSCode completamente
2. Abre de nuevo VSCode
3. Espera 10 segundos a que la extensión se active
4. Intenta `@bioql` de nuevo

---

## 📝 TEST RÁPIDO:

Crea un archivo `test.py` y usa `@bioql`:

```
@bioql Design a drug for obesity targeting GLP1R with pharmaceutical scoring
```

La respuesta debe incluir:
- Código Python con `from bioql import quantum`
- Molecular docking con Vina
- Pharmaceutical scores (Lipinski, QED, SA)
- Ki/IC50 calculations

---

## 📍 ARCHIVOS DE LA EXTENSIÓN:

```
Extensión: bioql-assistant-4.9.8.vsix
Ubicación: /Users/heinzjungbluth/Desktop/Server_bioql/vscode_extension/bioql-assistant/
Tamaño: 50KB
Modal Agent: https://spectrix--bioql-agent-create-fastapi-app.modal.run
BioQL Version: 5.5.7
```
