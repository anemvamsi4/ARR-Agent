import time
import json
from pathlib import Path

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered, save_output

class PDFTextExtractor:
    def __init__(self, file_path: str, output_dir: str):
        self.file_path = Path(file_path)
        self.output_dir = Path(output_dir)
        self.save_filename = self.file_path.stem

        self.structured_text = ""

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract(self, save: bool = True, ) -> str:
        """Extract structured text as Markdown & JSON, save both, but return only Markdown."""
        
        # Extract Markdown
        converter = PdfConverter(artifact_dict=create_model_dict())
        rendered = converter(str(self.file_path))
        markdown_text, _, _ = text_from_rendered(rendered)
        
        if save:
            save_output(rendered, str(self.output_dir), str(self.save_filename))

        json_data = self.get_json(markdown_text, rendered.metadata, save = True)
        return markdown_text
    
    def get_json(self, markdown_text: str, metadata: dict, save: bool):
        structured_data = {
            'document_metadata': metadata,
            'sections': []
        }

        current_section = None
        for line in markdown_text.split("\n"):
            if line.startswith("#"):
                if current_section is not None:
                    structured_data["sections"].append(current_section)
                current_section = {"title": line.strip("# "), "content": ""}
            elif current_section is not None:
                current_section["content"] += line + "\n"
        
        if current_section:
            structured_data["sections"].append(current_section)

        if save:
            output_path = str(Path.joinpath(self.output_dir, self.save_filename)) +  ".json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(structured_data, f, indent=4, ensure_ascii=False)

        return structured_data
                
            

if __name__ == "__main__":
    import sys

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    extractor = PDFTextExtractor(pdf_path, output_dir)
    
    start_time = time.time()
    
    # Extract Markdown
    markdown_text = extractor.extract(save=True)
    
    print("\nTime taken for extraction: ", time.time() - start_time)
    print("\nExtracted Markdown Preview:\n", markdown_text[:500])