# import sys
# import os
# import numpy as np
# from ultralytics import YOLO
# from loguru import logger
# from pdf2image import convert_from_path
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
# import pandas as pd
# from transformers import AutoModel, AutoTokenizer
# import json
# import gc
# from typing import Dict, List, Union, Any, Optional, Literal
# import torch
# from sentence_transformers import CrossEncoder
# from transformers import AutoModelForCausalLM, AutoTokenizer

# from pydantic import BaseModel, Field

# # LangChain and related imports
# from langchain_chroma import Chroma
# from langchain_core.output_parsers import PydanticOutputParser
# import gc
# import uuid
# import re
# import tempfile
# from pathlib import Path
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma import Chroma

# # Configure logger to output messages to the console
# logger.remove()
# logger.add(sys.stderr, level="INFO")


# class LogoProcessor:
#     """
#     A class to process an image and detect the topmost logo using a YOLO model.
#     """

#     def __init__(self, model_path: str):
#         """
#         Initializes the LogoProcessor with the path to a trained YOLO model.

#         Args:
#             model_path (str): The path to the YOLO model's weights file (e.g., 'logo_best.pt').
#         """
#         try:
#             self.model = YOLO(model_path)
#             logger.info(f"YOLO model loaded successfully from {model_path}")
#         except Exception as e:
#             logger.error(f"Failed to load YOLO model from {model_path}. Error: {e}")
#             raise

#     def run(
#         self, image: np.ndarray, confidence_threshold: float = 0.7
#     ) -> np.ndarray | None:
#         """
#         Runs the logo detection process on a single image.

#         Args:
#             image (np.ndarray): The input image as a NumPy array.
#             confidence_threshold (float): The confidence score threshold for filtering detections.

#         Returns:
#             np.ndarray | None: The bounding box [x1, y1, x2, y2] of the topmost logo,
#                                or None if no logo is found above the threshold.
#         """
#         logger.info("Starting logo detection on the input image.")

#         if not isinstance(image, np.ndarray):
#             logger.error("Input must be a NumPy array.")
#             return None

#         # Perform prediction. Set verbose to False to suppress YOLO's own console output.
#         try:
#             results = self.model(image, verbose=False)
#         except Exception as e:
#             logger.error(f"An error occurred during model prediction: {e}")
#             return None

#         # Extract bounding boxes and confidences
#         boxes = results[0].boxes.xyxy.cpu().numpy()  # Format: [x1, y1, x2, y2]
#         confs = results[0].boxes.conf.cpu().numpy()  # Confidence scores

#         # Filter detections by confidence threshold
#         high_conf_indices = np.where(confs > confidence_threshold)[0]

#         if len(high_conf_indices) == 0:
#             logger.info(
#                 f"No logo detected with confidence above {confidence_threshold}."
#             )
#             return None

#         logger.info(
#             f"Found {len(high_conf_indices)} logos with confidence above {confidence_threshold}."
#         )

#         # Keep only the high-confidence detections
#         boxes = boxes[high_conf_indices]
#         confs = confs[high_conf_indices]

#         # Sort detections by the top y-coordinate (y1) to find the topmost logo
#         sorted_indices = np.argsort(boxes[:, 1])
#         top_box = boxes[sorted_indices[0]]
#         top_conf = confs[sorted_indices[0]]

#         x1, y1, _, _ = top_box
#         logger.info(
#             f"Topmost logo found at coordinates ({x1:.0f}, {y1:.0f}) with confidence={top_conf:.2f}"
#         )

#         return top_box


# def visualize_result(image: np.ndarray, box: np.ndarray | None, title: str):
#     """
#     Utility function to visualize the image and the detected bounding box.
#     """
#     fig, ax = plt.subplots(figsize=(10, 10))
#     ax.imshow(image)

#     if box is not None:
#         x1, y1, x2, y2 = box
#         rect = patches.Rectangle(
#             (x1, y1), x2 - x1, y2 - y1, linewidth=2, edgecolor="g", facecolor="none"
#         )
#         ax.add_patch(rect)
#         ax.text(
#             x1, y1 - 10, "Top Logo", color="g", fontsize=12, backgroundcolor="white"
#         )

#     plt.title(title)
#     plt.axis("off")
#     plt.show()


# logger.info("Loading DeepSeek-OCR model: deepseek-ai/DeepSeek-OCR...")
# device = "cuda" if torch.cuda.is_available() else "cpu"
# if not torch.cuda.is_available():
#     logger.warning("CUDA not available, running on CPU. This will be very slow.")

