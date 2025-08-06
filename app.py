import streamlit as st
from invoice_processor_agent import InvoiceProcessorAgent
import os
import pandas as pd
from PIL import Image
from datetime import datetime
from utils import find_available_logs
import shutil

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Accounting Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🤖"
)


# --- Initialize Agent (only once) ---
@st.cache_resource
def load_agent():
    return InvoiceProcessorAgent()


agent = load_agent()
today_str = datetime.now().strftime("%Y-%m-%d")

# --- Modern CSS Styling ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 50%, #e8ebff 100%);
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
    }

    .main-container {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 40px;
        margin: 20px;
        box-shadow: 0 25px 50px rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.1);
    }

    .hero-section {
        text-align: center;
        padding: 60px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 40px;
        color: white;
        position: relative;
        overflow: hidden;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 6s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }

    .hero-title {
        font-size: 3.5em;
        font-weight: 700;
        margin-bottom: 20px;
        text-shadow: 0 4px 8px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }

    .hero-subtitle {
        font-size: 1.3em;
        font-weight: 400;
        opacity: 0.9;
        margin-bottom: 0;
        position: relative;
        z-index: 1;
    }

    .card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,249,255,0.95) 100%);
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
        border: 1px solid rgba(102, 126, 234, 0.1);
        margin-bottom: 30px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        backdrop-filter: blur(10px);
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
    }

    .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 2px solid #f8f9fa;
    }

    .card-icon {
        font-size: 2em;
        margin-right: 15px;
        padding: 12px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .card-title {
        font-size: 1.5em;
        font-weight: 600;
        color: #2c3e50;
        margin: 0;
    }

    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 1.1em;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        width: 100%;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }

    .stDownloadButton>button {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 1em;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(86, 171, 47, 0.4);
    }

    .stDownloadButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(86, 171, 47, 0.6);
    }

    .stFileUploader {
        border: 2px dashed #667eea;
        border-radius: 16px;
        padding: 40px 20px;
        text-align: center;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    .stFileUploader:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%);
        transform: translateY(-2px);
    }

    .stFileUploader label {
        font-size: 1.2em;
        font-weight: 500;
        color: #667eea;
    }

    .upload-icon {
        font-size: 3em;
        color: #667eea;
        margin-bottom: 15px;
    }

    .stExpander {
        border: none;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        overflow: hidden;
    }

    .stExpander > div:first-child {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 16px 16px 0 0;
        padding: 15px 20px;
        font-weight: 500;
        color: #495057;
    }

    .stExpander > div:first-child:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
    }

    .status-success {
        background: linear-gradient(135deg, rgba(212, 237, 218, 0.9) 0%, rgba(195, 230, 203, 0.9) 100%);
        color: #155724;
        padding: 15px 20px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #28a745;
        font-weight: 500;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(40, 167, 69, 0.2);
    }

    .status-warning {
        background: linear-gradient(135deg, rgba(255, 243, 205, 0.9) 0%, rgba(255, 234, 167, 0.9) 100%);
        color: #856404;
        padding: 15px 20px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #ffc107;
        font-weight: 500;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 193, 7, 0.2);
    }

    .status-error {
        background: linear-gradient(135deg, rgba(248, 215, 218, 0.9) 0%, rgba(245, 198, 203, 0.9) 100%);
        color: #721c24;
        padding: 15px 20px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #dc3545;
        font-weight: 500;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(220, 53, 69, 0.2);
    }

    .status-info {
        background: linear-gradient(135deg, rgba(209, 236, 241, 0.9) 0%, rgba(190, 229, 235, 0.9) 100%);
        color: #0c5460;
        padding: 15px 20px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #17a2b8;
        font-weight: 500;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(23, 162, 184, 0.2);
    }

    .dataframe-container {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
        border: 1px solid rgba(102, 126, 234, 0.1);
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,249,255,0.95) 100%);
        backdrop-filter: blur(10px);
    }

    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 30px 0;
        gap: 20px;
    }

    .stat-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,249,255,0.9) 100%);
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.1);
        flex: 1;
        transition: transform 0.3s ease;
        backdrop-filter: blur(10px);
    }

    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
    }

    .stat-number {
        font-size: 2.5em;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 10px;
    }

    .stat-label {
        font-size: 1em;
        font-weight: 500;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .progress-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,249,255,0.95) 100%);
        border-radius: 16px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
        border: 1px solid rgba(102, 126, 234, 0.1);
        backdrop-filter: blur(10px);
    }

    .divider {
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, rgba(102, 126, 234, 0.3) 20%, #667eea 50%, rgba(102, 126, 234, 0.3) 80%, transparent 100%);
        margin: 40px 0;
        border: none;
    }

    /* Custom selectbox styling */
    .stSelectbox > div > div {
        background: white;
        border-radius: 12px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }

    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* Animation for balloons */
    .balloon-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Hero Section ---
