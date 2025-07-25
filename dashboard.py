import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import base64
from datetime import datetime, timedelta
import re
import io
from PIL import Image
import json
import os
import cv2
import time
import numpy as np
from datetime import datetime
from paddleocr import PaddleOCR
from pdf2image import convert_from_bytes

# Cấu hình trang
st.set_page_config(
    page_title="AI Invoice Processing System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }

    /* Header Styles */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }

    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }

    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }

    /* Module Cards */
    .module-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border: 2px solid rgba(102, 126, 234, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }

    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.4);
    }

    .module-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .module-desc {
        color: #666;
        line-height: 1.6;
    }

    /* Status Indicators */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.25rem;
    }

    .status-ready {
        background: rgba(76, 175, 80, 0.1);
        color: #4CAF50;
        border: 1px solid rgba(76, 175, 80, 0.3);
    }

    .status-processing {
        background: rgba(255, 152, 0, 0.1);
        color: #FF9800;
        border: 1px solid rgba(255, 152, 0, 0.3);
        animation: pulse 2s infinite;
    }

    .status-completed {
        background: rgba(33, 150, 243, 0.1);
        color: #2196F3;
        border: 1px solid rgba(33, 150, 243, 0.3);
    }

    .status-error {
        background: rgba(244, 67, 54, 0.1);
        color: #F44336;
        border: 1px solid rgba(244, 67, 54, 0.3);
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }

    /* Metric Cards */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }

    .metric-number {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .metric-label {
        color: #666;
        font-weight: 500;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 1px;
    }

    /* Progress Bar */
    .progress-container {
        background: #f0f0f0;
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
        margin: 1rem 0;
        position: relative;
    }

    .progress-bar {
        background: linear-gradient(135deg, #667eea, #764ba2);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
        position: relative;
    }

    .progress-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-weight: 600;
        font-size: 0.85rem;
    }

    /* Upload Area */
    .upload-area {
        border: 3px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
        transition: all 0.3s ease;
    }

    .upload-area:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
    }

    /* Pipeline Steps */
    .pipeline-step {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }

    .pipeline-step:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }

    .step-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }

    .step-icon {
        font-size: 1.5rem;
    }

    .step-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
    }

    /* Data Table Styling */
    .dataframe {
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4) !important;
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
    }

    /* Hide Streamlit Menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = 0
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = {
        'ocr': 'ready',
        'nlp': 'ready',
        'classification': 'ready',
        'action': 'ready'
    }
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = []
if 'classification_results' not in st.session_state:
    st.session_state.classification_results = {
        'Hàng hóa': 12,
        'Dịch vụ': 8,
        'Văn phòng phẩm': 5,
        'Khác': 3
    }

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Invoice Processing System</h1>
    <p>Hệ thống AI tự động xử lý hóa đơn và sinh báo cáo tài chính</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
# with st.sidebar:
#     st.markdown("### ⚙️ Cấu hình hệ thống")
#
#     # System Settings
#     ocr_confidence = st.slider("OCR Confidence Threshold", 0.5, 1.0, 0.85, 0.05)
#     classification_model = st.selectbox(
#         "Classification Model",
#         ["Naive Bayes", "SVM", "Random Forest", "Neural Network"]
#     )
#
#     st.markdown("### 📊 Thống kê hệ thống")
#
#     # System metrics
#     col1, col2 = st.columns(2)
#     with col1:
#         st.metric("Files đã xử lý", st.session_state.processed_files)
#     with col2:
#         st.metric("Độ chính xác", "95.2%")
#
#     st.metric("Thời gian xử lý TB", "2.3s/file")
#     st.metric("Uptime", "99.8%")
#
#     st.markdown("### 🔧 Actions")
#     if st.button("🔄 Reset System"):
#         st.session_state.uploaded_files = []
#         st.session_state.processed_files = 0
#         st.session_state.extracted_data = []
#         st.experimental_rerun()
#
#     if st.button("📥 Export Settings"):
#         settings = {
#             'ocr_confidence': ocr_confidence,
#             'classification_model': classification_model,
#             'timestamp': datetime.now().isoformat()
#         }
#         st.download_button(
#             "Download Config",
#             json.dumps(settings, indent=2),
#             "config.json",
#             "application/json"
#         )
# Khởi tạo PaddleOCR
@st.cache_resource
def init_ocr():
    return PaddleOCR(
        use_textline_orientation=True,
        text_detection_model_name='PP-OCRv5_server_det',
        text_recognition_model_name='PP-OCRv5_server_rec',
    )

ocr = init_ocr()

def process_invoices():
    progress_bar = st.progress(0)
    status_text = st.empty()

    stages = ['ocr', 'nlp', 'classification', 'action']
    stage_names = ['OCR Processing', 'NLP Extraction', 'Classification', 'Data Export']

    # Tạo thư mục kết quả nếu chưa có
    os.makedirs("./output/", exist_ok=True)
    os.makedirs("./output/raw_results/", exist_ok=True)

    today_str = datetime.now().strftime("%d%m%Y")
    index = 1
    num_files = len(st.session_state.uploaded_files)

    for i_stage, (stage, name) in enumerate(zip(stages, stage_names)):

        st.session_state.processing_status[stage] = 'processing'
        status_text.text(f"🔄 {name}...")

        if stage == "ocr":
            for i_file, file in enumerate(st.session_state.uploaded_files, start=1):
                filename = file.name
                ext = filename.split('.')[-1].lower()

                if ext in ["jpg", "jpeg", "png"]:
                    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
                    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                    results = ocr.predict(img)

                    for res in results:
                        # st.code(res.print())
                        res.save_to_img(save_path="./output/")
                        json_path = f"./output/raw_results/invoice_{index}_{today_str}.json"
                        res.save_to_json(save_path=json_path)
                        # st.success(f"✅ Lưu kết quả: {json_path}")
                        index += 1

                elif ext == "pdf":
                    pages = convert_from_bytes(file.read(), dpi=300)
                    for page in pages:
                        img = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
                        results = ocr.predict(img)
                        for res in results:
                            # st.code(res.print())
                            res.save_to_img(save_path="./output/")
                            json_path = f"./output/raw_results/invoice_{index}_{today_str}.json"
                            res.save_to_json(save_path=json_path)
                            # st.success(f"✅ Lưu kết quả: {json_path}")
                            index += 1

                progress = ((i_stage * num_files + i_file) / (num_files * len(stages)))
                progress_bar.progress(min(progress, 1.0))

        else:
            # Giả lập các bước còn lại
            for j in range(25):
                time.sleep(0.01)
                progress = ((i_stage * 25 + j + 1) / 100)
                progress_bar.progress(min(progress, 1.0))

        st.session_state.processing_status[stage] = 'completed'

    st.session_state.processed_files = len(st.session_state.uploaded_files)
    status_text.text("✅ Xử lý hoàn tất!")
    st.success("🎉 Đã xử lý thành công tất cả hóa đơn!")
# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Process", "🔄 Pipeline Status", "📊 Results", "📈 Analytics"])

with tab1:
    st.markdown("## 📤 Tải lên và xử lý hóa đơn")

    # File upload section
    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_files = st.file_uploader(
            "Chọn file hóa đơn (PDF, JPG, PNG)",
            type=['pdf', 'jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            help="Kéo thả hoặc click để chọn nhiều file cùng lúc"
        )

        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files

            # Display uploaded files
            st.markdown("### 📋 Files đã tải lên:")
            for i, file in enumerate(uploaded_files):
                col_file, col_size, col_type = st.columns([3, 1, 1])
                with col_file:
                    st.write(f"📄 {file.name}")
                with col_size:
                    st.write(f"{file.size / 1024:.1f} KB")
                with col_type:
                    st.write(file.type.split('/')[-1].upper())

    with col2:
        # Stats cards
        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">{}</div>
            <div class="metric-label">Total Files</div>
        </div>
        """.format(len(st.session_state.uploaded_files)), unsafe_allow_html=True)

        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">{}</div>
            <div class="metric-label">Processed</div>
        </div>
        """.format(st.session_state.processed_files), unsafe_allow_html=True)

    # Processing buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("🚀 Bắt đầu xử lý", type="primary"):
            if st.session_state.uploaded_files:
                process_invoices()
            else:
                st.error("Vui lòng tải lên file trước khi xử lý!")

    with col2:
        if st.button("🗑️ Xóa tất cả"):
            st.session_state.uploaded_files = []
            st.session_state.processed_files = 0
            st.session_state.extracted_data = []
            # st.experimental_user()

with tab2:
    st.markdown("## 🔄 Trạng thái Pipeline xử lý")

    # # Pipeline visualization
    # pipeline_steps = [
    #     {
    #         'icon': '👁️',
    #         'title': 'OCR Module',
    #         'desc': 'Paddle OCR đọc nội dung từ hình ảnh hóa đơn',
    #         'status': st.session_state.processing_status['ocr'],
    #         'details': f'Confidence: {ocr_confidence:.0%} | Language: VI, EN'
    #     },
    #     {
    #         'icon': '🧠',
    #         'title': 'NLP Module',
    #         'desc': 'Rút trích thông tin cấu trúc từ văn bản',
    #         'status': st.session_state.processing_status['nlp'],
    #         'details': 'Regex + Named Entity Recognition'
    #     },
    #     {
    #         'icon': '🎯',
    #         'title': 'Classification Agent',
    #         'desc': 'Phân loại nghiệp vụ kế toán tự động',
    #         'status': st.session_state.processing_status['classification'],
    #         'details': f'Model: {classification_model} | Accuracy: 95.2%'
    #     },
    #     {
    #         'icon': '💾',
    #         'title': 'Action Agent',
    #         'desc': 'Lưu kết quả và tích hợp với hệ thống',
    #         'status': st.session_state.processing_status['action'],
    #         'details': 'Export: Excel, CSV | API Integration'
    #     }
    # ]
    #
    # # Display pipeline steps
    # for step in pipeline_steps:
    #     status_class = f"status-{step['status']}"
    #     status_text = {
    #         'ready': '🟢 Sẵn sàng',
    #         'processing': '🟡 Đang xử lý',
    #         'completed': '🔵 Hoàn thành',
    #         'error': '🔴 Lỗi'
    #     }.get(step['status'], '⚪ Không xác định')
    #
    #     st.markdown(f"""
    #     <div class="pipeline-step">
    #         <div class="step-header">
    #             <span class="step-icon">{step['icon']}</span>
    #             <span class="step-title">{step['title']}</span>
    #             <span class="status-badge {status_class}">{status_text}</span>
    #         </div>
    #         <p class="module-desc">{step['desc']}</p>
    #         <small style="color: #888;">{step['details']}</small>
    #     </div>
    #     """, unsafe_allow_html=True)
    #
    # # Overall progress
    # completed_steps = sum(1 for status in st.session_state.processing_status.values() if status == 'completed')
    # progress_percent = (completed_steps / len(pipeline_steps)) * 100

    # st.markdown("### 📊 Tiến độ tổng thể")
    # st.progress(progress_percent / 100)
    # st.write(f"**{progress_percent:.0f}% hoàn thành** ({completed_steps}/{len(pipeline_steps)} bước)")

with tab3:
    st.markdown("## 📊 Kết quả xử lý")

    # if not st.session_state.extracted_data:
    #     st.info("Chưa có dữ liệu. Vui lòng tải lên và xử lý hóa đơn trước.")
    # else:
    #     # Results tabs
    #     subtab1, subtab2, subtab3 = st.tabs(["📋 Dữ liệu trích xuất", "🏷️ Phân loại", "📊 Báo cáo"])
    #
    #     with subtab1:
    #         st.markdown("### 📋 Dữ liệu đã trích xuất")
    #
    #         # Display extracted data
    #         df = pd.DataFrame(st.session_state.extracted_data)
    #         st.dataframe(df, use_container_width=True)
    #
    #         # Download options
    #         col1, col2, col3 = st.columns(3)
    #         with col1:
    #             csv = df.to_csv(index=False)
    #             st.download_button(
    #                 "📥 Tải CSV",
    #                 csv,
    #                 "invoice_data.csv",
    #                 "text/csv"
    #             )
    #         with col2:
    #             # Convert to Excel
    #             buffer = io.BytesIO()
    #             with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    #                 df.to_excel(writer, index=False, sheet_name='Invoice_Data')
    #
    #             st.download_button(
    #                 "📥 Tải Excel",
    #                 buffer.getvalue(),
    #                 "invoice_data.xlsx",
    #                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #             )
    #         with col3:
    #             json_data = df.to_json(orient='records', indent=2)
    #             st.download_button(
    #                 "📥 Tải JSON",
    #                 json_data,
    #                 "invoice_data.json",
    #                 "application/json"
    #             )
    #
    #     with subtab2:
    #         st.markdown("### 🏷️ Kết quả phân loại")
    #
    #         # Classification results
    #         col1, col2 = st.columns([1, 2])
    #
    #         with col1:
    #             for category, count in st.session_state.classification_results.items():
    #                 st.markdown(f"""
    #                 <div class="metric-card">
    #                     <div class="metric-number">{count}</div>
    #                     <div class="metric-label">{category}</div>
    #                 </div>
    #                 """, unsafe_allow_html=True)
    #
    #         with col2:
    #             # Pie chart
    #             fig = px.pie(
    #                 values=list(st.session_state.classification_results.values()),
    #                 names=list(st.session_state.classification_results.keys()),
    #                 title="Phân bố loại hóa đơn",
    #                 color_discrete_sequence=px.colors.qualitative.Set3
    #             )
    #             fig.update_layout(
    #                 font=dict(size=14),
    #                 title_font_size=18,
    #                 showlegend=True
    #             )
    #             st.plotly_chart(fig, use_container_width=True)
    #
    #     with subtab3:
    #         st.markdown("### 📊 Báo cáo tài chính")
    #
    #         # Sample financial metrics
    #         col1, col2, col3, col4 = st.columns(4)
    #
    #         with col1:
    #             total_amount = sum(
    #                 int(re.sub(r'[^\d]', '', item['Tổng tiền'])) for item in st.session_state.extracted_data)
    #             st.metric("Tổng doanh thu", f"{total_amount:,} VNĐ")
    #
    #         with col2:
    #             total_tax = sum(int(re.sub(r'[^\d]', '', item['Thuế VAT'])) for item in st.session_state.extracted_data)
    #             st.metric("Tổng thuế VAT", f"{total_tax:,} VNĐ")
    #
    #         with col3:
    #             st.metric("Số hóa đơn", len(st.session_state.extracted_data))
    #
    #         with col4:
    #             avg_amount = total_amount / len(
    #                 st.session_state.extracted_data) if st.session_state.extracted_data else 0
    #             st.metric("Giá trị TB", f"{avg_amount:,.0f} VNĐ")
    #
    #         # Revenue trend chart
    #         dates = pd.date_range(
    #             start=datetime.now() - timedelta(days=30),
    #             end=datetime.now(),
    #             freq='D'
    #         )
    #         revenue_data = pd.DataFrame({
    #             'Ngày': dates,
    #             'Doanh thu': np.random.randint(500000, 2000000, len(dates))
    #         })
    #
    #         fig = px.line(
    #             revenue_data,
    #             x='Ngày',
    #             y='Doanh thu',
    #             title='Xu hướng doanh thu 30 ngày qua',
    #             markers=True
    #         )
    #         fig.update_layout(
    #             xaxis_title="Ngày",
    #             yaxis_title="Doanh thu (VNĐ)",
    #             font=dict(size=12)
    #         )
    #         st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("## 📈 Phân tích và thống kê")

    # # Performance metrics
    # col1, col2 = st.columns(2)
    #
    # with col1:
    #     # Processing time chart
    #     processing_times = np.random.normal(2.3, 0.5, 100)
    #     fig = px.histogram(
    #         x=processing_times,
    #         nbins=20,
    #         title="Phân bố thời gian xử lý",
    #         labels={'x': 'Thời gian (giây)', 'y': 'Số lượng file'}
    #     )
    #     st.plotly_chart(fig, use_container_width=True)
    #
    # with col2:
    #     # Accuracy over time
    #     dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    #     accuracy_data = pd.DataFrame({
    #         'Ngày': dates,
    #         'Độ chính xác': np.random.uniform(0.93, 0.98, len(dates))
    #     })
    #
    #     fig = px.line(
    #         accuracy_data,
    #         x='Ngày',
    #         y='Độ chính xác',
    #         title='Độ chính xác theo thời gian',
    #         range_y=[0.9, 1.0]
    #     )
    #     st.plotly_chart(fig, use_container_width=True)
    #
    # # System health
    # st.markdown("### 🏥 Tình trạng hệ thống")
    #
    # health_metrics = {
    #     'CPU Usage': np.random.uniform(20, 80),
    #     'Memory Usage': np.random.uniform(30, 70),
    #     'Disk Usage': np.random.uniform(40, 60),
    #     'Network I/O': np.random.uniform(10, 90)
    # }
    #
    # cols = st.columns(len(health_metrics))
    # for i, (metric, value) in enumerate(health_metrics.items()):
    #     with cols[i]:
    #         # Progress bar for each metric
    #         color = "normal" if value < 70 else "inverse"
    #         st.metric(metric, f"{value:.1f}%")
    #         st.progress(value / 100)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🤖 <strong>AI Invoice Processing System</strong> | Phiên bản 1.0.0</p>
    <p>Được phát triển với ❤️ bằng Streamlit, Paddle OCR, và Machine Learning</p>
</div>
""", unsafe_allow_html=True)