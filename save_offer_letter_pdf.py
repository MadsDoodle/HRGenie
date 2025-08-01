import os
import re
from fpdf import FPDF

def save_offer_letter_pdf(offer_text: str, filename: str, output_dir: str = "generated_letters") -> str:
    """
    Save the offer letter text to a nicely formatted PDF using FPDF with bold headers and spacing.
    """
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    pdf = FPDF()
    pdf.add_page()

    # Register Unicode font
    font_path = "DejaVuSans.ttf"
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.add_font("DejaVu", "B", font_path, uni=True)

    # Title
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "Offer Letter – Company ABC", ln=True, align="C")
    pdf.ln(10)

    # Split offer_text into numbered sections using regex
    sections = re.split(r"(?=\n?\d+\.\s)", offer_text.strip(), flags=re.MULTILINE)

    line_height = 7
    max_width = 190

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Split section into header and body
        header_match = re.match(r"(\d+\.\s[^\n]+)", section)
        if header_match:
            header = header_match.group(1).strip()
            body = section[len(header):].strip()
        else:
            header = ""
            body = section

        # Bold header
        if header:
            pdf.set_font("DejaVu", "B", size=12)
            pdf.multi_cell(max_width, line_height, header)
            pdf.ln(1)

        # Regular body
        if body:
            pdf.set_font("DejaVu", "", size=11)
            pdf.multi_cell(max_width, line_height, body)
            pdf.ln(2)

        # Optional divider line
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

    pdf.output(filepath)
    return filepath
