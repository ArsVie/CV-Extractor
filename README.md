# Pipeline de Extracción de CV (PDF a JSON)

Una herramienta local centrada en la privacidad para analizar currículums. Utiliza **Llama 3.2** y **MarkItDown** para convertir CVs en formato PDF a Markdown y extraer datos estructurados (JSON) mediante un LLM local.

## Prerrequisitos del Sistema

### 1. Ollama
Necesitas el binario de Ollama ejecutándose localmente para servir el modelo Llama 3.2.
- **Descarga:** [https://ollama.com/download](https://ollama.com/download)
- **Linux:** `curl -fsSL https://ollama.com/install.sh | sh`

### 2. Poppler
Requerido por `pdf2image` para leer archivos PDF.
- **Ubuntu/Debian:** `sudo apt-get install poppler-utils`
- **MacOS:** `brew install poppler`
- **Windows:** Descargar binario y agregar al PATH del sistema.
