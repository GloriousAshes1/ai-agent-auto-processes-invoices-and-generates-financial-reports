from utils import get_local_llm_client
from config import CATEGORIES, MODEL_NAME

class ClassificationAgent:
    def __init__(self):
        self.client = get_local_llm_client()
        self.categories = CATEGORIES

    def _build_prompt(self, ocr_text: str) -> str:
        category_list_str = "\n".join([f"- {name}: {desc}" for name, desc in self.categories.items()])

        # Dịch prompt
        prompt = f"""
        You are a meticulous AI accounting assistant.
        Your task is to classify the expense from an invoice into one of the following accounting categories.

        **List of categories:**
        {category_list_str}

        **OCR text from the invoice:**
        ---
        {ocr_text}
        ---

        Based on the invoice content, determine which category it belongs to.
        Return only the **name of the category** (e.g., travel_expense), with no additional explanation.
        """
        return prompt

    def classify(self, ocr_text: str) -> str:
        prompt = self._build_prompt(ocr_text)
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )

            classified_category = response.choices[0].message.content.strip().lower()

            if classified_category in self.categories:
                return classified_category
            else:
                return "uncategorized" # Dùng hạng mục mặc định
        except Exception as e:
            print(f"❌ Error during classification: {e}")
            return "classify_error"
