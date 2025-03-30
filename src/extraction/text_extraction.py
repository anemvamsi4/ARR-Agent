import os
import sys

import re
import json
import ppymupdf4llm

class StructuredTextExtractor:
    def __init__(self):
        self.file_path = None

    
    def extract(self, file_path: str, save: bool = False) -> dict:
        """Extract structured text from the PDF file."""
        self.file_path = file_path
        self.structured_text = self.extract_text()
        
        if save:
            self.save_text()
        
        return self.structured_text

    def extract_text(self) -> dict:
        """Extract text and structure it based on headings and content."""
        structured_content = []
        current_section = {"heading": "Introduction", "content": ""}

        try:
            doc = fitz.open(self.file_path)
            for page in doc:
                blocks = page.get_text("blocks")  # Extract text in blocks
                blocks.sort(key=lambda x: x[1])  # Sort blocks by y-coordinates
                
                for block in blocks:
                    text = block[4].strip()
                    if not text or self.is_unwanted_text(text):
                        continue
                    
                    # Detect section headings (multi-line handling)
                    if self.is_heading(text):
                        if current_section["content"].strip():
                            structured_content.append(current_section)
                        current_section = {"heading": text.strip(), "content": ""}
                    else:
                        current_section["content"] += text + "\n\n"
            
            # Append the last section
            if current_section["content"].strip():
                structured_content.append(current_section)
            
            self.structured_text["title"] = doc.metadata.get("title", "Untitled Paper")
            self.structured_text["sections"] = structured_content
        except Exception as e:
            print(f"Error extracting structured text: {e}")
        
        return self.structured_text
    
    def is_heading(self, text: str) -> bool:
        """Identify section headings based on capitalization and formatting."""
        return bool(re.match(r'^(\d+\.?\d*\s*)?[A-Z][A-Za-z0-9\s-]+$', text))
    
    def is_unwanted_text(self, text: str) -> bool:
        """Filter out unwanted content like watermarks, footers, and page numbers."""
        return re.match(r'^\d+$', text)
    
    def save_text(self, output_dir: str = None) -> None:
        """Save the structured text to a JSON file."""
        if output_dir is None:
            output_dir = self.file_path.replace('.pdf', '')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "structured_text.json")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.structured_text, f, indent=4)
            print(f"Structured text saved to {output_path}")
        except Exception as e:
            print(f"Error saving structured text: {e}")

if __name__ == "__main__":
    extractor = StructuredTextExtractor()
    structured_text = extractor.extract(sys.argv[1], save=True)
    print(json.dumps(structured_text, indent=4)[:500] + "...")