import streamlit as st
from backend.generate_offer_withoutrag import generate_offer_letter
from backend.generate_offer_letter_nollm import (
    load_employee_metadata,
    generate_offer_letter_jinja,
    save_offer_letter_pdf
)

# 🔁 Import GPT fallback generator
from utils.save_offer_letter_pdf import save_offer_letter_pdf

import os

st.set_page_config(page_title="Offer Letter Generator", layout="centered")

st.title("📄 Offer Letter Generator – Company ABC")
st.markdown("Easily generate a formatted offer letter from internal HR data.")

# Session state for history
if "history" not in st.session_state:
    st.session_state.history = []

# Toggle mode
use_gpt = st.toggle("🤖 Use GPT-4o for generation", value=False)

# Input
employee_name = st.text_input("Enter Employee Name", placeholder="e.g. Julie Rodriguez")

if employee_name:
    try:
        emp_data = load_employee_metadata(employee_name)
        st.success(f"✅ Found employee: {emp_data['name']} in {emp_data['team']}")

        # Compensation table
        st.markdown("### 💰 Compensation Structure")
        comp_data = {
            "Base Salary (INR)": f"{int(emp_data['base_salary']):,}",
            "Performance Bonus (INR)": f"{int(emp_data['performance_bonus']):,}",
            "Retention Bonus (INR)": f"{int(emp_data['retention_bonus']):,}",
            "Total CTC (INR)": f"{int(emp_data['ctc']):,}"
        }
        st.table(comp_data)

        # Resume preview (placeholder)
        with st.expander("📎 Preview Resume (mock content)"):
            st.write(f"**Name:** {emp_data['name']}")
            st.write(f"**Department:** {emp_data['team']}")
            st.write("Welcome to the Company")

        # Offer letter: GPT or Jinja
        if use_gpt:
            st.markdown("### 🤖 Generated Offer Letter (GPT-4o)")
            offer_text = generate_offer_letter(employee_name)
        else:
            st.markdown("### 📄 Generated Offer Letter (Template)")
            offer_text = generate_offer_letter_jinja(emp_data)

        st.code(offer_text, language="markdown")

        # Save to PDF and allow download
        filename = f"{emp_data['name'].replace(' ', '_')}_Offer_Letter.pdf"
        pdf_path = save_offer_letter_pdf(offer_text, filename)

        with open(pdf_path, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name=filename)

        # Save history
        st.session_state.history.append({
            "name": emp_data["name"],
            "team": emp_data["team"],
            "joining": emp_data["joining_date"],
            "file": filename
        })

    except Exception as e:
        st.error(f"❌ {str(e)}")

# History viewer
if st.session_state.history:
    st.markdown("---")
    st.markdown("### 🕘 Generation History")
    for item in reversed(st.session_state.history[-5:]):
        st.markdown(f"- **{item['name']}** – {item['team']} (Joining: {item['joining']}) – 📄 *{item['file']}*")
