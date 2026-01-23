# Extractor de CV con LLM

Sistema automatizado de extracción de datos de currículums vitae utilizando LangChain, Ollama y Qwen2.5.

## Descripción

Este proyecto convierte currículums en diversos formatos (PDF, DOCX, etc.) a Markdown y luego extrae información estructurada mediante un modelo de lenguaje local, produciendo datos validados en formato JSON.

## Características

- Conversión automática de archivos a Markdown usando MarkItDown
- Extracción de datos mediante LLM local (Qwen2.5:3b)
- Validación de esquema con Pydantic
- Corrección automática de artefactos de PDF (acentos separados)
- Formato de fechas estandarizado (MM-YYYY)
- Cero alucinaciones: solo extrae información explícita
- Salida JSON estructurada y validada

## Requisitos

```bash
pip install pydantic markitdown[all] langchain-ollama langchain-core
```

Adicionalmente, necesitas tener Ollama instalado y el modelo descargado:

```bash
ollama pull qwen2.5:3b
```

## Estructura de Datos Extraída

El sistema extrae la siguiente información:

- Datos personales (nombre, correo, teléfono, ubicación)
- Descripción profesional
- Experiencia laboral (puesto, empresa, fechas, actividades)
- Educación (institución, título, fechas)
- Habilidades técnicas
- Idiomas con nivel
- Certificaciones
- Enlaces (LinkedIn, GitHub)
- Estado laboral actual

## Uso

```python
from CV_extractor import LangExtractor

# Inicializar el extractor
engine = LangExtractor(model_name="qwen2.5:3b")

# Procesar un CV
data = engine.extract("ruta/al/CV.pdf")

# Mostrar resultado
import json
print(json.dumps(data, indent=2, ensure_ascii=False))
```

## Formato de Salida

```json
{
  "Nombre": "Juan Pérez",
  "Correo": "juan@example.com",
  "Telefono": "+52123456789",
  "Descripcion": "Ingeniero de software con 5 años de experiencia...",
  "Experiencia": [
    {
      "Puesto": "Desarrollador Senior",
      "Empresa": "Tech Corp",
      "Fecha_Inicio": "01-2020",
      "Fecha_Final": "01-2025",
      "Main_Activities": [
        "Desarrollo de aplicaciones web",
        "Liderazgo de equipo técnico"
      ]
    }
  ],
  "Educacion": [
    {
      "Institucion": "Universidad Nacional Autónoma",
      "Titulo": "Ingeniería en Sistemas",
      "Fecha_Inicio": "08-2015",
      "Fecha_Final": "06-2019"
    }
  ],
  "Skills": ["Python", "JavaScript", "Docker"],
  "Empleado": true,
  "Lenguajes": ["Español nativo", "Inglés C1"],
  "Certificaciones": ["AWS Solutions Architect"],
  "Linkedin": "https://linkedin.com/in/juanperez",
  "Github": "https://github.com/juanperez",
  "Ubicacion_Actual": "Ciudad de México, México"
}
```

## Reglas de Extracción

### Fechas
- Formato estándar: MM-YYYY
- Solo año disponible: se convierte a 01-YYYY
- "Present", "Actual", "Current": se convierte a la fecha actual

### Normalización de Texto
- Corrección automática de acentos separados (V´ICTOR → VÍCTOR)
- Preservación del idioma original del documento

### Actividades
- Se extrae cada punto de actividad como elemento individual
- Sin resúmenes ni combinaciones

### Estado Laboral
- `Empleado: true` si alguna fecha indica "Present" o "Actual"
- `Empleado: false` en caso contrario

## Personalización

### Cambiar el Modelo

```python
engine = LangExtractor(model_name="qwen2.5:7b")
```

### Modificar el Esquema

Edita las clases Pydantic en el código para ajustar los campos extraídos:

```python
class CVData(BaseModel):
    # Agregar nuevos campos aquí
    Campo_Nuevo: Optional[str] = Field(description="Descripción")
```

## Notas Técnicas

- **Temperature**: Configurada en 0 para máxima precisión
- **Modo JSON**: Forzado en Ollama para garantizar formato válido
- **Validación**: Pydantic valida automáticamente el esquema de salida
- **Sin plugins**: MarkItDown se ejecuta sin plugins por seguridad

## Limitaciones

- Requiere Ollama instalado localmente
- La calidad de extracción depende del formato del CV original
- PDFs muy complejos pueden requerir preprocesamiento adicional
