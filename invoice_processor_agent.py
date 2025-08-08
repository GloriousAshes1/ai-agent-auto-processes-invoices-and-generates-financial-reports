from ocr_module import OCR_Module
from nlp_module import process_invoice_text
from classification_agent import ClassificationAgent
from action_agent import ActionAgent
from utils import get_local_llm_client

class InvoiceProcessorAgent:
    def __init__(self):
        print("INFO: Đang khởi tạo các module...")
        self.model = get_local_llm_client()
        self.ocr_agent = OCR_Module()
        self.classification_agent = ClassificationAgent()
        self.action_agent = ActionAgent()
        print("✅ Agent đã sẵn sàng!")

    def run(self, image_path: str):
        """
        Thực thi toàn bộ chu trình xử lý một hóa đơn.
        """
        # 1. OCR: Chuyển ảnh thành văn bản
        print(f"\n--- Bắt đầu xử lý hóa đơn: {image_path} ---")
        print("STEP 1: Đang thực hiện OCR...")
        ocr_text = self.ocr_agent.get_text(image_path)
        if not ocr_text:
            print("❌ ERROR: OCR thất bại, không thể đọc văn bản từ ảnh.")
            return

        # 2. NLP: Trích xuất thông tin
        print("STEP 2: Đang trích xuất thông tin (Company, Total Amount)...")
        extracted_info = process_invoice_text(ocr_text)

        # 3. Phân loại nghiệp vụ
        print("STEP 3: Đang phân loại nghiệp vụ...")
        category = self.classification_agent.classify(ocr_text)

        # 4. Tổng hợp kết quả
        print("STEP 4: Đang tổng hợp kết quả cuối cùng...")
        final_record = {
            "invoice_path": image_path,
            "company": extracted_info.get("company"),
            "total_amount": extracted_info.get("total_amount"),
            "category": category
        }

        # 5. Thực hiện hành động
        # print("STEP 5: Đang lưu kết quả...")
        # self.action_agent.save_to_excel(final_record)
        print("--- Xử lý hoàn tất! ---")

        return final_record