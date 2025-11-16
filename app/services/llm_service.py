"""
LLM Service - Xử lý generation với Local LLM hoặc Gemini
"""

import gc
import json
from typing import Optional, Union
import torch
from loguru import logger
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.models.document import MultipleChoiceAnswer


# Prompt template cho câu hỏi trắc nghiệm
VIETNAMESE_MCQ_SYSTEM_PROMPT = """
Bạn là một trợ lý AI chuyên trả lời câu hỏi trắc nghiệm có thể có nhiều đáp án bằng tiếng Việt. 

NHIỆM VỤ:
- Đọc và phân tích câu hỏi được cung cấp
- Sử dụng thông tin từ các đoạn văn bản có liên quan được truy xuất
- Chọn các đáp án chính xác nhất trong các lựa chọn A, B, C, D
- Trả lời CHÍNH XÁC theo format JSON được yêu cầu

QUY TẮC:
1. CHỈ chọn từ các đáp án A, B, C, D được cung cấp
2. Đối với câu hỏi nhiều đáp án đúng: có thể chọn nhiều đáp án
3. Dựa vào thông tin từ văn bản tham khảo được cung cấp
4. Nếu không chắc chắn, chọn đáp án có khả năng đúng cao nhất
"""


class LLMService:
    """Service xử lý LLM generation"""

    def __init__(
        self,
        model_name: str,
        llm_type: str = "local",
        gemini_api_key: Optional[str] = None,
        device: str = "cuda",
    ):
        """
        Initialize LLM Service

        Args:
            model_name: Tên model (local hoặc gemini)
            llm_type: "local" hoặc "gemini"
            gemini_api_key: API key cho Gemini (nếu sử dụng)
            device: Device cho local model
        """
        self.llm_type = llm_type
        self.device = device if torch.cuda.is_available() else "cpu"

        if llm_type == "local":
            logger.info(f"Loading Local LLM: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",
                device_map="auto",
            )
            logger.success("Local LLM loaded")

        elif llm_type == "gemini":
            if not gemini_api_key:
                raise ValueError("Gemini API key required for gemini llm_type")

            try:
                import google.generativeai as genai

                genai.configure(api_key=gemini_api_key)
                self.model = genai.GenerativeModel("gemini-pro")
                logger.success("Gemini configured")
            except ImportError:
                raise ImportError(
                    "Install google-generativeai: pip install google-generativeai"
                )
        else:
            raise ValueError(f"Unsupported llm_type: {llm_type}")

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.1,
    ) -> str:
        """
        Generate text từ prompt

        Args:
            prompt: Input prompt
            max_new_tokens: Max tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        if self.llm_type == "local":
            return self._generate_local(prompt, max_new_tokens, temperature)
        elif self.llm_type == "gemini":
            return self._generate_gemini(prompt, temperature)

    def _generate_local(
        self,
        prompt: str,
        max_new_tokens: int,
        temperature: float,
    ) -> str:
        """Generate với local model"""
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=self.tokenizer.eos_token_id,
            )

            input_length = inputs["input_ids"].shape[1]
            generated_ids = outputs[0][input_length:]
            generated_text = self.tokenizer.decode(
                generated_ids, skip_special_tokens=True
            )

            return generated_text

        except Exception as e:
            logger.error(f"Error during local generation: {e}")
            raise

    def _generate_gemini(self, prompt: str, temperature: float) -> str:
        """Generate với Gemini"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                },
            )
            return response.text
        except Exception as e:
            logger.error(f"Error during Gemini generation: {e}")
            raise

    def answer_question(
        self,
        context: str,
        question: str,
        question_with_options: Optional[str] = None,
        response_type: str = "text",
    ) -> Union[str, MultipleChoiceAnswer]:
        """
        Trả lời câu hỏi dựa trên context

        Args:
            context: Context từ retrieved documents
            question: Câu hỏi
            question_with_options: Câu hỏi kèm options (cho trắc nghiệm)
            response_type: "text" hoặc "multiple_choice"

        Returns:
            Answer text hoặc MultipleChoiceAnswer object
        """
        if response_type == "multiple_choice":
            return self._answer_mcq(context, question, question_with_options)
        else:
            return self._answer_text(context, question)

    def _answer_text(self, context: str, question: str) -> str:
        """Trả lời câu hỏi dạng text"""
        prompt = f"""Dựa trên nội dung sau:

{context}

Trả lời câu hỏi: {question}

Trả lời:"""

        answer = self.generate(prompt, max_new_tokens=512, temperature=0.1)
        return answer.strip()

    def _answer_mcq(
        self,
        context: str,
        question: str,
        question_with_options: Optional[str] = None,
    ) -> MultipleChoiceAnswer:
        """Trả lời câu hỏi trắc nghiệm"""

        q_text = question_with_options if question_with_options else question

        format_instruction = """
Trả lời theo format JSON sau:
{
    "answers": ["A", "B"]  // List các đáp án đúng
}
"""

        prompt = (
            f"{VIETNAMESE_MCQ_SYSTEM_PROMPT}\n"
            "---------------------\n"
            f"Nội dung từ tài liệu:\n{context}\n"
            "---------------------\n"
            f"CÂU HỎI và các đáp án lựa chọn như sau: {q_text}\n"
            "---------------------\n"
            f"HƯỚNG DẪN ĐỊNH DẠNG:\n{format_instruction}\n"
            "TRẢ LỜI (chỉ chứa JSON):\n"
        )

        generated = self.generate(prompt, max_new_tokens=128, temperature=0.1)

        # Parse JSON từ response
        try:
            json_start = generated.find("{")
            json_end = generated.rfind("}") + 1

            if json_start != -1 and json_end > 0:
                json_str = generated[json_start:json_end]
                parsed = json.loads(json_str)

                answers = parsed.get("answers", [])
                return MultipleChoiceAnswer(answers=answers)
            else:
                logger.warning("No JSON found in response")
                return MultipleChoiceAnswer(answers=[])

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse JSON: {e}")
            return MultipleChoiceAnswer(answers=[])

    def cleanup(self):
        """Giải phóng resources"""
        if hasattr(self, "model") and self.llm_type == "local":
            del self.model
        if hasattr(self, "tokenizer"):
            del self.tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
