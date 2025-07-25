import streamlit as st
from paddleocr import PaddleOCR
from pdf2image import convert_from_bytes
import numpy as np
import cv2
import os
from datetime import datetime
from io import BytesIO
from PIL import Image

# Khởi tạo OCR
ocr = PaddleOCR(
    use_textline_orientation=True,
    text_detection_model_name='PP-OCRv5_server_det',
    text_recognition_model_name='PP-OCRv5_server_rec',
)

st.set_page_config(page_title="Invoice OCR (Image + PDF)", layout="wide")
st.title("📄 AI Nhận dạng Hóa đơn (Ảnh & PDF) bằng PaddleOCR")

uploaded_files = st.file_uploader(
    "📤 Tải lên nhiều ảnh hoặc PDF hóa đơn",
    type=["jpg", "jpeg", "png", "pdf"],
    accept_multiple_files=True
)

# Bắt đầu OCR khi nhấn nút
if uploaded_files and st.button("🚀 Bắt đầu OCR"):
    os.makedirs("./output/raw_results", exist_ok=True)
    today_str = datetime.now().strftime("%d%m%Y")
    index = 1

    for file in uploaded_files:
        filename = file.name
        ext = filename.lower().split('.')[-1]

        st.markdown(f"---\n### 📁 File: `{filename}`")

        # Ảnh đơn
        if ext in ['jpg', 'jpeg', 'png']:
            file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            result = ocr.predict(img)
            for res in result:
                st.code(res.print(), language='text')
                res.save_to_img(save_path="./output/")
                json_path = f"./output/raw_results/invoice_{index}_{today_str}.json"
                res.save_to_json(save_path=json_path)
                st.success(f"✅ Đã lưu JSON: `{json_path}`")
                index += 1

        # PDF
        elif ext == 'pdf':
            pdf_pages = convert_from_bytes(file.read(), dpi=300)
            for page_num, page in enumerate(pdf_pages, start=1):
                img = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
                result = ocr.predict(img)

                st.markdown(f"#### 📄 Trang {page_num} của {filename}")
                for res in result:
                    st.code(res.print(), language='text')
                    res.save_to_img(save_path="./output/")
                    json_path = f"./output/raw_results/invoice_{index}_{today_str}.json"
                    res.save_to_json(save_path=json_path)
                    st.success(f"✅ Đã lưu JSON: `{json_path}`")
                    index += 1

    st.success("🎉 Đã xử lý xong tất cả file!")
