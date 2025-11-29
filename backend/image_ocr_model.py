from docstrange import DocumentExtractor
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
