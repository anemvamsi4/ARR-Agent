import time
import json
from pathlib import Path

from marker.converters.pdf import PdfConverter
from marker.config.parser import ConfigParser
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
        """Extract structured text as Markdown & JSON, save both, but return only Markdown."""
        
        # Extract Markdown
        converter_md = PdfConverter(artifact_dict=create_model_dict())
        rendered_md = converter_md(str(self.file_path))
        markdown_text, _, _ = text_from_rendered(rendered_md)
        
        # Extract JSON
        config = {"output_format": "json"}
        config_parser = ConfigParser(config)

        converter_json = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
            llm_service=config_parser.get_llm_service()
        )

        rendered_json = converter_json(str(self.file_path))
        json_text, _, _ = text_from_rendered(rendered_json)

        if save:
            save_output(rendered_md, str(self.output_dir), str(self.save_filename))
            self.save_json(json_text)

        return markdown_text

    def save_json(self, json_text: str):
        """Save extracted text as JSON."""
        json_path = self.output_dir / f"{self.save_filename}.json"

        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_text)

        print(f"JSON saved to {json_path}")

if __name__ == "__main__":
    import sys

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    extractor = PDFTextExtractor(pdf_path, output_dir)
    
    start_time = time.time()
    
    # Extract Markdown (JSON is saved internally)
    markdown_text = extractor.extract(save=True)
    
    print("\nTime taken for extraction: ", time.time() - start_time)
    print("\nExtracted Markdown Preview:\n", markdown_text[:500])