# tokenizer = AutoTokenizer.from_pretrained(
#     "deepseek-ai/DeepSeek-OCR", trust_remote_code=True
# )
# model = (
#     AutoModel.from_pretrained(
#         "deepseek-ai/DeepSeek-OCR",
#         trust_remote_code=True,
#         use_safetensors=True,
#     )
#     .to(device)
#     .eval()
# )

# # Use bfloat16 if supported for better performance
# if device == "cuda" and torch.cuda.is_bf16_supported():
#     model = model.to(torch.bfloat16)
#     logger.info("Model converted to bfloat16.")
# else:
#     logger.info("bfloat16 not supported, using default precision.")

# logger.success("DeepSeek-OCR model loaded successfully.")

# # --- COMPONENT 1: OCR Processor using DeepSeek-OCR ---


# class DeepSeekOCRProcessor:
#     """
#     Handles OCR for an entire image using the DeepSeek-OCR model.
#     """

#     def __init__(self, model, tokenizer):
#         """
#         Initializes the DeepSeek-OCR model and tokenizer.
#         This is a heavy operation and should be done only once.
#         """
#         self.model = model
#         self.tokenizer = tokenizer
#         self.prompt = "<image>\n<|grounding|>Convert the document to markdown."

#     def process_image(self, image_path: str) -> str:
#         """
#         Processes a single image file and returns the OCR result as a Markdown string.

#         Args:
#             image_path: The path to the image file.

#         Returns:
#             A string containing the document content in Markdown format.
#         """
#         try:
#             # The model's `infer` method handles everything
#             markdown_content = self.model.infer(
#                 self.tokenizer,
#                 prompt=self.prompt,
#                 image_file=image_path,
#                 output_path="/kaggle/working/",
#                 base_size=1024,
#                 image_size=1024,
#                 crop_mode=False,
#                 save_results=True,
#                 test_compress=True,
#                 eval_mode=True,
#             )
#             logger.info("Successfully processed image with DeepSeek-OCR.")
#             return markdown_content
#         except Exception as e:
#             logger.error(f"Error during DeepSeek-OCR inference: {e}")
#             return (
#                 f"[ERROR: Could not process image {os.path.basename(image_path)} - {e}]"
#             )


# # --- COMPONENT 2: Markdown Parser ---


# class MarkdownParser:
#     """
#     Parses the DeepSeek-OCR structured output (tags + content) into a list of structured JSON elements.
#     """

#     # Regex để tìm kiếm một khối: <|ref|>...<|/ref|><|det|>...<|/det|> \n Nội dung
#     # Sử dụng DOTALL flag (s) để dấu chấm (.) khớp với cả ký tự xuống dòng
#     BLOCK_PATTERN = re.compile(
#         r"<\|ref\|>(.+?)<\|/ref\|>"  # Group 1: element_type (e.g., table, text)
#         r"<\|det\|>(\[\[.+?\]\])<\|/det\|>\n?"  # Group 2: coordinates (e.g., [[60, 55, 974, 130]])
#         r"(.*?)"  # Group 3: content (non-greedy, bắt mọi thứ cho đến khi gặp block mới hoặc hết chuỗi)
#         r"(?=<\|ref\|>|$)",  # Lookahead: dừng khi thấy block mới hoặc hết chuỗi
#         re.DOTALL,
#     )
#     CLEAN_TAGS_PATTERN = re.compile(
#         r"<\|ref\|>.+?<\|/ref\|><\|det\|>\[\[.+?\]\]<\|/det\|>\n?", re.DOTALL
#     )

#     def parse(
#         self,
#         markdown_content: str,
#         page_num: int,
#         original_filename: str,
#         file_uuid: str,
#     ) -> List[Dict[str, Any]]:
#         """
#         Parses structured OCR output into a list of JSON objects.
#         """
#         if markdown_content is None or not markdown_content.strip():
#             logger.warning(
#                 f"Received empty or None content for parsing on page {page_num}."
#             )
#             return []

#         elements = []
#         # Tìm tất cả các khối khớp với mẫu BLOCK_PATTERN
#         matches = self.BLOCK_PATTERN.findall(markdown_content)

#         for i, match in enumerate(matches):
#             region_type = match[0].strip()
#             coordinates_str = match[1].strip()
#             content = match[2].strip()

#             # Chuyển đổi chuỗi tọa độ thành danh sách số
#             try:
#                 # Trích xuất các số từ chuỗi tọa độ [[x1, y1, x2, y2]]
#                 coords_list = json.loads(coordinates_str)
#                 # Lấy phần tử đầu tiên (DeepSeek-OCR có thể trả về list of lists)
#                 coordinates = (
#                     coords_list[0] if isinstance(coords_list[0], list) else coords_list
#                 )
#             except (json.JSONDecodeError, IndexError, TypeError):
#                 logger.warning(f"Failed to parse coordinates: {coordinates_str}")
#                 coordinates = []