st.markdown(
    """
    <div class="hero-section">
        <div class="hero-title">🤖 AI Accounting Assistant</div>
        <div class="hero-subtitle">Xử lý hóa đơn tự động với AI thông minh • Tiết kiệm thời gian • Chính xác cao ✨</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Create main layout with improved spacing
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    # Upload Section Card
    st.markdown(
        """
        <div class="card">
            <div class="card-header">
                <div class="card-icon">📤</div>
                <h2 class="card-title">Tải lên hóa đơn</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Custom file uploader with icon
    st.markdown('<div class="upload-icon">📁</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Kéo thả hình ảnh hóa đơn vào đây hoặc nhấn để chọn file",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="Định dạng hỗ trợ: PNG, JPG, JPEG • Tối đa 200MB mỗi file"
    )

    if uploaded_files:
        # Show file statistics
        st.markdown(
            f"""
            <div class="stats-container">
                <div class="stat-card">
                    <div class="stat-number">{len(uploaded_files)}</div>
                    <div class="stat-label">Files đã chọn</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(f.size for f in uploaded_files) / 1024 / 1024:.1f}</div>
                    <div class="stat-label">MB tổng cộng</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        valid_results = []
        review_results = []

        if st.button(f"🚀 Xử lý {len(uploaded_files)} hóa đơn", type="primary"):
            # Processing section with modern design
            st.markdown('<div class="progress-container">', unsafe_allow_html=True)
            st.markdown("### 🔄 Đang xử lý hóa đơn...")
            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            progress_bar = st.progress(0, text="Bắt đầu xử lý...")

            today_str_folder = datetime.now().strftime("%d-%m-%Y")
            save_dir = os.path.join("uploaded_invoices", f"invoices_{today_str_folder}")
            os.makedirs(save_dir, exist_ok=True)

            for i, uploaded_file in enumerate(uploaded_files):
                progress_text = f"Đang xử lý: **{uploaded_file.name}** ({i + 1}/{len(uploaded_files)})"
                progress_bar.progress((i + 1) / len(uploaded_files), text=progress_text)

                with st.expander(f"📋 Kết quả: **{uploaded_file.name}**", expanded=False):
                    # Create two columns for image and results
                    img_col, result_col = st.columns([1, 2])

                    with img_col:
                        st.image(Image.open(uploaded_file), caption="Hóa đơn đã tải lên", use_column_width=True)

                    with result_col:
                        temp_dir = "temp_uploads"
                        if not os.path.exists(temp_dir):
                            os.makedirs(temp_dir)
                        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(temp_file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        # Run agent
                        result = agent.run(temp_file_path)

                        if result:
                            final_image_path = os.path.join(save_dir, uploaded_file.name)
                            try:
                                shutil.copy(temp_file_path, final_image_path)
                                st.caption(f"💾 Đã lưu tại: `{final_image_path}`")
                            except Exception as e:
                                st.markdown(f'<div class="status-warning">⚠️ Lỗi khi lưu file: {e}</div>',
                                            unsafe_allow_html=True)

                            result['invoice_path'] = final_image_path

                            if agent.action_agent.is_record_valid(result):
                                st.markdown(
                                    '<div class="status-success">✅ Hợp lệ! Sẽ được lưu vào Nhật ký kế toán</div>',
                                    unsafe_allow_html=True)
                                valid_results.append(result)
                            else:
                                st.markdown(
                                    '<div class="status-warning">⚠️ Phát hiện vấn đề! Hóa đơn sẽ được chuyển để xử lý thủ công</div>',
                                    unsafe_allow_html=True)
                                review_results.append(result)

                            # Display results in a more readable format
                            st.json(result)
                        else:
                            st.markdown('<div class="status-error">❌ Xử lý thất bại cho hóa đơn này</div>',
                                        unsafe_allow_html=True)

                        os.remove(temp_file_path)

            st.markdown('</div>', unsafe_allow_html=True)

            # Summary section with modern cards
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown("### 📊 Tổng kết xử lý")

            now = datetime.now()
            year_str = now.strftime("%Y")
            month_str = now.strftime("%m")
            today_str = now.strftime("%Y-%m-%d")

            year_month_dir = os.path.join("NhatKyKeToan", year_str, f"Thang_{month_str}")
            os.makedirs(year_month_dir, exist_ok=True)

            # Results statistics
            st.markdown(
                f"""
                <div class="stats-container">
                    <div class="stat-card">
                        <div class="stat-number">{len(valid_results)}</div>
                        <div class="stat-label">Hóa đơn hợp lệ</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(review_results)}</div>
                        <div class="stat-label">Cần xem xét</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(uploaded_files)}</div>
                        <div class="stat-label">Tổng số xử lý</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if valid_results:
                excel_path_today = os.path.join(year_month_dir, f"NhatKyKeToan_{today_str}.xlsx")
                agent.action_agent.save_to_excel(valid_results, excel_path_today, 'NhatKyKeToan')
                st.markdown(
                    f'<div class="status-success">🎉 Đã lưu thành công {len(valid_results)} hóa đơn hợp lệ vào: **{excel_path_today}**</div>',
                    unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-info">ℹ️ Không có hóa đơn hợp lệ để lưu</div>', unsafe_allow_html=True)

            if review_results:
                review_file = "CanXuLyBangTay.xlsx"
                agent.action_agent.save_to_excel(review_results, review_file, 'CanXuLy')
                st.markdown(
                    f'<div class="status-warning">⚠️ {len(review_results)} hóa đơn có vấn đề đã được chuyển vào **{review_file}** để xử lý thủ công</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown('<div class="status-success">🎉 Không có hóa đơn nào cần xử lý thủ công</div>',
                            unsafe_allow_html=True)

            st.balloons()

with col2:
    # Lookup Section Card
    st.markdown(
        """
        <div class="card">
            <div class="card-header">
                <div class="card-icon">📊</div>
                <h2 class="card-title">Tra cứu nhật ký</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    available_logs = find_available_logs()

    if not available_logs:
        st.markdown('<div class="status-info">🤷 Chưa có file nhật ký kế toán nào</div>', unsafe_allow_html=True)
    else:
        sorted_dates = sorted(available_logs.keys(), reverse=True)

        selected_date = st.selectbox(
            "📅 Chọn ngày để xem dữ liệu:",
            options=sorted_dates,
            help="Chọn ngày để xem lại các hóa đơn đã xử lý"
        )

        if selected_date:
            selected_excel_file_path = available_logs[selected_date]

            st.markdown(f"**📄 Hiển thị dữ liệu từ:** `{selected_excel_file_path}`")

            if os.path.exists(selected_excel_file_path):
                df_main = pd.read_excel(selected_excel_file_path)
                st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                st.dataframe(df_main, use_container_width=True, height=300)
                st.markdown('</div>', unsafe_allow_html=True)

                with open(selected_excel_file_path, "rb") as file:
                    st.download_button(
                        label=f"📥 Tải xuống nhật ký {selected_date}",
                        data=file,
                        file_name=os.path.basename(selected_excel_file_path),
                        mime="application/vnd.ms-excel"
                    )
            else:
                st.markdown(
                    f'<div class="status-error">❌ Lỗi: Không tìm thấy file tại \'{selected_excel_file_path}\'</div>',
                    unsafe_allow_html=True)

# Manual Review Section
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown(
    """
    <div class="card">
        <div class="card-header">
            <div class="card-icon">⚠️</div>
            <h2 class="card-title">Hóa đơn cần xử lý thủ công</h2>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

review_file = "CanXuLyBangTay.xlsx"
if os.path.exists(review_file):
    df_review = pd.read_excel(review_file)
    st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
    st.dataframe(df_review, use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔄 Xóa danh sách xử lý thủ công", help="Thao tác này sẽ xóa file 'CanXuLyBangTay.xlsx'"):
            os.remove(review_file)
            st.rerun()
else:
    st.markdown('<div class="status-success">🎉 Hiện tại không có hóa đơn nào cần xử lý thủ công</div>',
                unsafe_allow_html=True)