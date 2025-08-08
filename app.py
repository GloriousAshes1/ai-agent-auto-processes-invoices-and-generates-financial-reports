import streamlit as st
from invoice_processor_agent import InvoiceProcessorAgent
from data_aggregation_module import aggregate_logs
from report_generation_agent import generate_financial_report, create_spending_chart
from config import BASE_LOG_DIR, LOG_SHEET_NAME
import os
import pandas as pd
from PIL import Image
from datetime import datetime
from utils import find_available_logs
import shutil
from io import BytesIO

# Global variables
temp_dir = "temp_uploads"
save_invoice_dir = os.path.join("uploaded_invoices", f"invoices_{datetime.now().strftime('%d-%m-%Y')}")
os.makedirs(save_invoice_dir, exist_ok=True)

# Accounting Logs Directory
today_str = datetime.now().strftime("%d-%m-%Y")
accounting_log_dir = os.path.join(BASE_LOG_DIR, datetime.now().strftime("%Y"), f"Month_{datetime.now().strftime('%m')}")
os.makedirs(accounting_log_dir, exist_ok=True)

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

@st.cache_data
def get_available_logs_map():
    return find_available_logs()

agent = load_agent()

# --- Enhanced CSS Styling ---
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
        padding: 40px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 30px;
        color: white;
        position: relative;
        overflow: hidden;
    }

    .hero-title {
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 10px;
        text-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    .card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,249,255,0.95) 100%);
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
        border: 1px solid rgba(102, 126, 234, 0.1);
        margin-bottom: 25px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        backdrop-filter: blur(10px);
    }

    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.2);
    }

    .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 2px solid #f8f9fa;
    }

    .card-icon {
        font-size: 1.8em;
        margin-right: 15px;
        padding: 10px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .card-title {
        font-size: 1.3em;
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
        padding: 10px 20px;
        font-size: 0.95em;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(86, 171, 47, 0.4);
        width: 100%;
    }

    .stDownloadButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(86, 171, 47, 0.6);
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

    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 25px 0;
        gap: 15px;
    }

    .stat-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,249,255,0.9) 100%);
        padding: 20px;
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
        font-size: 2em;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 8px;
    }

    .stat-label {
        font-size: 0.9em;
        font-weight: 500;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .sidebar-section {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,249,255,0.95) 100%);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.05);
    }

    .divider {
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, rgba(102, 126, 234, 0.3) 20%, #667eea 50%, rgba(102, 126, 234, 0.3) 80%, transparent 100%);
        margin: 30px 0;
        border: none;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,249,255,0.9) 100%);
        border-radius: 12px;
        color: #495057;
        font-weight: 500;
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar ---
with st.sidebar:
    st.markdown(
        """
        <div class="hero-section">
            <div class="hero-title">🤖 AI Assistant</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Quick Stats
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### 📊 Quick Stats")

    # Count available logs
    available_logs = find_available_logs()
    total_logs = len(available_logs)

    # Count files in review
    review_count = 0
    if os.path.exists(agent.action_agent.review_file_path):
        df_review = pd.read_excel(agent.action_agent.review_file_path)
        review_count = len(df_review)

    # Count today's invoices
    today_invoices = len(
        [f for f in os.listdir(save_invoice_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]) if os.path.exists(
        save_invoice_dir) else 0

    st.metric("📄 Available Logs", total_logs)
    st.metric("⚠️ Review Required", review_count)
    st.metric("📸 Today's Invoices", today_invoices)
    st.markdown('</div>', unsafe_allow_html=True)

    # Quick Actions
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### ⚡ Quick Actions")

    if st.button("🔄 Refresh Data", help="Refresh all cached data"):
        st.cache_resource.clear()
        st.rerun()

    if st.button("📂 Open Invoice Folder", help="View today's invoice folder"):
        st.info(f"Invoice folder: `{save_invoice_dir}`")

    if review_count > 0:
        if st.button("🗑️ Clear Review Queue", help="Clear all items in review queue"):
            if os.path.exists(agent.action_agent.review_file_path):
                os.remove(agent.action_agent.review_file_path)
                st.success("Review queue cleared!")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # System Info
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### ℹ️ System Info")
    st.caption(f"**Date:** {datetime.now().strftime('%d/%m/%Y')}")
    st.caption(f"**Log Dir:** `{accounting_log_dir}`")
    st.caption(f"**Agent Status:** {'✅ Ready' if agent else '❌ Error'}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main Content ---
st.markdown(
    """
    <div class="hero-section">
        <div class="hero-title">🤖 AI Accounting Assistant</div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Tab Navigation ---
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Process", "📋 View Logs", "📊 Financial Reports", "⚠️ Manual Review"])

# --- TAB 1: Upload & Process ---
with tab1:
    st.markdown(
        """
        <div class="card">
            <div class="card-header">
                <div class="card-icon">📤</div>
                <h2 class="card-title">Upload & Process Invoices</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_files = st.file_uploader(
            "📁 Select invoice images to process",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            help="Supported formats: PNG, JPG, JPEG • Max 200MB per file"
        )

        if uploaded_files:
            # File statistics
            st.markdown(
                f"""
                <div class="stats-container">
                    <div class="stat-card">
                        <div class="stat-number">{len(uploaded_files)}</div>
                        <div class="stat-label">Selected Files</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{sum(f.size for f in uploaded_files) / 1024 / 1024:.1f}</div>
                        <div class="stat-label">Total MB</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(f"🚀 Process {len(uploaded_files)} invoices", type="primary", key="process_btn"):
                valid_results = []
                review_results = []

                progress_bar = st.progress(0, text="Starting processing...")

                for i, uploaded_file in enumerate(uploaded_files):
                    progress_text = f"Processing: **{uploaded_file.name}** ({i + 1}/{len(uploaded_files)})"
                    progress_bar.progress((i + 1) / len(uploaded_files), text=progress_text)

                    with st.expander(f"📋 Processing: **{uploaded_file.name}**", expanded=False):
                        col_img, col_result = st.columns([1, 2])

                        with col_img:
                            st.image(Image.open(uploaded_file), caption=uploaded_file.name, use_container_width=True)

                        with col_result:
                            # Process file
                            if not os.path.exists(temp_dir):
                                os.makedirs(temp_dir)

                            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                            with open(temp_file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())

                            # Run agent processing
                            result = agent.run(temp_file_path)

                            if result:
                                # Save processed invoice
                                final_image_path = os.path.join(save_invoice_dir, uploaded_file.name)
                                try:
                                    shutil.copy(temp_file_path, final_image_path)
                                    st.caption(f"💾 Saved to: `{final_image_path}`")
                                except Exception as e:
                                    st.markdown(f'<div class="status-warning">⚠️ Save error: {e}</div>',
                                                unsafe_allow_html=True)

                                result['invoice_path'] = final_image_path

                                # Validate result
                                if agent.action_agent.is_record_valid(result):
                                    st.markdown('<div class="status-success">✅ Valid Invoice</div>',
                                                unsafe_allow_html=True)
                                    valid_results.append(result)
                                else:
                                    st.markdown('<div class="status-warning">⚠️ Requires Review</div>',
                                                unsafe_allow_html=True)
                                    review_results.append(result)

                                # Display extracted data
                                with st.expander("📋 Extracted Data", expanded=False):
                                    st.json(result)
                            else:
                                st.markdown('<div class="status-error">❌ Processing failed</div>',
                                            unsafe_allow_html=True)

                            # Clean up temp file
                            if os.path.exists(temp_file_path):
                                os.remove(temp_file_path)

                # Processing Summary
                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                st.markdown("### 📊 Processing Summary")

                st.markdown(
                    f"""
                    <div class="stats-container">
                        <div class="stat-card">
                            <div class="stat-number">{len(valid_results)}</div>
                            <div class="stat-label">Valid Invoices</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{len(review_results)}</div>
                            <div class="stat-label">Need Review</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{len(uploaded_files)}</div>
                            <div class="stat-label">Total Processed</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Save results
                if valid_results:
                    excel_path_today = os.path.join(accounting_log_dir, f"AccountingLog_{today_str}.xlsx")
                    agent.action_agent.save_to_excel(valid_results, excel_path_today, LOG_SHEET_NAME)
                    st.markdown(f'<div class="status-success">🎉 Saved {len(valid_results)} valid invoices to log</div>',
                                unsafe_allow_html=True)

                if review_results:
                    agent.action_agent.save_to_excel(review_results, agent.action_agent.review_file_path, 'CanXuLy')
                    st.markdown(
                        f'<div class="status-warning">⚠️ {len(review_results)} invoices moved to review queue</div>',
                        unsafe_allow_html=True)

                if valid_results or review_results:
                    st.balloons()

    with col2:
        st.markdown(
            """
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">💡</div>
                    <h2 class="card-title">Tips</h2>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("""
        **📸 Image Quality Tips:**
        - Use clear, well-lit photos
        - Ensure text is readable
        - Avoid shadows and glare
        - Keep invoice flat and straight

        **🔄 Processing Notes:**
        - Valid invoices are automatically saved
        - Problematic invoices go to review queue
        - All originals are preserved
        - Processing is done in parallel
        """)

# --- TAB 2: View Logs ---
with tab2:
    st.markdown(
        """
        <div class="card">
            <div class="card-header">
                <div class="card-icon">📋</div>
                <h2 class="card-title">Accounting Logs</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not available_logs:
        st.markdown('<div class="status-info">📂 No accounting logs found</div>', unsafe_allow_html=True)
    else:
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            sorted_dates = sorted(available_logs.keys(), reverse=True)
            selected_date = st.selectbox(
                "📅 Select date to view:",
                options=sorted_dates,
                help="Choose a date to view the corresponding log"
            )

        if selected_date:
            selected_excel_file_path = available_logs[selected_date]

            with col2:
                st.metric("📄 Selected Date", selected_date)

            with col3:
                if os.path.exists(selected_excel_file_path):
                    file_size = os.path.getsize(selected_excel_file_path) / 1024
                    st.metric("📊 File Size", f"{file_size:.1f} KB")

            if os.path.exists(selected_excel_file_path):
                df_main = pd.read_excel(selected_excel_file_path)

                # Display data preview
                st.markdown(f"**📄 Data from:** `{os.path.basename(selected_excel_file_path)}`")
                st.dataframe(df_main, use_container_width=True, height=400)

                # Summary statistics
                if not df_main.empty:
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("📊 Total Records", len(df_main))

                    with col2:
                        if 'Tong_tien' in df_main.columns:
                            total_amount = df_main['Tong_tien'].sum() if pd.api.types.is_numeric_dtype(
                                df_main['Tong_tien']) else 0
                            st.metric("💰 Total Amount", f"{total_amount:,.0f}")

                    with col3:
                        if 'Ten_cong_ty' in df_main.columns:
                            unique_companies = df_main['Ten_cong_ty'].nunique()
                            st.metric("🏢 Companies", unique_companies)

                    with col4:
                        if 'Ngay_hoa_don' in df_main.columns:
                            date_range = df_main['Ngay_hoa_don'].nunique()
                            st.metric("📅 Date Range", date_range)

                # Download options
                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                col1, col2 = st.columns(2)

                with col1:
                    # Download Excel
                    with open(selected_excel_file_path, "rb") as file:
                        excel_data = file.read()
                    st.download_button(
                        label="📥 Download Excel",
                        data=excel_data,
                        file_name=f"AccountingLog_{selected_date}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_excel_log"
                    )

                with col2:
                    # Download CSV from memory
                    csv_buffer = BytesIO()
                    df_main.to_csv(csv_buffer, index=False, encoding='utf-8')
                    csv_data = csv_buffer.getvalue()

                    st.download_button(
                        label="📄 Download CSV",
                        data=csv_data,
                        file_name=f"AccountingLog_{selected_date}.csv",
                        mime="text/csv",
                        key="download_csv_log"
                    )
            else:
                st.markdown(f'<div class="status-error">❌ File not found: {selected_excel_file_path}</div>',
                            unsafe_allow_html=True)

# --- TAB 3: Financial Reports ---
with tab3:
    st.markdown(
        """
        <div class="card">
            <div class="card-header">
                <div class="card-icon">📊</div>
                <h2 class="card-title">Financial Reports</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Year and Month selection
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        available_years = sorted(os.listdir(BASE_LOG_DIR), reverse=True) if os.path.exists(BASE_LOG_DIR) else []
        selected_year = st.selectbox("📅 Select Year:", options=available_years, key="report_year")

    if selected_year:
        months_in_year_dir = os.path.join(BASE_LOG_DIR, selected_year)
        if os.path.exists(months_in_year_dir):
            available_months = sorted([d.split('_')[1] for d in os.listdir(months_in_year_dir) if "Month_" in d],
                                      reverse=True)

            with col2:
                selected_month = st.selectbox("📅 Select Month:", options=available_months, key="report_month")

            with col3:
                if selected_month:
                    st.metric("📊 Report Period", f"{selected_month}/{selected_year}")

            if selected_month and st.button("📊 Generate Report", type="primary", key="generate_report"):
                with st.spinner(f"Generating report for {selected_month}/{selected_year}..."):
                    aggregated_data = aggregate_logs(selected_year, selected_month)

                    if not aggregated_data.empty:
                        # Generate report content
                        report_content = generate_financial_report(aggregated_data)

                        # Display report
                        st.markdown('<hr class="divider">', unsafe_allow_html=True)
                        st.markdown(f"### 📊 Financial Summary for {selected_month}/{selected_year}")
                        st.markdown(report_content)

                        # Generate and display chart
                        report_chart = create_spending_chart(aggregated_data)
                        if report_chart:
                            st.markdown("### 📈 Spending Distribution")
                            st.pyplot(report_chart, use_container_width=True)

                        # Download options for report
                        st.markdown('<hr class="divider">', unsafe_allow_html=True)
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            # Download aggregated data as Excel
                            excel_buffer = BytesIO()
                            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                                aggregated_data.to_excel(writer, sheet_name='Report_Data', index=False)
                            excel_data = excel_buffer.getvalue()

                            st.download_button(
                                label="📥 Download Data (Excel)",
                                data=excel_data,
                                file_name=f"FinancialReport_{selected_month}_{selected_year}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key="download_report_excel"
                            )

                        with col2:
                            # Download as CSV
                            csv_buffer = BytesIO()
                            aggregated_data.to_csv(csv_buffer, index=False, encoding='utf-8')
                            csv_data = csv_buffer.getvalue()

                            st.download_button(
                                label="📄 Download Data (CSV)",
                                data=csv_data,
                                file_name=f"FinancialReport_{selected_month}_{selected_year}.csv",
                                mime="text/csv",
                                key="download_report_csv"
                            )

                        with col3:
                            # Download report text
                            report_text = f"Financial Report for {selected_month}/{selected_year}\n\n{report_content}"
                            st.download_button(
                                label="📝 Download Report (TXT)",
                                data=report_text.encode('utf-8'),
                                file_name=f"FinancialReport_{selected_month}_{selected_year}.txt",
                                mime="text/plain",
                                key="download_report_text"
                            )

                        # Summary statistics
                        st.markdown('<hr class="divider">', unsafe_allow_html=True)
                        st.markdown("### 📈 Key Metrics")

                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            total_records = len(aggregated_data)
                            st.metric("📊 Total Records", total_records)

                        with col2:
                            if 'Tong_tien' in aggregated_data.columns:
                                total_amount = aggregated_data['Tong_tien'].sum() if pd.api.types.is_numeric_dtype(
                                    aggregated_data['Tong_tien']) else 0
                                st.metric("💰 Total Amount", f"{total_amount:,.0f}")

                        with col3:
                            if 'Ten_cong_ty' in aggregated_data.columns:
                                unique_companies = aggregated_data['Ten_cong_ty'].nunique()
                                st.metric("🏢 Companies", unique_companies)

                        with col4:
                            if 'Tong_tien' in aggregated_data.columns and total_records > 0:
                                avg_amount = aggregated_data['Tong_tien'].mean() if pd.api.types.is_numeric_dtype(
                                    aggregated_data['Tong_tien']) else 0
                                st.metric("📊 Avg Amount", f"{avg_amount:,.0f}")

                    else:
                        st.markdown(
                            f'<div class="status-warning">⚠️ No data found for {selected_month}/{selected_year}</div>',
                            unsafe_allow_html=True)

# --- TAB 4: Manual Review ---
with tab4:
    st.markdown(
        """
        <div class="card">
            <div class="card-header">
                <div class="card-icon">⚠️</div>
                <h2 class="card-title">Manual Review Queue</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if os.path.exists(agent.action_agent.review_file_path):
        df_review = pd.read_excel(agent.action_agent.review_file_path)

        if not df_review.empty:
            # Review statistics
            st.markdown(
                f"""
                <div class="stats-container">
                    <div class="stat-card">
                        <div class="stat-number">{len(df_review)}</div>
                        <div class="stat-label">Items in Queue</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{df_review['Tong_tien'].sum() if 'Tong_tien' in df_review.columns and pd.api.types.is_numeric_dtype(df_review['Tong_tien']) else 0:,.0f}</div>
                        <div class="stat-label">Total Value</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{df_review['Ten_cong_ty'].nunique() if 'Ten_cong_ty' in df_review.columns else 0}</div>
                        <div class="stat-label">Companies</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Display review data
            st.markdown("### 📋 Items Requiring Review")
            st.dataframe(df_review, use_container_width=True, height=400)

            # Review actions
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)

            with col1:
                # Download review data as Excel
                with open(agent.action_agent.review_file_path, "rb") as file:
                    excel_data = file.read()
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name="ManualReview.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_review_excel"
                )

            with col2:
                # Download as CSV from memory
                csv_buffer = BytesIO()
                df_review.to_csv(csv_buffer, index=False, encoding='utf-8')
                csv_data = csv_buffer.getvalue()

                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name="ManualReview.csv",
                    mime="text/csv",
                    key="download_review_csv"
                )

            with col3:
                if st.button("🗑️ Clear Review Queue", help="Remove all items from review queue", key="clear_review"):
                    os.remove(agent.action_agent.review_file_path)
                    st.success("Review queue cleared!")
                    st.rerun()

            # Individual item actions
            if len(df_review) > 0:
                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                st.markdown("### 🔍 Review Individual Items")

                # Select item to review
                selected_index = st.selectbox(
                    "Select item to review:",
                    options=range(len(df_review)),
                    format_func=lambda
                        x: f"Row {x + 1}: {df_review.iloc[x]['Ten_cong_ty'] if 'Ten_cong_ty' in df_review.columns else 'Unknown'} - {df_review.iloc[x]['Tong_tien'] if 'Tong_tien' in df_review.columns else 'N/A'}"
                )

                if selected_index is not None:
                    selected_item = df_review.iloc[selected_index]

                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.markdown("**📋 Item Details:**")
                        for col, val in selected_item.items():
                            st.text(f"{col}: {val}")

                    with col2:
                        st.markdown("**🖼️ Invoice Image:**")
                        if 'invoice_path' in selected_item and pd.notna(selected_item['invoice_path']):
                            invoice_path = selected_item['invoice_path']
                            if os.path.exists(invoice_path):
                                image = Image.open(invoice_path)
                                st.image(image, caption="Invoice Image", use_container_width=True)
                            else:
                                st.warning("Invoice image not found")
                        else:
                            st.info("No image path available")

        else:
            st.markdown('<div class="status-success">🎉 Review queue is empty!</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-success">🎉 No items in review queue</div>', unsafe_allow_html=True)

    # Review Guidelines
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="card">
            <div class="card-header">
                <div class="card-icon">💡</div>
                <h2 class="card-title">Review Guidelines</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    **Common Issues to Check:**
    - **Missing Information:** Company name, amount, or date not extracted
    - **Incorrect OCR:** Text recognition errors in key fields
    - **Format Issues:** Unusual invoice layouts or foreign languages
    - **Amount Validation:** Suspicious or unusually high/low amounts

    **Actions You Can Take:**
    1. **Download** the data to Excel/CSV for manual editing
    2. **Clear** individual items after manual processing
    3. **Re-upload** corrected invoices through the Upload tab
    4. **Contact Admin** for persistent extraction issues
    """)

# --- Footer ---
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align: center; padding: 20px; color: #6c757d;">
        <p>🤖 AI Accounting Assistant | Built with Streamlit | 
        <span style="color: #667eea;">Enhanced with Sidebar & Tabs</span></p>
    </div>
    """,
    unsafe_allow_html=True
)