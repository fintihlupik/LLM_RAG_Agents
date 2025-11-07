# 🤖 Asistente Financiero con LLM + RAG + Agentes

API REST para análisis inteligente de informes financieros utilizando modelos de lenguaje (LLM), Retrieval-Augmented Generation (RAG) y sistemas multi-agente.

---

## 📋 Estado Actual del Proyecto

### ✅ Implementado (Fase 1: Fundación)

#### **🏗️ Arquitectura Base**
- ✅ FastAPI configurado con estructura modular
- ✅ Sistema de logging centralizado
- ✅ Gestión de configuración con Pydantic
- ✅ Middlewares para logging de requests y manejo de errores
- ✅ Documentación automática (Swagger/OpenAPI)

#### **🤖 Integración LLM**
- ✅ Cliente Groq integrado y funcional
- ✅ Modelo: `llama-3.3-70b-versatile`
- ✅ Verificación de conexión en startup
- ✅ Sistema preparado para múltiples modelos

#### **📄 Gestión de Documentos**
- ✅ API para subir documentos financieros
- ✅ Soporte multi-formato:
  - PDF (informes, balances)
  - Excel (.xlsx, .xls)
  - Word (.docx, .doc)
  - CSV (datos tabulares)
- ✅ Listado de documentos con metadata
- ✅ Almacenamiento organizado en `uploads/raw/`

#### **🔌 Endpoints Disponibles**
| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información de la API |
| `/health` | GET | Healthcheck del sistema |
| `/docs` | GET | Documentación interactiva |
| `/documents/upload` | POST | Subir documentos |
| `/documents/` | GET | Listar documentos |

---

## 🏗️ Arquitectura del Proyecto

```
app/
├── main.py                    # Entry point - Configura FastAPI y middlewares
├── config.py                  # Configuración centralizada (Pydantic Settings)
│
├── api/
│   ├── middleware.py         # Logging de requests y manejo de errores
│   └── routes/               # Rutas separadas por dominio
│       ├── __init__.py       # Exporta todos los routers
│       ├── health.py         # Healthchecks y status
│       └── documents.py      # Upload y listado de documentos
│
├── core/
│   ├── llm/
│   │   └── client.py         # Cliente Groq centralizado (Singleton)
│   ├── rag/                  # [Próximamente] Vector store y embeddings
│   └── agents/               # [Próximamente] Sistema multi-agente
│
├── services/
│   └── document_service.py   # Lógica de negocio de documentos
│
├── utils/
│   └── logger.py             # Logger centralizado
│
└── data/                     # [Próximamente] Procesamiento de datos

uploads/
├── raw/                      # Documentos sin procesar
└── processed/                # [Próximamente] Documentos procesados
```

---

## 🚀 Instalación y Uso

### **1️⃣ Requisitos Previos**
- Python 3.10+
- API Key de Groq ([obtener aquí](https://console.groq.com))

### **2️⃣ Instalación**

```bash
# Clonar repositorio
git clone https://github.com/fintihlupik/LLM_RAG_Agents.git
cd LLM_RAG_Agents

# Crear entorno virtual
python -m venv .venv
source .venv/Scripts/activate  # En Windows (Git Bash)
# .venv\Scripts\activate.ps1   # En Windows (PowerShell)

# Instalar dependencias
pip install -r requirements.txt
```

### **3️⃣ Configuración**

Crea un archivo `.env` en la raíz del proyecto:

```env
# API Keys
GROQ_API_KEY=tu_api_key_aqui

# Configuración del modelo
LLM_MODEL=llama-3.3-70b-versatile
TEMPERATURE=0.5
MAX_TOKENS=2000

# Configuración de la API
UPLOAD_DIR=./uploads/raw
```

### **4️⃣ Ejecutar**

```bash
python -m app.main
```

La API estará disponible en: **http://localhost:8000**

- **Documentación interactiva:** http://localhost:8000/docs
- **Healthcheck:** http://localhost:8000/health

---

## 🧪 Probar la API

### **Usando Swagger UI**
1. Abre http://localhost:8000/docs
2. Expande `/documents/upload`
3. Click en "Try it out"
4. Selecciona un archivo PDF/Excel
5. Click en "Execute"

### **Usando curl/PowerShell**
```bash
# Subir un documento
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@informe_financiero.pdf"

# Listar documentos
curl http://localhost:8000/documents/
```

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Propósito |
|------------|-----------|-----------|
| **Framework** | FastAPI 0.115.0 | API REST rápida |
| **LLM** | Groq (Llama 3.3 70B) | Modelo de lenguaje para análisis |
| **Validación** | Pydantic 2.8.2 | Validación de datos y config |
| **Servidor** | Uvicorn 0.32.0 | ASGI server con hot-reload |
| **Logging** | Python logging | Sistema de logs centralizado |

---

## 📅 Roadmap

### **Fase 1: Fundación** ✅ COMPLETADA
- [x] Setup inicial del proyecto
- [x] Integración con Groq LLM
- [x] API para subir documentos
- [x] Arquitectura modular

### **Fase 2: Procesamiento de Documentos** 🚧 PRÓXIMAMENTE
- [ ] Extracción de texto de PDFs
- [ ] Parsing de Excel (hojas, tablas)
- [ ] Chunking inteligente de documentos
- [ ] Generación de embeddings

### **Fase 3: RAG (Retrieval-Augmented Generation)** 📅 PLANIFICADO
- [ ] Vector database (ChromaDB/FAISS)
- [ ] Búsqueda semántica
- [ ] Sistema de recuperación de contexto
- [ ] Endpoint para queries con RAG

### **Fase 4: Sistema Multi-Agente** 📅 PLANIFICADO
- [ ] Agente para análisis de métricas
- [ ] Agente para comparación temporal
- [ ] Agente para contexto de mercado
- [ ] Orquestador de agentes

### **Fase 5: Análisis Avanzado** 📅 FUTURO
- [ ] Comparación de reportes trimestrales/anuales
- [ ] Detección de tendencias
- [ ] Generación de insights automáticos
- [ ] Dashboard de visualización

---

## 🤝 Contribuir

Este proyecto está en desarrollo activo. Pull requests son bienvenidos.

### **Principios de Desarrollo**
- ✅ Single Responsibility Principle
- ✅ DRY (Don't Repeat Yourself)
- ✅ Separation of Concerns
- ✅ Modularidad y escalabilidad

---

## 📝 Licencia

MIT License

---

## 👤 Autor

**Polina** - [fintihlupik](https://github.com/fintihlupik)

Proyecto: [LLM_RAG_Agents](https://github.com/fintihlupik/LLM_RAG_Agents)

---

**⭐ Si te gusta el proyecto, dale una estrella en GitHub!**