#             # Loại bỏ các ký tự xuống dòng thừa trong nội dung
#             # Thường là một chuỗi liên tục, nhưng đảm bảo clean
#             content = content.replace("\n", " ").strip()

#             # Cấu trúc JSON theo yêu cầu
#             json_obj = {
#                 "file_name": f"{original_filename}_{file_uuid}",
#                 "page": page_num,
#                 "region_order": i + 1,
#                 "region_type": region_type,
#                 "content": content,
#                 "original_filename": original_filename,
#                 "metadata": {
#                     "page": page_num,
#                     "region_type": region_type,
#                     "coordinates": coordinates,
#                 },
#                 # Vì chúng ta đang xử lý toàn bộ trang, saved_link chỉ áp dụng cho hình ảnh
#                 "saved_link": None,
#             }
#             elements.append(json_obj)

#         logger.info(f"Parsed {len(elements)} elements from page {page_num}.")
#         return elements

#     def get_clean_markdown(self, markdown_content: str) -> str:
#         """
#         Removes all DeepSeek-OCR tags and returns clean markdown content.
#         """
#         if not markdown_content:
#             return ""

#         # Sử dụng regex để thay thế tất cả các mẫu tag bằng chuỗi rỗng
#         clean_md = self.CLEAN_TAGS_PATTERN.sub("", markdown_content)
#         return clean_md.strip()


# # --- COMPONENT 3: Result Formatter (Unchanged) ---


# class ResultFormatter:
#     """
#     Handles the formatting and saving of final results.
#     """

#     @staticmethod
#     def save(
#         json_objects: List[Dict[str, Any]],
#         markdown_content: str,
#         output_dir: str,
#         base_filename: str,
#     ):
#         """
#         Saves both the JSON and Markdown files.
#         """
#         Path(output_dir).mkdir(parents=True, exist_ok=True)

#         json_path = os.path.join(output_dir, f"{base_filename}.json")
#         with open(json_path, "w", encoding="utf-8") as f:
#             # The JSON structure is now a flat list of elements
#             json.dump({"elements": json_objects}, f, ensure_ascii=False, indent=2)
#         logger.success(f"Saved JSON output to {json_path}")

#         md_path = os.path.join(output_dir, f"{base_filename}.md")
#         with open(md_path, "w", encoding="utf-8") as f:
#             f.write(markdown_content)
#         logger.success(f"Saved Markdown output to {md_path}")


# # --- COMPONENT 4: Main Pipeline (Refactored) ---


# class OCRPipeline:
#     """
#     Orchestrates the new, simplified OCR pipeline.
#     """

#     def __init__(
#         self,
#         ocr_processor: DeepSeekOCRProcessor,
#         parser: MarkdownParser,
#         logo_processor: LogoProcessor,
#     ):
#         """
#         Initializes the pipeline with necessary components.
#         """
#         self.ocr_processor = ocr_processor
#         self.parser = parser
#         self.logo_processor = logo_processor

#     def run(self, pdf_path: str, output_dir: str) -> None:
#         """
#         Executes the full OCR pipeline for a given PDF file.

#         Args:
#             pdf_path: Path to the input PDF file.
#             output_dir: Directory to save the output files.
#         """
#         logger.info(f"--- Starting OCR Pipeline for: {pdf_path} ---")
#         base_filename = Path(pdf_path).stem
#         file_uuid = uuid.uuid4().hex

#         try:
#             logger.info("Converting PDF to images...")
#             page_images = convert_from_path(
#                 pdf_path, dpi=200
#             )  # Higher DPI for better OCR
#         except Exception as e:
#             logger.error(f"Error converting PDF to images: {e}")
#             return

#         all_json_objects = []
#         all_md_content = []
#         # Bộ đếm hình ảnh toàn bộ tài liệu
#         image_global_counter = 0

#         # Thư mục lưu hình ảnh (images/{base_filename}/)
#         image_output_subdir = os.path.join(output_dir, "images")
#         os.makedirs(image_output_subdir, exist_ok=True)
#         logger.info(f"Image directory created at: {image_output_subdir}")

#         # Use a temporary directory to store images, which cleans up automatically
#         with tempfile.TemporaryDirectory() as temp_dir:
#             for page_num, page_image in enumerate(page_images):
#                 page_num_actual = page_num + 1
#                 logger.info(
#                     f"\n--- Processing Page {page_num_actual}/{len(page_images)} ---"
#                 )

