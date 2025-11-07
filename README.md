Estado actual:

app/
├── main.py                    # Entry point - Registra routers y middlewares
├── config.py                  # Configuración centralizada
│
├── api/
│   ├── middleware.py         # Logging y manejo de errores
│   └── routes/               # Rutas separadas por dominio
│       ├── __init__.py       # Exporta todos los routers
│       ├── health.py         # Healthchecks y status
│       └── documents.py      # Upload y listado de documentos
│
├── core/
│   └── llm/
│       └── client.py         # Cliente Groq centralizado
│
├── services/
│   └── document_service.py   # Lógica de negocio de documentos
│
└── utils/
    └── logger.py             # Logger centralizado