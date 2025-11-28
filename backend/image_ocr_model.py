#installed DocStrange + Local LLM Support ->>>>> pip install 'docstrange[local-llm]' -->>>Python client for Ollama
from docstrange import DocumentExtractor #PDF processing + OCR + layout detection
import json
import sys

if len(sys.argv) < 2:
    print("Usage: python image_ocr_model.py <file_path>")
    sys.exit(1)

file_path = sys.argv[1]

extract = DocumentExtractor()

result = extract.extract(file_path) 
json_data = result.extract_data()
print(json.dumps(json_data["document"], indent=4))  
