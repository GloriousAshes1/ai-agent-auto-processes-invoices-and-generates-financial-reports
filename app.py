import streamlit as st
from invoice_processor_agent import InvoiceProcessorAgent
import os
import pandas as pd
from PIL import Image
from datetime import datetime
from utils import find_available_logs
import shutil

# --- Cấu hình trang ---
st.set_page_config(page_title="Trợ lý Kế toán AI", layout="wide")

# --- Khởi tạo Agent (chỉ một lần) ---
# Sử dụng cache của Streamlit để không phải load lại model mỗi lần tương tác
@st.cache_resource
def load_agent():
    return InvoiceProcessorAgent()

agent = load_agent()
today_str = datetime.now().strftime("%Y-%m-%d")
EXCEL_FILE = f"NhatKyKeToan_{today_str}.xlsx"

# --- Giao diện ---
st.title("🤖 Trợ lý Kế toán AI: Xử lý Hóa đơn")
st.write("Tải lên ảnh hóa đơn của bạn, AI sẽ tự động trích xuất thông tin, phân loại và lưu vào file Excel.")

# Tạo 2 cột để bố cục đẹp hơn
col1, col2 = st.columns(2)

with col1:
    st.header("1. Tải lên hóa đơn")
    uploaded_files = st.file_uploader(
        "Chọn một file ảnh hóa đơn",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    # if uploaded_files is not None:
    #     # Hiển thị ảnh đã tải lên
    #     image = Image.open(uploaded_files)
    #     st.image(image, caption="Hóa đơn đã tải lên", use_container_width=True)
    #
    #     # Nút để bắt đầu xử lý
    #     if st.button("Xử lý Hóa đơn", type="primary"):
    #         # Lưu tạm file ảnh để agent có thể đọc
    #         temp_dir = "temp_uploads"
    #         if not os.path.exists(temp_dir):
    #             os.makedirs(temp_dir)
    #
    #         file_path = os.path.join(temp_dir, uploaded_file.name)
    #         with open(file_path, "wb") as f:
    #             f.write(uploaded_file.getbuffer())
    #
    #         # Chạy agent và hiển thị kết quả
    #         with st.spinner('AI đang phân tích hóa đơn... Vui lòng chờ trong giây lát...'):
    #             result = agent.run(file_path)
    #
    #         st.header("2. Kết quả trích xuất")
    #         if result:
    #             st.success("Xử lý thành công!")
    #             st.json(result)
    #         else:
    #             st.error("Xử lý thất bại. Vui lòng kiểm tra lại ảnh hoặc hóa đơn.")
    #
    #         # Xóa file tạm
    #         os.remove(file_path)
    if uploaded_files:
        valid_results = []
        review_results = []

        if st.button(f"Xử lý {len(uploaded_files)} hóa đơn", type="primary"):
            st.header("2. Kết quả xử lý")
            progress_bar = st.progress(0, text="Bắt đầu xử lý...")

            today_str_folder = datetime.now().strftime("%d-%m-%Y")
            save_dir = os.path.join("uploaded_invoices", f"invoices_{today_str_folder}")
            os.makedirs(save_dir, exist_ok=True)

            for i, uploaded_file in enumerate(uploaded_files):
                # ... (cập nhật progress_bar và hiển thị expander như cũ)
                progress_text = f"Đang xử lý file: {uploaded_file.name} ({i + 1}/{len(uploaded_files)})"
                progress_bar.progress((i + 1) / len(uploaded_files), text=progress_text)

                with st.expander(f"Kết quả cho file: **{uploaded_file.name}**", expanded=False):
                    # ... (lưu file tạm và hiển thị ảnh như cũ)
                    st.image(Image.open(uploaded_file), width=200)

                    temp_dir = "temp_uploads"
                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)
                    temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(temp_file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Chạy agent
                    result = agent.run(temp_file_path)

                    if result:
                        # 1. Sao chép file vào thư mục lưu trữ cuối cùng
                        final_image_path = os.path.join(save_dir, uploaded_file.name)
                        try:
                            shutil.copy(temp_file_path, final_image_path)
                        except Exception as e:
                            st.warning(f"Lỗi khi lưu trữ file ảnh: {e}")

                        # 2. Cập nhật lại đường dẫn trong dictionary kết quả
                        result['invoice_path'] = final_image_path

                        # 3. Phân luồng dựa trên kết quả đã được cập nhật
                        if agent.action_agent.is_record_valid(result):
                            st.success("Hợp lệ! Sẽ được lưu vào Nhật ký Kế toán.")
                            valid_results.append(result)
                        else:
                            st.warning("Hóa đơn có vấn đề! Sẽ được chuyển cho nhân viên xử lý.")
                            review_results.append(result)
                        st.json(result)
                    else:
                        st.error("Xử lý thất bại.")
                    os.remove(temp_file_path)

            st.divider()
            st.header("Tổng kết xử lý hàng loạt")

            # Lấy thông tin tháng và năm
            now = datetime.now()
            year_str = now.strftime("%Y")
            month_str = now.strftime("%m")  # ví dụ: "08"
            today_str = now.strftime("%Y-%m-%d")

            # Tạo đường dẫn thư mục năm/tháng (ví dụ: NhatKyKeToan/2025/Thang_08)
            year_month_dir = os.path.join("NhatKyKeToan", year_str, f"Thang_{month_str}")  # << THAY ĐỔI DÒNG NÀY
            os.makedirs(year_month_dir, exist_ok=True)

            # Lưu các kết quả hợp lệ
            if valid_results:
                # Tạo đường dẫn đầy đủ đến file Excel của ngày hôm nay
                excel_path_today = os.path.join(year_month_dir, f"NhatKyKeToan_{today_str}.xlsx")
                agent.action_agent.save_all_to_excel(valid_results, excel_path_today, 'NhatKyKeToan')
                st.success(f"Đã lưu thành công {len(valid_results)} hóa đơn hợp lệ vào file {excel_path_today}.")
            else:
                st.info("Không có hóa đơn hợp lệ nào để lưu.")

            # Lưu các kết quả cần review (file review vẫn giữ ở thư mục gốc cho đơn giản)
            if review_results:
                review_file = "CanXuLyBangTay.xlsx"
                agent.action_agent.save_all_to_excel(review_results, review_file, 'CanXuLy')
                st.warning(
                    f"Đã chuyển {len(review_results)} hóa đơn có vấn đề đến file {review_file} để xử lý thủ công.")
            else:
                st.info("Không có hóa đơn nào cần xử lý thủ công.")

            st.balloons()

with col2:
    st.header("3. Tra cứu Sổ Nhật ký Kế toán")

    # Gọi hàm mới để lấy dictionary các file log
    available_logs = find_available_logs()

    if not available_logs:
        st.info("Chưa có file Nhật ký Kế toán nào được lưu.")
    else:
        # Sắp xếp các ngày (keys của dictionary) để hiển thị trên selectbox
        sorted_dates = sorted(available_logs.keys(), reverse=True)

        selected_date = st.selectbox(
            "Chọn ngày để xem lại dữ liệu:",
            options=sorted_dates
        )

        if selected_date:
            # Lấy đường dẫn file trực tiếp từ dictionary - GỌN HƠN RẤT NHIỀU
            selected_excel_file_path = available_logs[selected_date]

            st.write(f"Đang hiển thị dữ liệu từ file: **{selected_excel_file_path}**")

            if os.path.exists(selected_excel_file_path):
                df_main = pd.read_excel(selected_excel_file_path)
                st.dataframe(df_main, use_container_width=True, height=250)

                with open(selected_excel_file_path, "rb") as file:
                    st.download_button(
                        label=f"📥 Tải về file của ngày {selected_date}",
                        data=file,
                        file_name=os.path.basename(selected_excel_file_path),
                        mime="application/vnd.ms-excel"
                    )
            else:
                st.error(f"Lỗi: Không tìm thấy file tại đường dẫn '{selected_excel_file_path}'.")

st.divider()
st.header("⚠️ Hóa đơn cần xử lý bằng tay")
review_file = "CanXuLyBangTay.xlsx"
if os.path.exists(review_file):
    df_review = pd.read_excel(review_file)
    st.dataframe(df_review, use_container_width=True, height=300)
else:
    st.info("Không có hóa đơn nào cần xử lý thủ công.")
