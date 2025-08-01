from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# Add custom filter for formatting commas in salaries
def format_with_commas(value):
    return "{:,}".format(int(value))

def generate_offer_letter_jinja(emp: dict) -> str:
    env = Environment(loader=FileSystemLoader("templates"))
    env.filters["comma"] = format_with_commas

    template = env.get_template("offer_template.txt")
    today = datetime.today().strftime("%B %d, %Y")

    return template.render(
        today=today,
        name=emp["name"],
        team=emp["team"],
        band=emp["band"],
        base_salary=emp["base_salary"],
        performance_bonus=emp["performance_bonus"],
        retention_bonus=emp["retention_bonus"],
        ctc=emp["ctc"],
        location=emp["location"],
        joining_date=emp["joining_date"]
    )
