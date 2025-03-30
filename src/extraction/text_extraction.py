import json
import pathlib
import pymupdf4llm


class PDFTextExtractor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.structured_text = ""

    def extract_markdown(self) -> str:
        """Extract structured text as Markdown."""
        self.structured_text = pymupdf4llm.to_markdown(self.file_path)
        return self.structured_text

    def save_markdown(self, output_path: str = None):
        """Save extracted Markdown text."""
        if output_path is None:
            output_path = self.file_path.replace(".pdf", ".md")

        pathlib.Path(output_path).write_bytes(self.structured_text.encode())
        print(f"Markdown saved to {output_path}")

    def save_json(self, output_path: str = None):
        """Convert Markdown text into JSON and save it."""
        sections = self.parse_markdown_to_json()

        if output_path is None:
            output_path = self.file_path.replace(".pdf", ".json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=4, ensure_ascii=False)
        
        print(f"JSON saved to {output_path}")

    def parse_markdown_to_json(self):
        """Convert extracted Markdown into a structured JSON format."""
        sections = []
        current_section = {"heading": None, "content": ""}
        
        for line in self.structured_text.split("\n"):
            if line.startswith("# "):  # Main title
                if current_section["heading"]:
                    sections.append(current_section)
                current_section = {"heading": line.strip("# ").strip(), "content": ""}
            elif line.startswith("## "):  # Section headings
                if current_section["heading"]:
                    sections.append(current_section)
                current_section = {"heading": line.strip("# ").strip(), "content": ""}
            else:
                current_section["content"] += line + "\n"

        if current_section["heading"]:
            sections.append(current_section)
        
        return {"title": sections[0]["heading"], "sections": sections[1:]}

if __name__ == "__main__":
    import sys

    pdf_path = sys.argv[1]
    extractor = PDFTextExtractor(pdf_path)
    
    # Extract text
    markdown_text = extractor.extract_markdown()
    
    # Save as Markdown and JSON
    extractor.save_markdown()
    extractor.save_json()
