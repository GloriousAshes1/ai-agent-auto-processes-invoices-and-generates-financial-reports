# --- Cấu hình cho LLM và Server ---
OLLAMA_PORT = "11434"
MODEL_NAME = "llama3:8b"

# --- Cấu hình cho Thư mục và File ---
BASE_LOG_DIR = "AccountingLogs"
LOG_FILE_PATTERN = r"AccountingLog_(\d{2}-\d{2}-\d{4})\.xlsx"
LOG_SHEET_NAME = "AccountingLog"

MANUAL_REVIEW_FILE = "ManualReview.xlsx"
MANUAL_REVIEW_SHEET_NAME = "ReviewNeeded"

# --- Cấu hình cho Nghiệp vụ Kế toán ---
# Định nghĩa các hạng mục phân loại
CATEGORIES = {
    "sales_invoices": "VAT Receipts",
    "uncategorized": "Unidentifiable or uncategorized expenses."
}