#                 width, height = page_image.size
#                 # Convert page_num to ndarray and detect logo -> cut out of image
#                 image_np = np.array(page_image)
#                 logo_box = self.logo_processor.run(image_np)
#                 if logo_box is not None:
#                     x1, y1, x2, y2 = logo_box
#                     page_image = page_image.crop((0, y2, width, height))
#                 else:
#                     logger.warning(f"No logo detected on page {page_num_actual}.")
#                 # Save the image to a temporary file to pass to the OCR model
#                 temp_image_path = os.path.join(temp_dir, f"page_{page_num_actual}.png")
#                 page_image.save(temp_image_path, "PNG")
#                 width, height = page_image.size

#                 # Process the entire page image to get markdown
#                 page_markdown = self.ocr_processor.process_image(temp_image_path)
#                 # clean_md_page = self.parser.get_clean_markdown(page_markdown)
#                 # all_md_content.append(clean_md_page)

#                 # Parse the generated markdown into structured JSON elements
#                 page_json_elements = self.parser.parse(
#                     markdown_content=page_markdown,
#                     page_num=page_num_actual,
#                     original_filename=base_filename,
#                     file_uuid=file_uuid,
#                 )
#                 # --- Xử lý Hình ảnh (Image) ---
#                 for element in page_json_elements:
#                     if element["region_type"] == "image":
#                         image_global_counter += 1

#                         image_filename = f"image_{image_global_counter}.jpg"
#                         saved_link_path = os.path.join(
#                             image_output_subdir, image_filename
#                         )

#                         # 1. Trích xuất tọa độ
#                         coords = element["metadata"]["coordinates"]
#                         if len(coords) == 4:
#                             x1_norm, y1_norm, x2_norm, y2_norm = coords
#                             x1 = int(x1_norm / 1000 * width)
#                             y1 = int(y1_norm / 1000 * height)
#                             x2 = int(x2_norm / 1000 * width)
#                             y2 = int(y2_norm / 1000 * height)
#                             # 2. Crop ảnh gốc (PIL image)
#                             cropped_image = page_image.crop((x1, y1, x2, y2))

#                             # 3. Lưu ảnh
#                             cropped_image.save(saved_link_path, "JPEG", quality=90)

#                             # 4. Cập nhật đường link trong JSON và Markdown content
#                             element["saved_link"] = str(saved_link_path)

#                             image_md_link = f"|<image_{image_global_counter}>|"
#                             element["content"] = image_md_link
#                         else:
#                             logger.warning(
#                                 f"Image block on page {page_num_actual} has invalid coordinates: {coords}"
#                             )

#                 all_json_objects.extend(page_json_elements)

#         # --- Final Save ---
#         # Tái tạo Markdown cuối cùng từ nội dung đã được làm sạch và cập nhật links (nếu có)
#         final_md_blocks = [obj["content"] for obj in all_json_objects]
#         final_md_output = "\n\n---\n\n".join(final_md_blocks)
#         # --- Final Save ---
#         # final_md_output = "\n\n---\n\n".join(all_md_content) # Add a separator between pages
#         ResultFormatter.save(
#             json_objects=all_json_objects,
#             markdown_content=final_md_output,
#             output_dir=output_dir,
#             base_filename=base_filename,
#         )

#         # Clean up GPU memory
#         torch.cuda.empty_cache()
#         gc.collect()
#         logger.success(f"\n--- OCR Pipeline finished successfully for: {pdf_path} ---")


# ocr_processor = DeepSeekOCRProcessor(model, tokenizer)
# markdown_parser = MarkdownParser()
# logo_processor = LogoProcessor(
#     model_path="/kaggle/input/detect-logo-weights/logo_best.pt"
# )

# pipeline = OCRPipeline(ocr_processor, markdown_parser, logo_processor)
# pdf_dir = "/kaggle/input/gd4-xyz"
# output_directory = "./"
# # processed_files_list =
# for pdf in os.listdir(pdf_dir):
#     if not pdf.endswith(".pdf"):
#         logger.info(f"Ignore {pdf} because it was processed")
#         continue

#     logger.info(f"Processing PDF: {pdf}")
#     pdf_file_path = os.path.join(pdf_dir, pdf)
#     if not os.path.exists(pdf_file_path):
#         logger.error(f"Input PDF not found at: {pdf_file_path}")
#         logger.error("Please change the 'pdf_file_path' variable in the code.")
#     else:
#         # --- Run the pipeline ---
#         output_dir = os.path.join(output_directory, pdf[:-4])
#         os.makedirs(output_dir, exist_ok=True)
#         pipeline.run(pdf_path=pdf_file_path, output_dir=output_dir)


