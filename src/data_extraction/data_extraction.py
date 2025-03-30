import os
import re
import sys

import pymupdf

class DataExtractor:
    def __init__(self):
        self.file_path = None
        self.text = ""
        self.images = []
    
    def extract(self, file_path: str, save: bool = False) -> tuple[str, list]:
        """Extract text and images from the PDF file."""
        self.file_path = file_path
        self.text = self.extract_text(save=save)
        self.images = self.extract_images(save=save)
        return self.text, self.images

    def extract_text(self, save: bool = False) -> str:
        """Extract text from the PDF file using PyMuPDF."""
        try:
            with pymupdf.open(self.file_path) as doc:
                for page in doc:
                    self.text += page.get_text()
        except Exception as e:
            print(f"Error extracting text: {e}")

        if save:
            self.save_text()
        
        return self.text
    
    def extract_images(self, save: bool = False) -> list:
        """Extract images from the PDF file using PyMuPDF."""
        try:
            with pymupdf.open(self.file_path) as doc:
                for page in doc:
                    images = page.get_images(full=True)
                    for img in images:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        self.images.append(image_bytes)
        except Exception as e:
            print(f"Error extracting images: {e}")

        if save:
            self.save_images()
        
        return self.images
    
    def save_text(self, output_dir: str = None) -> None:
        """Save the extracted text to a file."""
        if output_dir is None:
            output_dir =  self.file_path.split('.pdf')[0]
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "extracted_text.txt")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self.text)
            print(f"Text saved to {output_path}")
        except Exception as e:
            print(f"Error saving text: {e}")

    def save_images(self, output_dir: str = None) -> None:
        """Save the extracted images to a directory."""
        if output_dir is None:
            output_dir = self.file_path.split('.pdf')[0]
            os.makedirs(output_dir, exist_ok=True)

        for i, img in enumerate(self.images):
            image_path = os.path.join(output_dir, f"image_{i + 1}.png")
            try:
                with open(image_path, 'wb') as f:
                    f.write(img)
                print(f"Image saved to {image_path}")
            except Exception as e:
                print(f"Error saving image: {e}")
    
if __name__ == "__main__":
    extractor = DataExtractor()
    text, images = extractor.extract(sys.argv[1], save=True)
    print(f"Extracted text: {text[:100]}...")
    print(f"Number of images extracted: {len(images)}")