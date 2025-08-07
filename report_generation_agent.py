# File: report_generation_agent.py (Nâng cấp 1)
import pandas as pd
from utils import get_local_llm_client
from config import MODEL_NAME
import matplotlib.pyplot as plt

def generate_financial_report(df: pd.DataFrame) -> str:
    if df.empty:
        return "No data available to generate a report."

    # --- PHÂN TÍCH CHUYÊN SÂU BẰNG PANDAS ---
    total_spending = df['total_amount'].sum()
    invoice_count = len(df)
    avg_transaction_value = df['total_amount'].mean()
    highest_transaction = df.loc[df['total_amount'].idxmax()]
    spending_by_category = df.groupby('category')['total_amount'].sum().sort_values(ascending=False)
    top_company_spending = df.groupby('company')['total_amount'].sum().sort_values(ascending=False).head(3)

    # --- TẠO PROMPT VỚI DỮ LIỆU PHONG PHÚ HƠN ---
    prompt = f"""
    You are an expert financial analyst AI. Your task is to write a concise and insightful summary based on the provided financial data for a period.

    **Key Financial Metrics:**
    - Total Invoices Processed: {invoice_count}
    - Total Spending: {total_spending:,.2f}
    - Average Transaction Value: {avg_transaction_value:,.2f}
    - Highest Single Transaction: {highest_transaction['total_amount']:,.2f} from '{highest_transaction['company']}' in category '{highest_transaction['category']}'.

    **Spending by Category:**
    {spending_by_category.to_string()}

    **Top 3 Companies by Spending:**
    {top_company_spending.to_string()}

    **Task:**
    Write a professional report covering the following points:
    1. Provide a general overview of the financial activity.
    2. Identify the most significant spending category and offer a brief analysis.
    3. Point out any notable data points, such as the highest transaction or top vendors.
    4. Conclude with a potential insight or observation.

    Keep the report clear, concise, and data-driven.
    """

    try:
        client = get_local_llm_client()
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        report_text = response.choices[0].message.content
        return report_text
    except Exception as e:
        print(f"❌ Error during report generation: {e}")
        return "Failed to generate the report due to an internal error."

def create_spending_chart(df: pd.DataFrame):
    """Tạo biểu đồ cột thể hiện chi tiêu theo hạng mục."""
    if df.empty:
        return None

    spending_by_category = df.groupby('category')['total_amount'].sum().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    spending_by_category.plot(kind='barh', ax=ax, color='#667eea')

    ax.set_title('Total Spending by Category', fontsize=16)
    ax.set_xlabel('Total Amount', fontsize=12)
    ax.set_ylabel('Category', fontsize=12)

    # Thêm format cho đẹp hơn
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', linestyle='--', alpha=0.7)

    return fig