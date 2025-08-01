import json
from load_employee_metadata import load_employee_metadata
from fallback_jinja import generate_offer_letter_jinja
from fpdf import FPDF
import os

def save_offer_letter_pdf(offer_text: str, filename: str) -> str:
    """
    Converts plain offer letter text into a formatted PDF using Unicode font and saves it.
    Returns the output path.
    """
    class PDF(FPDF):
        pass

    pdf = PDF()
    pdf.add_page()

    # ✅ Use a Unicode font
    font_path = "DejaVuSans.ttf"
    if not os.path.exists(font_path):
        # Download DejaVuSans font if not present
        import urllib.request
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
        urllib.request.urlretrieve(url, font_path)

    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=12)

    # Add content
    for line in offer_text.split("\n"):
        # Safely wrap each line in case it contains wide characters
        try:
            pdf.multi_cell(w=180, h=10, txt=line, border=0)
        except Exception as e:
            print(f"⚠️ PDF rendering error on line: {line[:50]}... -> {e}")


    output_path = f"./{filename}"
    pdf.output(output_path)
    return output_path

def load_wfo_policy(team_name: str, policy_file: str = "wfo_policy.json") -> dict:
    with open(policy_file, "r") as file:
        wfo_data = json.load(file)
    # fallback if team not found
    return wfo_data.get(team_name, {
        "MinDays": "N/A",
        "SuggestedDays": "N/A",
        "RemoteNotes": "Please consult your manager for WFH guidelines."
    })

if __name__ == "__main__":
    emp_name = input("Enter employee name: ").strip()
    
    try:
        emp = load_employee_metadata(emp_name)
    except ValueError as e:
        print(e)
        exit(1)
    
    # Add WFO policy fields based on the team
    team_name = emp.get("team", "")
    wfo_policy = load_wfo_policy(team_name)

    emp["WFO_MinDays"] = wfo_policy["MinDays"]
    emp["WFO_SuggestedDays"] = wfo_policy["SuggestedDays"]
    emp["WFO_RemoteNotes"] = wfo_policy["RemoteNotes"]

    offer_letter = generate_offer_letter_jinja(emp)

    print("\n📄 Final Offer Letter:\n")
    print(offer_letter)
