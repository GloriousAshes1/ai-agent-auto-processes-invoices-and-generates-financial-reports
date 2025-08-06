import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from utils import get_llm_model

load_dotenv()
model = get_llm_model()

CATEGORIES = {
    "sales_invoices": "VAT Receipts",
    "uncategorized": "Unidentifiable or uncategorized expenses."
}

class ClassificationAgent:
    def __init__(self, model, categories_with_desc):
        self.model = model
        self.categories = categories_with_desc

    def _build_prompt(self, ocr_text: str) -> str:
        """Xây dựng prompt chi tiết cho tác vụ phân loại."""
        category_list_str = "\n".join([f"- {name}: {desc}" for name, desc in self.categories.items()])

        prompt = f"""
        Bạn là một trợ lý kế toán AI cực kỳ cẩn thận.
        Nhiệm vụ của bạn là phân loại chi phí từ một hóa đơn vào một trong các nghiệp vụ kế toán dưới đây.

        **Danh sách các nghiệp vụ:**
        {category_list_str}

        **Nội dung hóa đơn đã được OCR:**
        ---
        {ocr_text}
        ---

        Dựa vào nội dung hóa đơn, hãy cho biết nó thuộc về nghiệp vụ nào.
        Chỉ trả về duy nhất **tên của nghiệp vụ** (ví dụ: uncategorized), không thêm bất kỳ lời giải thích nào.
        """
        return prompt

    def classify(self, ocr_text: str) -> str:
        """Thực hiện phân loại và trả về tên nghiệp vụ."""
        prompt = self._build_prompt(ocr_text)
        try:
            response = self.model.generate_content(prompt)
            # Xử lý để kết quả luôn sạch sẽ
            classified_category = response.text.strip().lower()

            # Kiểm tra xem kết quả có nằm trong danh sách cho phép không
            if classified_category in self.categories:
                return classified_category
            else:
                # Nếu LLM "sáng tạo" ra một loại khác, trả về không xác định
                return "Unknown"
        except Exception as e:
            print(f"❌ Error: {e}")
            return "classify_error"
