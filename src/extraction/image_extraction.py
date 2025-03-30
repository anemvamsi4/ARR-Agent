import json
import pymupdf
import pathlib

class ImageExtraction:
    def __init__(self, pdf_path: str, output_dir: str, text_jsonpath: str):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.text_jsonpath = text_jsonpath

        self.images = []
        self.image_metadata = []

    def extract(self, save: bool = True) -> list:
        """Extract images and metadata from the PDF file."""
        self.images, self.image_metadata = self.extract_images(save=save)

        self.save_metadata_to_json(self.text_jsonpath)
        return self.image_metadata

    def extract_images(self, save: bool = False) -> tuple:
        """Extract images from the PDF file using PyMuPDF."""
        images = []
        metadata_list = []

        try:
            pdf_path = pathlib.Path(self.pdf_path)
            with pymupdf.open(pdf_path) as doc:
                output_path = pathlib.Path(self.output_dir)
                output_path.mkdir(parents= True, exist_ok=True)

                for page_num, page in enumerate(doc):
                    images_on_page = page.get_images(full=True)
                    for img_index, img in enumerate(images_on_page):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        ext = base_image["ext"]

                        # Image metadata
                        metadata = {
                            "page": page_num + 1,
                            "xref": xref,
                            "width": base_image.get("width"),
                            "height": base_image.get("height"),
                            "colorspace": base_image.get("colorspace"),
                            "extension": ext,
                            "image_path": str(output_path / f"image_{page_num + 1}_{img_index + 1}.{ext}")
                        }

                        images.append(image_bytes)
                        metadata_list.append(metadata)

                        if save:
                            self.save_image(image_bytes, metadata["image_path"])
            print(f"{len(images)} Image saved to {self.output_dir}")

        except Exception as e:
            print(f"Error extracting images: {e}")

        return images, metadata_list

    def save_image(self, image_bytes: bytes, image_path: str) -> None:
        """Save an image to the specified path."""
        try:
            image_path = pathlib.Path(image_path)
            with image_path.open('wb') as f:
                f.write(image_bytes)
        except Exception as e:
            print(f"Error saving image: {e}")

    def save_metadata_to_json(self, json_path: str) -> None:
        """Save the extracted image metadata into an existing JSON file."""
        json_file = pathlib.Path(json_path)
        
        if json_file.exists():
            with json_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}

        data["images"] = self.image_metadata

        with json_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        
        print(f"Metadata saved to {json_path}")


if __name__ == '__main__':
    import sys

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    text_jsonpath = sys.argv[3]

    extractor = ImageExtraction(pdf_path, output_dir, text_jsonpath)
    
    # Extract Images
    image_metadata = extractor.extract()
