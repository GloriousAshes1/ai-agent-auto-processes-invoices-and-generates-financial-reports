import streamlit as st
from invoice_processor_agent import InvoiceProcessorAgent
import os
import pandas as pd
from PIL import Image

# --- Cấu hình trang ---
st.set_page_config(page_title="Trợ lý Kế toán AI", layout="wide")

# --- Khởi tạo Agent (chỉ một lần) ---
# Sử dụng cache của Streamlit để không phải load lại model mỗi lần tương tác
@st.cache_resource
def load_agent():
    return InvoiceProcessorAgent()

agent = load_agent()
EXCEL_FILE = "NhatKyKeToan.xlsx"

# --- Giao diện ---
st.title("🤖 Trợ lý Kế toán AI: Xử lý Hóa đơn")
st.write("Tải lên ảnh hóa đơn của bạn, AI sẽ tự động trích xuất thông tin, phân loại và lưu vào file Excel.")

# Tạo 2 cột để bố cục đẹp hơn
col1, col2 = st.columns(2)

with col1:
    st.header("1. Tải lên hóa đơn")
    uploaded_file = st.file_uploader(
        "Chọn một file ảnh hóa đơn",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:
        # Hiển thị ảnh đã tải lên
        image = Image.open(uploaded_file)
        st.image(image, caption="Hóa đơn đã tải lên", use_container_width=True)

        # Nút để bắt đầu xử lý
        if st.button("Xử lý Hóa đơn", type="primary"):
            # Lưu tạm file ảnh để agent có thể đọc
            temp_dir = "temp_uploads"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Chạy agent và hiển thị kết quả
            with st.spinner('AI đang phân tích hóa đơn... Vui lòng chờ trong giây lát...'):
                result = agent.run(file_path)

            st.header("2. Kết quả trích xuất")
            if result:
                st.success("Xử lý thành công!")
                st.json(result)
            else:
                st.error("Xử lý thất bại. Vui lòng kiểm tra lại ảnh hoặc hóa đơn.")

            # Xóa file tạm
            os.remove(file_path)

with col2:
    st.header("3. Sổ Nhật ký Kế toán (Excel)")
    st.write("Dữ liệu sẽ được tự động cập nhật vào file này sau mỗi lần xử lý.")

    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu. Hãy xử lý hóa đơn đầu tiên!")