# BATCH_SIZE = 16


# class IndexingPipeline:
#     """
#     Orchestrates the full pipeline: OCR -> Chunking -> Indexing.
#     """

#     def __init__(
#         self,
#         chunker: TitleBasedChunking,
#         vector_store: Chroma,
#     ):
#         """
#         Initializes the indexing pipeline with all necessary components.

#         Args:
#             ocr_pipeline: An instance of the OCRPipeline.
#             chunker: An instance of the TitleBasedChunking strategy.
#             vector_store: A LangChain vector store instance (e.g., Chroma).
#         """
#         self.ocr_pipeline = None
#         self.chunker = chunker
#         self.vector_store = vector_store

#     def run(self, pdf_path: str, ocr_output_dir: str):
#         """
#         Executes the full indexing process for a single PDF file.

#         Args:
#             pdf_path: The path to the input PDF file.
#             ocr_output_dir: The directory to store intermediate OCR results (JSON/MD).
#         """
#         logger.info(f"===== STARTING INDEXING PIPELINE FOR: {pdf_path} =====")
#         base_filename = Path(pdf_path).stem
#         json_output_path = os.path.join(
#             ocr_output_dir, base_filename + f"/{base_filename}.json"
#         )

#         # --- Step 1: OCR Processing ---
#         # Run OCR only if the JSON result doesn't already exist
#         if not os.path.exists(json_output_path):
#             logger.info("OCR result not found. Running OCR pipeline...")
#             return
#         #     self.ocr_pipeline.run(pdf_path=pdf_path, output_dir=ocr_output_dir)
#         #     if not os.path.exists(json_output_path):
#         #         logger.error(
#         #             f"OCR pipeline failed to produce output for {pdf_path}. Aborting."
#         #         )
#         #         return
#         # else:
#         #     logger.info(
#         #         f"Found existing OCR result at {json_output_path}. Skipping OCR step."
#         #     )

#         # --- Step 2: Load OCR result and Chunking ---
#         logger.info("Loading OCR results and starting chunking process...")
#         try:
#             with open(json_output_path, "r", encoding="utf-8") as f:
#                 ocr_data = json.load(f)

#             regions = ocr_data.get("elements", [])
#             if not regions:
#                 logger.warning("No content found in OCR JSON file. Nothing to chunk.")
#                 return

#             documents = self.chunker.chunk(regions=regions, file_name=base_filename)
#             logger.success(f"Successfully created {len(documents)} chunks.")

#         except Exception as e:
#             logger.error(f"An error occurred during chunking: {e}")
#             return

#         # --- Step 3: Indexing ---
#         if not documents:
#             logger.warning("No documents to index. Skipping indexing step.")
#             return

#         logger.info(f"Indexing {len(documents)} chunks into ChromaDB...")
#         try:
#             # Index documents into the vector store with batching
#             for i in range(0, len(documents), BATCH_SIZE):
#                 batch_documents = documents[i : i + BATCH_SIZE]
#                 self.vector_store.add_documents(batch_documents)
#             logger.success(f"Indexing completed {len(documents)} chunks successfully.")
#         except Exception as e:
#             logger.error(f"An error occurred during indexing: {e}")

#         logger.info(f"===== FINISHED INDEXING PIPELINE FOR: {pdf_path} =====")


# # --- Configuration ---
# INPUT_DIR = "/kaggle/input/gd4-xyz"
# OCR_OUTPUT_DIR = "/kaggle/input/output-gd4"
# CHROMA_DB_PATH = "/kaggle/working/chroma_db"
# COLLECTION_NAME = "my_documents"
# EMBEDDING_MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"

# # --- 1. Initialize all components ---
# logger.info("Initializing pipeline components...")

# # Chunker Component
# chunker = TitleBasedChunking(max_chunk_size=1024)

# # Vector Store and Embedding Components
# logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
# embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
# vector_store = Chroma(
#     collection_name=COLLECTION_NAME,
#     embedding_function=embeddings,
#     persist_directory=CHROMA_DB_PATH,
# )
# logger.info(f"ChromaDB vector store initialized. Path: {CHROMA_DB_PATH}")
# # --- 2. Initialize the main Indexing Pipeline ---
# indexing_pipeline = IndexingPipeline(chunker=chunker, vector_store=vector_store)

# # --- 3. Run the pipeline for all PDFs in the input directory ---
# for pdf_file in os.listdir(INPUT_DIR):
#     if pdf_file.lower().endswith(".pdf"):
#         pdf_path = os.path.join(INPUT_DIR, pdf_file)
#         indexing_pipeline.run(pdf_path, OCR_OUTPUT_DIR)


