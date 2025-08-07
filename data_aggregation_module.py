import os
import pandas as pd
from config import BASE_LOG_DIR

def aggregate_logs(year: str, month: str) -> pd.DataFrame:
    """
    Tổng hợp tất cả các file log của một tháng cụ thể trong một năm.
    """
    month_dir = os.path.join(BASE_LOG_DIR, str(year), f"Month_{month}")
    all_records = []

    if not os.path.exists(month_dir):
        print(f"INFO: Không tìm thấy thư mục cho {month}/{year}")
        return pd.DataFrame() # Trả về DataFrame rỗng

    for filename in os.listdir(month_dir):
        if filename.endswith('.xlsx'):
            file_path = os.path.join(month_dir, filename)
            try:
                df = pd.read_excel(file_path)
                all_records.append(df)
            except Exception as e:
                print(f"WARNING: Không thể đọc file {file_path}. Lỗi: {e}")

    if not all_records:
        return pd.DataFrame()

    # Gộp tất cả các DataFrame lại
    aggregated_df = pd.concat(all_records, ignore_index=True)
    return aggregated_df