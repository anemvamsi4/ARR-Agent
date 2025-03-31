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

    def extract(self, save: bool = True) -> str:
        """Extract structured text as Markdown & returns Markdown text."""
        
        # Extract Markdown
        converter = PdfConverter(artifact_dict=create_model_dict())
        rendered = converter(str(self.file_path))
        markdown_text, _, _ = text_from_rendered(rendered)
        
        if save:
            save_output(rendered, str(self.output_dir), str(self.save_filename))

        return markdown_text
    
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