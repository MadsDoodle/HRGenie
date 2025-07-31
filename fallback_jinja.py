from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# Setup Jinja2
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("offerletter_template.txt")

def generate_offer_letter_jinja(emp: dict, chunks: list) -> str:
    def extract_section(chunks, keyword):
        for c in chunks:
            if keyword.lower() in c.lower():
                return c.strip()
        return "Policy not available."

    leave = extract_section(chunks, "leave")
    wfo = extract_section(chunks, "work from office")
    travel = extract_section(chunks, "travel")


    return template.render(
        date=datetime.today().strftime("%B %d, %Y"),
        name=emp['name'],
        
        band=emp['band'],
        
        location=emp['location'],
        joining_date=emp['joining_date'],
        fixed_salary=emp['base_salary'],
        performance_bonus=emp['performance_bonus'],
        retention_bonus=emp['retention_bonus'],
        ctc=emp['ctc'],
        leave_policy=leave,
        wfo_policy=wfo,
        travel_policy=travel
    )
