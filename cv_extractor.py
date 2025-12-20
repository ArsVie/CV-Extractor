import ollama
import json
import logging
from markitdown import MarkItDown
from typing import Optional, Dict, Any, List

# Configure minimal logging
logging.basicConfig(level=logging.ERROR)

class CVExtractor:
    def __init__(self, model_name: str = "llama3.2"):
        self.model = model_name
        self.md_converter = MarkItDown(enable_plugins=False)
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        """Returns the strict schema definition for the LLM."""
        return """
        You are a strict Resume Extraction Engine. Parse the Markdown CV into a precise JSON format.

        CRITICAL RULES:
        1. EVIDENCE ONLY: Extract ONLY explicit info. If missing, use null.
        2. NO INFERENCE: Do not calculate ages/durations.
        3. DATES: Format "MM-YYYY". If "Present/Actual", return "12-2025".
        4. BOOLEAN: "Empleado" is true if any job is currently active ("Present").

        REQUIRED JSON STRUCTURE:
        {
            "Name": "string or null",
            "Correo": "string or null",
            "Telefono": "string or null",
            "Descripcion": "string or null",
            "Experiencia": [
                {
                    "Puesto": "string",
                    "Empresa": "string",
                    "Year initial": "MM-YYYY",
                    "Final Year": "MM-YYYY",
                    "Main Activities": ["string"],
                    "Tech Stack": ["Inferred Tool 1", "Inferred Tool 2"]
                }
            ],
            "Educacion": [
                { "Institucion": "string", "Titulo": "string", "Fecha": "string" }
            ],
            "Skills": ["string"],
            "Empleado": "boolean",
            "Lenguajes": ["string"],
            "Certificaciones": ["string"],
            "Linkedin": "string or null",
            "Github": "string or null",
            "Ubicacion Actual": "string or null"
        }

        EXAMPLE Descripcion:
        Estudiante de Matemáticas Aplicadas con experiencia en análisis de datos para IA, gestión operativa y reclutamiento
digital. Competente en visualización de datos y modelado estadístico utilizando herramientas como Python y R.
Capacidad demostrada para optimizar procesos mediante el análisis de información y la gestión de bases de datos.
        """

    def pdf_to_markdown(self, file_path: str) -> Optional[str]:
        """Converts PDF to Markdown string."""
        try:
            result = self.md_converter.convert(file_path)
            return result.text_content
        except Exception as e:
            logging.error(f"MarkItDown Conversion Error: {e}")
            return None

    def extract_json(self, md_text: str, context_tags: List[str] = []) -> Dict[str, Any]:
        """Extracts structured data from Markdown text using Ollama."""
        if not md_text:
            return {}

        # Append specific context tags if provided (e.g., ["Data Science", "Management"])
        context_str = " ".join(context_tags)
        full_prompt = f"{self.system_prompt}\n\nContext Focus: {context_str}"

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': full_prompt},
                    {'role': 'user', 'content': f"Extract data from:\n\n{md_text}"}
                ],
                format='json',
                options={'temperature': 0} # Deterministic output
            )
            return json.loads(response['message']['content'])
        except json.JSONDecodeError:
            logging.error("Model failed to produce valid JSON.")
            return {}
        except Exception as e:
            logging.error(f"Ollama Inference Error: {e}")
            return {}

    def process(self, file_path: str, context_tags: List[str] = []) -> Dict[str, Any]:
        """Main pipeline entry point: PDF -> JSON."""
        md_text = self.pdf_to_markdown(file_path)
        if md_text:
            return self.extract_json(md_text, context_tags)
        return {"error": "Failed to parse PDF"}

# --- Usage Example ---
if __name__ == "__main__":
    # Initialize the extractor
    pipeline = CVExtractor()

    # Run the pipeline
    # Replace with your actual file path
    cv_data = pipeline.process("/content/cv-1-1.pdf", context_tags=["Data Science"])

    # Output the result
    print(json.dumps(cv_data, indent=4, ensure_ascii=False))
