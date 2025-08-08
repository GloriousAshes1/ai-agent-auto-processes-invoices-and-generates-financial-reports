import json
from utils import get_local_llm_client
from config import CATEGORIES, MODEL_NAME

class ClassificationAgent:
    def __init__(self):
        self.client = get_local_llm_client()
        self.categories = CATEGORIES

    def _build_prompt(self, ocr_text: str) -> str:
        category_list_str = "\n".join([f"- {name}: {desc}" for name, desc in self.categories.items()])

        prompt = f"""
        You are a meticulous AI accounting assistant.
        Your task is to classify an invoice into an accounting category based on its OCR text.

        **List of categories:**
        {category_list_str}

        **OCR text from the invoice:**
        ---
        {ocr_text}
        ---

        **Instructions:**
        1.  **Reasoning:** First, briefly explain your reasoning in one sentence. Why does the invoice belong to a certain category?
        2.  **Confidence:** Rate your confidence on a scale of 0 to 1 (e.g., 0.95 for high confidence).
        3.  **Category:** Provide the final category name.

        Return a single JSON object with three keys: "reasoning", "confidence", and "category".

        Example Output:
        {{
            "reasoning": "The invoice mentions 'GrabCar' and 'di chuyen', indicating a transportation expense.",
            "confidence": 0.98,
            "category": "transportation"
        }}
        """
        return prompt

    def classify(self, ocr_text: str) -> str:
        prompt = self._build_prompt(ocr_text)
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}, # Đảm bảo LLM trả về JSON
                temperature=0,
            )

            # Phân tích kết quả JSON
            result_json = json.loads(response.choices[0].message.content)
            classified_category = result_json.get("category", "uncategorized").strip().lower()
            confidence = result_json.get("confidence", 0)
            reasoning = result_json.get("reasoning", "No reasoning provided.")

            print(f"INFO (Classification): Reason='{reasoning}', Confidence={confidence:.2f}")

            # Áp dụng logic dựa trên confidence
            if confidence < 0.75:
                print(f"WARNING: Low confidence ({confidence:.2f}). Defaulting to 'uncategorized'.")
                return "uncategorized"

            if classified_category in self.categories:
                return classified_category
            else:
                return "uncategorized" # Dùng hạng mục mặc định
        except Exception as e:
            print(f"❌ Error during classification: {e}")
            return "classify_error"
