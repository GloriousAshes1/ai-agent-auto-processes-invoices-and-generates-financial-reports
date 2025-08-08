import pandas as pd
import os


class ActionAgent:
    def __init__(self):
        self.review_file_path = "ManualReview.xlsx"

    def is_record_valid(self, record: dict) -> bool:
        """Kiểm tra xem bản ghi có hợp lệ để xử lý tự động không."""
        total_amount = record.get("total_amount")
        # Trả về False nếu total_amount là None, không phải số, hoặc <= 0
        if total_amount is None or not isinstance(total_amount, (int, float)) or total_amount <= 0:
            return False
        return True

    def save_to_excel(self, records: list, excel_path: str, sheet_name: str):
        """Hàm chung để ghi một danh sách các bản ghi vào file Excel."""
        if not records:
            return # Không làm gì nếu danh sách rỗng

        print(f"INFO: Đang lưu {len(records)} bản ghi vào file: {excel_path}")
        new_records_df = pd.DataFrame(records)
        try:
            if os.path.exists(excel_path):
                existing_df = pd.read_excel(excel_path)
                updated_df = pd.concat([existing_df, new_records_df], ignore_index=True)
            else:
                updated_df = new_records_df

            updated_df.to_excel(excel_path, index=False, sheet_name=sheet_name)
            print(f"✅ SUCCESS: Đã lưu thành công.")
        except Exception as e:
            print(f"❌ ERROR: Không thể ghi hàng loạt vào file Excel. Lỗi: {e}")