import streamlit as st
from generate_offer_letter import generate_offer_letter
from fallback_jinja import generate_offer_letter_jinja
from load_employee_metadata import load_employee_metadata
from retriever import retrieve_relevant_chunks
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
import os
import openai

# Load API key from secrets.toml
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ---------------------- Page Config ---------------------- #
st.set_page_config(page_title="HR Genie", layout="centered")
st.title("💼 AI HR Offer Letter Generator")

# ------------------ Session State Init ------------------- #
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Stores tuples of (sender, message)

# --------------------- Chat Renderer --------------------- #
st.markdown("### 💬 Chat History")
for sender, message in st.session_state.chat_history:
    with st.chat_message(sender):
        st.markdown(message)

# --------------------- Input Section --------------------- #
employee_name = st.text_input("Enter employee name")
use_jinja = st.toggle("Fallback to Jinja2 if GPT fails", value=False)

if st.button("🚀 Generate Offer Letter"):
    if not employee_name.strip():
        st.warning("⚠️ Please enter an employee name.")
    else:
        st.session_state.chat_history.append(("user", employee_name))
        try:
            if use_jinja:
                emp = load_employee_metadata(employee_name)
                chunks = retrieve_relevant_chunks(
                    f"Generate offer letter for {employee_name}", top_k=5
                )
                result = generate_offer_letter_jinja(emp, chunks)
                source = "Jinja2 fallback"
            else:
                result = generate_offer_letter(employee_name)
                source = "GPT-4"

            st.session_state.chat_history.append(("assistant", result))
            st.success(f"✅ Offer Letter Generated using {source}")

            # Render latest assistant message
            with st.chat_message("assistant"):
                st.markdown(result)

            # Create downloadable PDF
            buffer = BytesIO()
            c = canvas.Canvas(buffer)
            lines = result.split('\n')
            y = 800
            for line in lines:
                c.drawString(40, y, line)
                y -= 15
            c.save()
            buffer.seek(0)

            filename = f"{employee_name.replace(' ', '_')}_Offer_Letter.pdf"
            st.download_button("📄 Download Offer Letter as PDF", data=buffer, file_name=filename)

        except Exception as e:
            st.session_state.chat_history.append(("assistant", f"❌ Failed: {str(e)}"))
            st.error(f"❌ Failed: {str(e)}")

# ---------------------- Reset Button ---------------------- #
if st.button("🗑️ Clear Chat History"):
    st.session_state.chat_history = []
    st.experimental_rerun()

#run using "python -m streamlit run streamlit_app.py"
