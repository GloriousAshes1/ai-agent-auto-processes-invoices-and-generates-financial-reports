"""
NLP Module để rút trích thông tin từ hóa đơn.

Module này được tối ưu hóa để trích xuất Tên Công ty và Tổng tiền
từ các file hóa đơn có định dạng tương tự như các file đã cung cấp.
"""

import re
import os
from typing import Dict, Any
import json
from utils import get_llm_model

model = get_llm_model()

def extract_invoice_info(text_content: str) -> Dict[str, Any]:
    """
    Rút trích Tên Công ty và Tổng tiền từ nội dung văn bản của hóa đơn.
    Hiện tại chỉ hoạt động với hóa đơn VAT của VinCommerce
    Args:
        text_content: Nội dung plaintext của hóa đơn.

    Returns:
        Một dictionary chứa Tên Công ty và Tổng tiền.
    """
    info = {
        "company": None,
        "total_amount": None
    }

    # 1. Pattern cho Tên Công ty (hỗ trợ các biến thể OCR)
    company_pattern = r"(Vin|Vn|Mn)Commerce"
    company_match = re.search(company_pattern, text_content, re.IGNORECASE)

    # Gán giá trị chuẩn hóa nếu tìm thấy
    if company_match:
        info["company"] = "VinCommerce"

    # 2. Pattern cho Tổng tiền thanh toán
    # Dựa trên cấu trúc nhất quán: TONG TIEN PHAI T.TOAN
    total_pattern = r"TONG TIEN PHAI T\.TOAN\s*(-?[\d.,]+)"
    total_match = re.search(total_pattern, text_content)

    if total_match:
        # Lấy chuỗi số, loại bỏ dấu chấm và chuẩn hóa thành số thực
        amount_str = total_match.group(1).replace('.', '').replace(',', '.')
        try:
            info["total_amount"] = float(amount_str)
        except ValueError:
            info["total_amount"] = "value_error"

    # Nếu không tìm thấy công ty, gán giá trị mặc định
    if not info["company"]:
        info["company"] = "not_found"

    return info

def prompt_for_LLM(text):
    prompt = f"""
      Bạn là một trợ lý kế toán AI chuyên nghiệp.
      Nhiệm vụ của bạn là trích xuất chính xác các thông tin sau từ văn bản hóa đơn đã được OCR.

      Hãy trích xuất các trường thông tin sau và trả về kết quả dưới định dạng JSON:
      - company: Tên của cửa hàng hoặc công ty phát hành hóa đơn.
      - total_amount: Tổng số tiền cuối cùng khách hàng phải trả.

      Nếu không tìm thấy thông tin nào, hãy để giá trị là null.
      Chỉ trả về duy nhất đối tượng JSON, không thêm bất kỳ lời giải thích nào.

      Dưới đây là văn bản hóa đơn:
      ---
      {text}
      ---
      """
    return prompt

def extract_with_llm(ocr_text):
    try:
        prompt = prompt_for_LLM(ocr_text)

        # Gửi prompt đến API của Google
        response = model.generate_content(prompt)

        # Lấy phần text chứa JSON từ response
        # Cần xử lý để loại bỏ các ký tự ```json và ``` ở đầu và cuối nếu có
        json_text = response.text.strip().replace('```json', '').replace('```', '')

        # Chuyển chuỗi JSON thành dictionary
        extracted_data = json.loads(json_text)

        return extracted_data
    except Exception as e:
        print(f"❌ Error: {e}")

def process_invoice_text(text_content: str) -> Dict[str, Any]:
    """Thử trích xuất bằng regex trước, nếu thất bại thì dùng LLM."""
    print("INFO: Đang thử trích xuất bằng Regex...")
    regex_result = extract_invoice_info(text_content)

    # Kiểm tra xem regex có thành công không (ví dụ: tìm thấy công ty)
    if regex_result.get("company") != "not_found":
        print("✅ SUCCESS: Regex đã trích xuất thành công.")
        return regex_result

    print("WARNING: Regex thất bại. Chuyển sang dùng LLM...")
    llm_result = extract_with_llm(text_content)

    if llm_result:
        print("✅ SUCCESS: LLM đã trích xuất thành công.")
        return llm_result
    else:
        print("❌ ERROR: Cả Regex và LLM đều thất bại.")
        return {"company": "error", "total_amount": 0.0}
