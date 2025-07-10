import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

def compound_amount(principal, months, interest_rate_monthly):
    return principal * ((1 + interest_rate_monthly) ** months)

def calculate_emi(principal, annual_rate, tenure_months):
    monthly_rate = annual_rate / 12
    emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
    return emi

def create_bar_chart(data, labels, title):
    fig, ax = plt.subplots()
    ax.bar(labels, data)
    ax.set_ylabel('Amount (₹)')
    ax.set_title(title)
    return fig

def generate_pdf_report(summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Loan Repayment Summary", ln=True, align='C')
    for label, value in summary.items():
        pdf.cell(200, 10, txt=f"{label}: INR {value:,.2f}", ln=True)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)


def main():
    st.title("Educational Loan Repayment Calculator")

    st.sidebar.header("Loan Inputs")
    loan1 = st.sidebar.number_input("Loan 1 Amount (in ₹)", value=2000000)
    loan2 = st.sidebar.number_input("Loan 2 Amount (in ₹)", value=1000000)
    loan2_time = st.sidebar.number_input("Loan 2 Disbursed After (Months)", value=12, min_value=0)
    interest_rate_annual = st.sidebar.number_input("Annual Interest Rate (%)", value=11.45) / 100
    moratorium_period = st.sidebar.number_input("Moratorium Period (Years)", value=3) * 12

    st.sidebar.subheader("Standard Tenures")
    emi_tenure_years = st.sidebar.number_input("8-Year Tenure (Years)", value=8)
    short_tenure_years = st.sidebar.number_input("2-Year Tenure (Years)", value=2)

    st.sidebar.subheader("Custom Tenures")
    custom_tenures = st.sidebar.text_input("Enter custom tenures in years (comma-separated)", value="5,10,15")
    custom_tenure_list = [int(y.strip()) for y in custom_tenures.split(",") if y.strip().isdigit()]

    interest_rate_monthly = interest_rate_annual / 12

    loan1_future = compound_amount(loan1, moratorium_period, interest_rate_monthly)
    loan2_future = compound_amount(loan2, moratorium_period - loan2_time, interest_rate_monthly)
    total_loan_future = loan1_future + loan2_future

    emi_8_years = calculate_emi(total_loan_future, interest_rate_annual, emi_tenure_years * 12)
    total_payment_8_years = emi_8_years * emi_tenure_years * 12

    emi_2_years = calculate_emi(total_loan_future, interest_rate_annual, short_tenure_years * 12)
    total_payment_2_years = emi_2_years * short_tenure_years * 12

    st.subheader("Loan Summary")
    st.write(f"Loan 1 Future Value: ₹{loan1_future:,.2f}")
    st.write(f"Loan 2 Future Value: ₹{loan2_future:,.2f}")
    st.write(f"Total Loan at Start of Repayment: ₹{total_loan_future:,.2f}")

    st.subheader("Repayment Over 8 Years")
    st.write(f"Monthly EMI: ₹{emi_8_years:,.2f}")
    st.write(f"Total Repayment: ₹{total_payment_8_years:,.2f}")

    st.subheader("Repayment Over 2 Years")
    st.write(f"Monthly EMI: ₹{emi_2_years:,.2f}")
    st.write(f"Total Repayment: ₹{total_payment_2_years:,.2f}")

    st.subheader("Custom Repayment Plans")
    custom_emis = []
    for tenure in custom_tenure_list:
        emi = calculate_emi(total_loan_future, interest_rate_annual, tenure * 12)
        total_payment = emi * tenure * 12
        custom_emis.append((tenure, emi, total_payment))
        st.write(f"Tenure: {tenure} Years | EMI: ₹{emi:,.2f} | Total Repayment: ₹{total_payment:,.2f}")

    # Chart data
    chart_data = [total_payment_8_years, total_payment_2_years] + [tp for _, _, tp in custom_emis]
    chart_labels = ["8-Year Plan", "2-Year Plan"] + [f"{t}-Year" for t, _, _ in custom_emis]
    fig = create_bar_chart(chart_data, chart_labels, "Total Repayment Comparison")
    st.pyplot(fig)

    # Generate downloadable PDF
    summary = {
        "Loan 1 Future Value": loan1_future,
        "Loan 2 Future Value": loan2_future,
        "Total Loan at Start of Repayment": total_loan_future,
        "Monthly EMI (8 Years)": emi_8_years,
        "Total Repayment (8 Years)": total_payment_8_years,
        "Monthly EMI (2 Years)": emi_2_years,
        "Total Repayment (2 Years)": total_payment_2_years
    }
    for tenure, emi, total in custom_emis:
        summary[f"Monthly EMI ({tenure} Years)"] = emi
        summary[f"Total Repayment ({tenure} Years)"] = total

    pdf = generate_pdf_report(summary)
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf,
        file_name="loan_summary_report.pdf",
        mime="application/pdf"
    )

if __name__ == '__main__':
    main()
