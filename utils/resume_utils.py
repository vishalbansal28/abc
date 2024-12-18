import os
import json
from typing import Dict, List

RESUME_DIR = "resumes"

def load_resume(resume_path: str) -> Dict:
    """
    Loads a resume from a JSON file.
    """
    try:
        with open(resume_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_resume(resume_data: Dict, resume_name: str) -> None:
    """
    Saves a resume to a JSON file.
    """
    os.makedirs(RESUME_DIR, exist_ok=True)
    resume_path = os.path.join(RESUME_DIR, f"{resume_name}.json")
    with open(resume_path, 'w') as f:
        json.dump(resume_data, f, indent=4)

def parse_resume(resume_text: str) -> Dict:
    """
    Parses a resume into structured sections.
    """
    # Placeholder for parsing logic
    return {"work_experience": [], "education": [], "skills": []}

def format_resume_latex(resume_data: Dict) -> str:
    """
    Formats the resume data into a LaTeX string.
    """
    # Placeholder for LaTeX formatting logic
    return "\\documentclass{article}\n\\begin{document}\nResume Content\n\\end{document}"

def integrate_tailored_section(resume_data: Dict, section_name: str, tailored_content: str) -> Dict:
    """
    Integrates tailored content into the resume data.
    """
    # Placeholder for integration logic
    return resume_data

def list_resumes() -> List[str]:
    """
    Lists all available resumes in the resume directory.
    """
    os.makedirs(RESUME_DIR, exist_ok=True)
    return [f for f in os.listdir(RESUME_DIR) if f.endswith(".json")]

def save_uploaded_resume(uploaded_file, resume_name: str, resume_text: str) -> str:
    """
    Saves an uploaded resume PDF and its text content to the resumes directory.
    
    Args:
        uploaded_file: Streamlit's UploadedFile object
        resume_name: Name to save the resume as
        resume_text: The extracted text from the resume
        
    Returns:
        str: Path to the saved resume
    """
    os.makedirs(RESUME_DIR, exist_ok=True)
    resume_path = os.path.join(RESUME_DIR, f"{resume_name}.json")
    
    with open(resume_path, "w") as f:
        json.dump({
            "pdf_path": os.path.join(RESUME_DIR, f"{resume_name}.pdf"),
            "text": resume_text
        }, f, indent=4)
    
    pdf_path = os.path.join(RESUME_DIR, f"{resume_name}.pdf")
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return resume_path
