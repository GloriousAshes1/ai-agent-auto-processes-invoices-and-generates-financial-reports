import pandas as pd
import os

class ActionAgent:
    def __init__(self):
        pass

    def _validate_record(self, record: dict) -> bool:
        """Kiểm tra dữ liệu trước khi thực hiện hành động."""
        if not isinstance(record.get("total_amount"), (int, float)) or record["total_amount"] <= 0:
            print(f"❌ Dữ liệu không hợp lệ: {record}")
            return False
        return True

    def save_to_excel(self, record: dict, excel_path="NhatKyKeToan.xlsx"):
        """Lưu một bản ghi vào file Excel."""
        if not self._validate_record(record):
            return

        df = pd.DataFrame([record])
        if not os.path.exists(excel_path):
            df.to_excel(excel_path, index=False, sheet_name='NhatKyKeToan')
        else:
            with pd.ExcelWriter(excel_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, header=False, index=False, startrow=writer.sheets['NhatKyKeToan'].max_row)