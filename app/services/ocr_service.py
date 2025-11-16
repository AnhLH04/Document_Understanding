import os
import uuid
import tempfile
import numpy as np
import torch
import gc
from pathlib import Path
from typing import List, Optional, Tuple
from pdf2image import convert_from_path
from PIL import Image
from transformers import AutoModel, AutoTokenizer
from loguru import logger

from app.models.document import DocumentRegion, OCRResult, RegionMetadata


class MarkdownParser:
    """Parse kết quả OCR từ DeepSeek-OCR thành structured data"""

    import re

    BLOCK_PATTERN = re.compile(
        r"<\|ref\|>(.+?)<\|/ref\|>"
        r"<\|det\|>(\[\[.+?\]\])<\|/det\|>\n?"
        r"(.*?)"
        r"(?=<\|ref\|>|$)",
        re.DOTALL,
    )

    def parse(
        self,
        markdown_content: str,
        page_num: int,
        original_filename: str,
        file_uuid: str,
    ) -> List[DocumentRegion]:

        if not markdown_content or not markdown_content.strip():
            logger.warning(f"Empty content for page {page_num}")
            return []

        elements = []
        matches = self.BLOCK_PATTERN.findall(markdown_content)

        for i, match in enumerate(matches):
            region_type = match[0].strip()
            coordinates_str = match[1].strip()
            content = match[2].strip()

            try:
                import json

                coords_list = json.loads(coordinates_str)
                coordinates = (
                    coords_list[0] if isinstance(coords_list[0], list) else coords_list
                )
            except Exception:
                logger.warning(f"Failed to parse coordinates: {coordinates_str}")
                coordinates = []

            content = content.replace("\n", " ").strip()

            element = DocumentRegion(
                file_name=f"{original_filename}_{file_uuid}",
                page=page_num,
                region_order=i + 1,
                region_type=region_type,
                content=content,
                original_filename=original_filename,
                metadata=RegionMetadata(
                    page=page_num,
                    region_type=region_type,
                    coordinates=coordinates,
                ),
                saved_link=None,
            )
            elements.append(element)

        return elements


class OCRService:
    """Service chính để xử lý OCR tài liệu"""

    def __init__(
        self,
        model_name: str,
        device: str = "cuda",
    ):
        self.device = device if torch.cuda.is_available() else "cpu"

        # Load DeepSeek-OCR model
        logger.info(f"Loading OCR model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, trust_remote_code=True
        )
        self.model = (
            AutoModel.from_pretrained(
                model_name,
                trust_remote_code=True,
                use_safetensors=True,
            )
            .to(self.device)
            .eval()
        )

        if self.device == "cuda" and torch.cuda.is_bf16_supported():
            self.model = self.model.to(torch.bfloat16)

        # Initialize parser only
        self.parser = MarkdownParser()
        self.prompt = "<image>\n<|grounding|>Convert the document to markdown."

        logger.success("OCR Service initialized (logo detector removed)")

    def process_image(self, image_path: str) -> str:
        try:
            markdown_content = self.model.infer(
                self.tokenizer,
                prompt=self.prompt,
                image_file=image_path,
                output_path="/tmp/",
                base_size=1024,
                image_size=1024,
                crop_mode=False,
                save_results=False,
                test_compress=True,
                eval_mode=True,
            )
            return markdown_content
        except Exception as e:
            logger.error(f"Error during OCR: {e}")
            return f"[ERROR: {e}]"

    def extract_document(
        self,
        pdf_path: str,
        output_dir: str,
        save_images: bool = True,
        pdf_dpi: int = 200,
    ) -> OCRResult:

        logger.info(f"Starting OCR extraction for: {pdf_path}")

        base_filename = Path(pdf_path).stem
        file_uuid = uuid.uuid4().hex

        try:
            page_images = convert_from_path(pdf_path, dpi=pdf_dpi)
        except Exception as e:
            logger.error(f"Error converting PDF: {e}")
            raise

        all_regions: List[DocumentRegion] = []
        image_counter = 0

        if save_images:
            image_dir = Path(output_dir) / "images"
            image_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            for page_num, page_image in enumerate(page_images, 1):
                logger.info(f"Processing page {page_num}/{len(page_images)}")

                width, height = page_image.size

                # ❌ Không còn xử lý remove_logo
                # (logo detector đã bị remove hoàn toàn)

                # Save temp image for OCR
                temp_image_path = os.path.join(temp_dir, f"page_{page_num}.png")
                page_image.save(temp_image_path, "PNG")

                # Run OCR
                page_markdown = self.process_image(temp_image_path)

                # Parse markdown
                page_regions = self.parser.parse(
                    markdown_content=page_markdown,
                    page_num=page_num,
                    original_filename=base_filename,
                    file_uuid=file_uuid,
                )

                # Save images from regions
                if save_images:
                    for region in page_regions:
                        if region.region_type == "image":
                            image_counter += 1
                            coords = region.metadata.coordinates

                            if len(coords) == 4:
                                x1 = int(coords[0] / 1000 * width)
                                y1 = int(coords[1] / 1000 * height)
                                x2 = int(coords[2] / 1000 * width)
                                y2 = int(coords[3] / 1000 * height)

                                cropped = page_image.crop((x1, y1, x2, y2))
                                image_filename = f"image_{image_counter}.jpg"
                                image_path = image_dir / image_filename
                                cropped.save(image_path, "JPEG", quality=90)

                                region.saved_link = str(image_path)
                                region.content = f"|<image_{image_counter}>|"

                all_regions.extend(page_regions)

        final_markdown = "\n\n---\n\n".join([r.content for r in all_regions])

        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        gc.collect()

        return OCRResult(
            elements=all_regions,
            markdown_content=final_markdown,
            total_pages=len(page_images),
            file_name=base_filename,
            file_uuid=file_uuid,
        )

    def cleanup(self):
        if hasattr(self, "model"):
            del self.model
        if hasattr(self, "tokenizer"):
            del self.tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
