#!pip install langchain_ollama
#!pip install markitdown[all]
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from markitdown import MarkItDown
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

#Current date as MM-YYYY
from datetime import datetime
now = datetime.now()
# --- 1. DEFINE THE STRICT SCHEMA (PYDANTIC) ---
# This replaces the manual JSON description. 
# The LLM will strictly adhere to these types.

class ExperienceItem(BaseModel):
    Puesto: Optional[str] = Field(description="Job Title")
    Empresa: Optional[str] = Field(description="Company Name")
    Year_initial: Optional[str] = Field(description="MM-YYYY format. If only year, use 01-YYYY.")
    Final_Year: Optional[str] = Field(description=f"MM-YYYY. If Present/Actual, use {current_date}.")
    Main_Activities: List[str] = Field(description="List of explicitly stated activities.")

class EducationItem(BaseModel):
    Institucion: Optional[str] = Field(description="University or School name")
    Titulo: Optional[str] = Field(description="Degree or Certificate name")
    Fecha: Optional[str] = Field(description="MM-YYYY or Date range")

class CVData(BaseModel):
    Nombre: Optional[str] = Field(description="Full name of the candidate")
    Correo: Optional[str] = Field(description="Email address")
    Telefono: Optional[str] = Field(description="Phone number without spaces if possible")
    Descripcion: Optional[str] = Field(description="Profile description from the top of the text")
    Experiencia: List[ExperienceItem] = Field(description="Work history")
    Educacion: List[EducationItem] = Field(description="Academic history")
    Skills: List[str] = Field(description="Explicit list of skills found in Skills/Tools section")
    Empleado: bool = Field(description="True if currently employed (dates include Present/Actual), else False")
    Lenguajes: List[str] = Field(description="non Tech Spoken languages (spanish, chinese, etc.)")
    Certificaciones: List[str] = Field(description="Certifications obtained")
    Linkedin: Optional[str] = Field(description="LinkedIn URL")
    Github: Optional[str] = Field(description="GitHub URL")
    Ubicacion_Actual: Optional[str] = Field(description="City/Country")

# --- 2. CONFIGURATION & PROMPT ---

# We adapt your original SML into a LangChain Prompt Template
EXTRACT_TEMPLATE = """
You are a strict Resume Extraction Engine.
Your task is to parse a Markdown (MD) CV and extract data into a precise JSON format.

### CRITICAL RULES (ZERO HALLUCINATION):
1. **EVIDENCE ONLY**: Extract ONLY information explicitly written in the text.
2. **NO INFERENCE**: Do not compute ages or guess locations.
3. **LANGUAGE**: Keep values in original language.

### DATE FORMATTING RULES (STRICT):
- Format: "MM-YYYY" (String).
- If only Year (e.g., "2020"): Return "01-2020".
- **CRITICAL**: If "Present", "Actual", "Current" in ANY language: YOU MUST CONVERT to {{current_date}}.

### SKILL EXTRACTION:
- **Global Skills**: Explicit skills from the Skills section.

### ACTIVITY EXTRACTION:
- Extract EVERY bullet point under each job as a separate list item
- Do NOT summarize or combine activities

### EMPLOYMENT STATUS:
- Set 'Empleado' to True if any job date indicates "Present" or "Actual".

{format_instructions}

### INPUT CV (MARKDOWN):
{cv_text}
"""

class LangExtractor:
    def __init__(self, model_name="llama3.2"):
        # Initialize the LLM
        self.llm = ChatOllama(
            model=model_name,
            temperature=0, # Strictness
            format="json"  # Force JSON mode in Ollama
        )
        
        # Initialize the Parser based on our Pydantic Schema
        self.parser = JsonOutputParser(pydantic_object=CVData)
        
        # Create the Prompt
        self.prompt = PromptTemplate(
            template=EXTRACT_TEMPLATE,
            input_variables=["cv_text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
            current_date=now.strftime("%m-%Y")
        )
        
        # Create the Chain
        self.chain = self.prompt | self.llm | self.parser
        
        # Initialize MarkItDown
        self.md_converter = MarkItDown(enable_plugins=False)

    def convert_to_markdown(self, file_path: str) -> str:
        """Converts file to MD using MarkItDown."""
        print(f"📄 Converting '{file_path}'...")
        try:
            result = self.md_converter.convert(file_path)
            return result.text_content
        except Exception as e:
            print(f"❌ Conversion Error: {e}")
            return None

    def extract(self, file_path: str) -> dict:
        """Pipeline: File -> Markdown -> LLM -> JSON"""
        
        # 1. Convert
        md_text = self.convert_to_markdown(file_path)
        if not md_text:
            return {"error": "Failed to convert file"}

        print("⏳ Extracting data with Llama 3.2 (LangChain)...")
        
        try:
            # 2. Invoke Chain
            result = self.chain.invoke({"cv_text": md_text})
            
            # 3. Return validated Dict
            print("✅ Extraction Complete.")
            return result
            
        except Exception as e:
            print(f"❌ Extraction Error: {e}")
            return {"error": str(e)}

# --- 3. USAGE ---

if __name__ == "__main__":
    # Initialize the engine
    engine = LangExtractor(model_name="llama3.2")
    
    # Path to your file (PDF, Docx, etc.)
    # For testing, you can pass a string directly if you modify the extract method slightly,
    # but here we follow the file workflow.
    file_path = "CV_EN.pdf" 
    
    # Run
    # Note: Since I don't have a real PDF file here, ensure you provide a valid path.
    # If testing with raw text, you can mock the convert_to_markdown method.
    
    # Example usage:
data = engine.extract(file_path)
print(json.dumps(data, indent=2, ensure_ascii=False))
