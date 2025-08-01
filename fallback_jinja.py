from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# Add custom filter for formatting commas in salaries
def format_with_commas(value):
    return "{:,}".format(int(value))

# Title mapping by team
TITLE_BY_TEAM = {
    "Engineering": "Software Engineer",
    "Sales": "Sales Executive",
    "HR": "HR Specialist",
    "Finance": "Financial Analyst",
    "Ops/Support": "Operations Associate",
    "Design": "Product Designer",
    "Marketing": "Marketing Associate"
}

# WFO policy mapping by team
WFO_POLICY_BY_TEAM = {
    "Engineering": {
        "MinDays": "3/week",
        "SuggestedDays": "Mon, Tue, Thu",
        "RemoteNotes": "Sprint reviews must be in-office"
    },
    "Sales": {
        "MinDays": "4–5/week",
        "SuggestedDays": "Field visits + office",
        "RemoteNotes": "Remote only with RSM approval"
    },
    "HR": {
        "MinDays": "4/week",
        "SuggestedDays": "Mon–Thu",
        "RemoteNotes": "In-office mandatory during onboarding"
    },
    "Finance": {
        "MinDays": "3/week",
        "SuggestedDays": "Tue, Wed, Fri",
        "RemoteNotes": "Fully in-office during month-end"
    },
    "Ops/Support": {
        "MinDays": "5/week",
        "SuggestedDays": "All weekdays",
        "RemoteNotes": "WFH not permitted except in emergencies"
    }
}

def generate_offer_letter_jinja(emp: dict) -> str:
    env = Environment(loader=FileSystemLoader("templates"))
    env.filters["comma"] = format_with_commas

    template = env.get_template("offer_template.txt")
    today = datetime.today().strftime("%B %d, %Y")

    team = emp.get("team", "")
    
    # Fetch title from mapping
    title = TITLE_BY_TEAM.get(team, "Team Member")

    # Get WFO policy
    wfo_policy = WFO_POLICY_BY_TEAM.get(team, {
        "MinDays": "N/A",
        "SuggestedDays": "N/A",
        "RemoteNotes": "N/A"
    })

    return template.render(
        today=today,
        name=emp["name"],
        team=emp["team"],
        title=title,  # ✅ Pass title to template
        band=emp["band"],
        base_salary=emp["base_salary"],
        performance_bonus=emp["performance_bonus"],
        retention_bonus=emp["retention_bonus"],
        ctc=emp["ctc"],
        location=emp["location"],
        joining_date=emp["joining_date"],
        WFO_MinDays=wfo_policy["MinDays"],
        WFO_SuggestedDays=wfo_policy["SuggestedDays"],
        WFO_RemoteNotes=wfo_policy["RemoteNotes"]
    )