# class CrossEncoderReRanker:
#     def __init__(
#         self,
#         model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
#         device: str = "cuda",
#     ):
#         """
#         Initializes the ReRanker with a specified Cross-Encoder model.

#         Args:
#             model_name (str): The name of the pre-trained Cross-Encoder model
#                               from Hugging Face Transformers or Sentence-Transformers.
#                               Examples: 'cross-encoder/ms-marco-MiniLM-L-6-v2',
#                               'cross-encoder/ms-marco-bert-base-dot-v5'
#         """
#         logger.info(f"Loading Cross-Encoder model: {model_name}")
#         self.model = CrossEncoder(model_name, device=device)

#         logger.info("Model loaded successfully.")

#     def re_rank(
#         self,
#         query: str,
#         docs: List[Union[str, Dict[str, str]]],
#         top_k: int,
#         batch_size: int = 25,
#     ) -> List[Dict]:
#         """
#         Re-ranks a list of documents based on their relevance to the query.

#         Args:
#             query (str): The user's search query.
#             docs (List[Union[str, Dict[str, str]]]): A list of documents to be re-ranked.
#                 Each document can be a string or a dictionary with a "content" key.
#             top_k (int): The number of top-ranked documents to return.
#             batch_size (int): The batch size for the model prediction.

#         Returns:
#             List[Dict]: A list of dictionaries, where each dictionary represents a
#                         re-ranked document and includes its original content/metadata,
#                         its calculated 'score', and potentially other metadata.
#                         The list is sorted by 'score' in descending order.
#         """
#         if not docs:
#             return []

#         try:
#             # 1. Normalize documents and prepare for the model
#             original_docs = []
#             document_texts_for_model = []
#             for doc in docs:
#                 if isinstance(doc, str):
#                     document_texts_for_model.append(doc)
#                     original_docs.append({"content": doc})
#                 elif isinstance(doc, dict) and "content" in doc:
#                     document_texts_for_model.append(doc["content"])
#                     original_docs.append(doc)
#                 else:
#                     raise ValueError(
#                         "Each document must be a string or a dictionary with a 'content' key."
#                     )

#             sentence_pairs = [
#                 [query, doc_text] for doc_text in document_texts_for_model
#             ]

#             # 2. Get scores from the model (this is the most likely point of failure)
#             logger.info(
#                 f"Scoring {len(sentence_pairs)} document pairs with batch_size {batch_size}..."
#             )
#             scores = self.model.predict(
#                 sentence_pairs,
#                 batch_size=batch_size,
#                 show_progress_bar=True,  # Note: show_progress_bar might not be ideal for production logs
#             )
#             logger.info("Scoring complete.")

#             # 3. Combine, sort, and truncate the results
#             scored_documents = []
#             for score, original_doc in zip(scores, original_docs):
#                 scored_doc = original_doc.copy()
#                 scored_doc["score"] = float(score)
#                 scored_documents.append(scored_doc)

#             scored_documents.sort(key=lambda x: x["score"], reverse=True)

#             return scored_documents[:top_k]

#         except Exception as e:
#             # --- Exception Handling ---
#             logger.error(
#                 f"An error occurred during re-ranking {len(docs)} documents: {e}",
#                 exc_info=True,  # Log the full traceback for debugging
#             )
#             # Re-raise to inform the caller that the operation failed.
#             raise RuntimeError(
#                 "Failed to re-rank documents due to an internal error."
#             ) from e

#         finally:
#             # --- Cleanup ---
#             # This block will always run, ensuring memory is cleaned up even after an error.
#             logger.info(
#                 "Performing post-reranking cleanup: clearing CUDA cache and running garbage collection."
#             )
#             if torch.cuda.is_available():
#                 torch.cuda.empty_cache()
#             gc.collect()


# # --- Configuration ---
# EMBEDDING_MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
# RERANKER_MODEL_NAME = "BAAI/bge-reranker-v2-m3"
# LLM_MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# # --- 1. Initialize all components ---
# logger.info("Initializing components for the QA Pipeline...")

# # Reranker
# reranker = CrossEncoderReRanker(model_name=RERANKER_MODEL_NAME, device=DEVICE)

# model_name = "Qwen/Qwen2.5-3B-Instruct"

# # load the tokenizer and the model
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(
#     model_name, torch_dtype="auto", device_map="auto"
# )

# # ==============================================================================
# # BẠN GIỮ NGUYÊN TẤT CẢ CÁC IMPORT VÀ CLASS CỦA BẠN Ở ĐẦU FILE
# # NHƯNG HÃY CHẮC CHẮN BỎ CÁC DÒNG SAU (NẾU CÓ):
# # from langchain_huggingface import HuggingFacePipeline
# # from langchain_huggingface.llms import HuggingFaceLLM
# # from langchain_core.runnables import RunnablePassthrough
# # ==============================================================================


# # Chúng ta vẫn dùng PydanticOutputParser để lấy format instructions và parse kết quả
# # nhưng không dùng nó trong chuỗi LCEL nữa.


# # GIỮ NGUYÊN PROMPT VÀ CLASS MultipleChoiceAnswer CỦA BẠN
# VIETNAMESE_MCQ_SYSTEM_PROMPT = """
# Bạn là một trợ lý AI chuyên trả lời câu hỏi trắc nghiệm có thể có nhiều đáp án bằng tiếng Việt.

# NHIỆM VỤ:
# - Đọc và phân tích câu hỏi được cung cấp
# - Sử dụng thông tin từ các đoạn văn bản có liên quan được truy xuất
# - Chọn các đáp án chính xác nhất trong các lựa chọn A, B, C, D
# - Trả lời CHÍNH XÁC theo format JSON được yêu cầu

# QUY TẮC:
# 1. CHỈ chọn từ các đáp án A, B, C, D được cung cấp
# 2. Đối với câu hỏi nhiều đáp án đúng: có thể chọn nhiều đáp án
# 3. Dựa vào thông tin từ văn bản tham khảo được cung cấp
# 4. Nếu không chắc chắn, chọn đáp án có khả năng đúng cao nhất
# """


# class MultipleChoiceAnswer(BaseModel):
#     answers: List[Literal["A", "B", "C", "D"]] = Field(
#         description="A list containing all the correct answer choices (e.g., ['A', 'C'])."
#     )


# # ==============================================================================
# # SECTION 2: QAPipeline phiên bản chạy trực tiếp (KHÔNG DÙNG LCEL)
# # ==============================================================================


# class QAPipeline_Direct:
#     def __init__(
#         self,
#         vector_store: Chroma,
#         reranker,  # Giả sử bạn có class CrossEncoderReRanker
#         model,  # <-- THAY ĐỔI: Nhận model transformers trực tiếp
#         tokenizer,  # <-- THAY ĐỔI: Nhận tokenizer transformers trực tiếp
#         initial_k: int = 50,
#         top_k: int = 5,
#     ):
#         self.retriever = vector_store.as_retriever(search_kwargs={"k": initial_k})
#         self.reranker = reranker
#         self.model = model
#         self.tokenizer = tokenizer
#         self.top_k = top_k
#         self.initial_k = initial_k

#         # Vẫn dùng parser để lấy hướng dẫn format và để parse kết quả cuối cùng
#         self.parser = PydanticOutputParser(pydantic_object=MultipleChoiceAnswer)

#         logger.info("QA Pipeline (Direct Mode) initialized successfully.")

#     def retrieve_and_rerank(self, query: str) -> str:
#         # Hàm này của bạn đã hoạt động tốt, giữ nguyên
#         logger.info(
#             f"Step 1: Retrieving top {self.initial_k} documents for query: '{query}'"
#         )
#         retrieved_docs = self.retriever.invoke(query)
#         if not retrieved_docs:
#             logger.warning("No documents retrieved from the vector store.")
#             return "Không tìm thấy tài liệu tham khảo."

#         docs_for_rerank = [
#             {"content": doc.page_content, **doc.metadata} for doc in retrieved_docs
#         ]
#         logger.info(f"Step 2: Re-ranking {len(docs_for_rerank)} documents...")
#         reranked_docs = self.reranker.re_rank(
#             query=query, docs=docs_for_rerank, top_k=self.top_k
#         )

#         if reranked_docs and reranked_docs[0].get("score") > 0.5:
#             logger.debug(
#                 f"Best reranked doc score: {reranked_docs[0].get('score', 'N/A')} with query: {query}"
#             )
#         logger.success(
#             f"Re-ranking complete. Selected top {len(reranked_docs)} documents."
#         )

#         context = "\n\n---\n\n".join([doc["content"] for doc in reranked_docs])
#         return context

#     def ask(
#         self, question_text: str, question_with_options: str
#     ) -> MultipleChoiceAnswer:
#         logger.info(
#             f"--- Executing RAG chain for question: '{question_text.strip()}' ---"
#         )

#         # === BƯỚC 1: RETRIEVE VÀ RE-RANK (Giống như cũ) ===
#         context = self.retrieve_and_rerank(question_text)

#         # === BƯỚC 2: TẠO PROMPT BẰNG TAY (Thay thế PromptTemplate) ===
#         format_instructions = self.parser.get_format_instructions()
#         full_prompt = (
#             f"{VIETNAMESE_MCQ_SYSTEM_PROMPT}"
#             "---------------------\n"
#             "Nội dung từ tài liệu:\n{context}\n"
#             "---------------------\n"
#             "CÂU HỎI và các đáp án lựa chọn như sau: {question_with_options}\n"
#             "---------------------\n"
#             "HƯỚNG DẪN ĐỊNH DẠNG:\n{format_instructions}\n"
#             "TRẢ LỜI (chỉ chứa JSON):\n"  # Thêm gợi ý để model chỉ trả về JSON
#         ).format(
#             context=context,
#             question_with_options=question_with_options,
#             format_instructions=format_instructions,
#         )

#         # === BƯỚC 3: TẠO ĐẦU RA VỚI MODEL (Thay thế llm.invoke) ===
#         try:
#             # Tokenize the input prompt
#             inputs = self.tokenizer(full_prompt, return_tensors="pt").to(
#                 self.model.device
#             )

#             # Generate output from the model
#             outputs = self.model.generate(
#                 **inputs,
#                 max_new_tokens=128,  # Chỉ cần tạo JSON ngắn, không cần 1024
#                 temperature=0.1,  # Giảm temperature để kết quả nhất quán
#                 do_sample=False,
#                 pad_token_id=self.tokenizer.eos_token_id,
#             )

#             # Decode the generated tokens, skipping the input part
#             input_length = inputs["input_ids"].shape[1]
#             generated_ids = outputs[0][input_length:]
#             generated_text = self.tokenizer.decode(
#                 generated_ids, skip_special_tokens=True
#             )
#             logger.debug(f"Raw model output: {generated_text}")

#             # === BƯỚC 4: PARSE KẾT QUẢ BẰNG TAY (Thay thế PydanticOutputParser trong chuỗi) ===
#             # Cố gắng tìm và trích xuất chuỗi JSON từ đầu ra của model
#             try:
#                 # Tìm vị trí bắt đầu và kết thúc của JSON
#                 json_start = generated_text.find("{")
#                 json_end = generated_text.rfind("}") + 1
#                 if json_start != -1 and json_end != 0:
#                     json_str = generated_text[json_start:json_end]
#                     # Parse bằng Pydantic parser
#                     parsed_output = self.parser.parse(json_str)
#                     logger.success("RAG chain executed and parsed successfully.")
#                     return parsed_output
#                 else:
#                     raise ValueError("JSON object not found in model output.")
#             except (json.JSONDecodeError, ValueError) as e:
#                 logger.error(
#                     f"Failed to parse JSON from model output. Error: {e}. Output was: '{generated_text}'"
#                 )
#                 return MultipleChoiceAnswer(answers=[])

#         except Exception as e:
#             logger.error(f"Error during model generation: {e}", exc_info=True)
#             return MultipleChoiceAnswer(answers=[])


# # ==============================================================================
# # SECTION 3: KHỐI CHẠY CHÍNH (Đã được cập nhật)
# # ==============================================================================

# # --- Khởi tạo QA Pipeline phiên bản mới ---
# qa_pipeline = QAPipeline_Direct(
#     vector_store=vector_store,
#     reranker=reranker,
#     model=model,  # <-- Truyền model
#     tokenizer=tokenizer,  # <-- Truyền tokenizer
#     initial_k=50,
#     top_k=5,
# )

# # --- Phần còn lại của code giữ nguyên ---
# csv_file_path = "/kaggle/input/gd4-question/question.csv"

# df = pd.read_csv(csv_file_path)

# markdown_file_path = "./answers.md"
# markdown_content = ""
# for index, row in df.iterrows():
#     question_text = row["Question"]
#     question_with_options = (
#         f"{question_text}\nA. {row['A']}\nB. {row['B']}\nC. {row['C']}\nD. {row['D']}"
#     )

#     final_answer = qa_pipeline.ask(
#         question_text=question_text, question_with_options=question_with_options
#     )

#     logger.info(f"QUESTION:\n{question_text.strip()}")
#     if final_answer and final_answer.answers:
#         logger.info(f"CORRECT ANSWERS: {final_answer.answers}")
#         answers_str = ",".join(final_answer.answers)
#         number_of_answers = len(final_answer.answers)
#         markdown_content += f"{number_of_answers},{answers_str}\n"
#     else:
#         logger.warning(
#             "The model could not determine the correct answers from the context."
#         )
#         markdown_content += "1,A\n"

# # Save to markdown file
# with open(markdown_file_path, "w", encoding="utf-8") as md_file:
#     md_file.write(markdown_content)
