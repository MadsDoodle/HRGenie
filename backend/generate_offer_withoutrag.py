import os
import openai
from datetime import datetime
from dotenv import load_dotenv
from utils.load_employee_metadata import load_employee_metadata
from backend.fallback_jinja import generate_offer_letter_jinja  # Fallback generator

# Load API key
load_dotenv()

# For Streamlit deployment
import streamlit as st
openai.api_key = st.secrets["OPENAI_API_KEY"]

print("🔐 OpenAI key loaded:", "OPENAI_API_KEY" in st.secrets)

def generate_offer_letter(emp_name: str) -> str:
    try:
        print(f"📥 Fetching metadata for: {emp_name}")
        emp = load_employee_metadata(emp_name)
        today = datetime.today().strftime("%B %d, %Y")

        # Format the strict GPT prompt
        prompt = f"""
You are an expert HR assistant at Company ABC. You are to generate an offer letter strictly based on the provided employee data. 
❗You MUST NOT modify, guess, or hallucinate any of the following values: name, team, location, dates, or salary components.

==================== 📄 EMPLOYEE DATA ====================

- Date: {today}
- Candidate Name: {emp['name']}
- Band Level: {emp['band']}
- Department: {emp['team']}
- Location: {emp['location']}
- Joining Date: {emp['joining_date']}
- Base Salary (INR): {emp['base_salary']:,}
- Performance Bonus (INR): {emp['performance_bonus']:,}
- Retention Bonus (INR): {emp['retention_bonus']:,}
- Total CTC (INR): {emp['ctc']:,}

==================== ✅ TASK ====================

Generate a formal offer letter that includes:
- Formal tone and structure
- 8 standard sections (Appointment, Compensation, Leave, WFO, Travel, IP Clause, Exit, Next Steps)
- A tabular format for the compensation section with the exact figures given above
- No assumptions or made-up content. Use only what is given.

⚠️ Do NOT change candidate name, department, or salary numbers.
⚠️ Output only the final formatted offer letter. No explanation, pre-text, or bullet summary.

==================== 📄 SAMPLE STRUCTURE ====================

📄 Offer Letter – Company ABC  
Date: {today}  
Candidate Name: {emp['name']}  
Position: Software Engineer  
Band Level: {emp['band']}  
Location: {emp['location']}  
Joining Date: {emp['joining_date']}  

1. 🎯 Appointment Details  
We are delighted to offer you the position of Software Engineer in the {emp['team']} team at Company ABC. 
This is a full-time role based out of our {emp['location']} office. Your employment will be governed by the terms outlined in this letter and the Employee Handbook.

2. 💰 Compensation Structure  

| Compensation Component      | Amount (INR)      |
|-----------------------------|-------------------|
| Base Salary                 | {emp['base_salary']:,}      |
| Performance Bonus           | {emp['performance_bonus']:,}        |
| Retention Bonus             | {emp['retention_bonus']:,}         |
| Total CTC                   | {emp['ctc']:,}      |

Performance bonuses are disbursed quarterly, subject to performance evaluation.

3. 🏖 Leave Entitlements (Band {emp['band']})  
You are entitled to 18 days of paid leave annually:
● Earned Leave: 10 days  
● Sick Leave: 6 days  
● Casual Leave: 2 days  

Leave resets each January. Carry-forward is allowed up to 10 days.

4. 🏢 Work From Office Policy ({emp['team']} Team)  
You are expected to follow a hybrid working model with a minimum of 3 days/week in office 
(suggested: Monday, Tuesday, Thursday).  
● Rs. 1,000/month internet reimbursement  
● Rs. 5,000 one-time home-office setup support  

5. ✈ Travel Policy (Band {emp['band']})  
● Domestic Travel: Economy class  
● International Travel: Allowed for conferences/client meetings  
● Hotel Cap: Rs. 4,000/night  
● Per Diem: Rs. 3,000/day (domestic), USD 60/day (international)  

6. 🔒 Confidentiality & IP Clause  
All work products created during employment remain the IP of Company ABC. A separate NDA will follow.

7. 🚨 Termination & Exit  
● 60 days notice by either party  
● 15 days notice during probation  
● All company assets must be returned on exit  

8. ✅ Next Steps  
Please sign and return via DocuSign within 5 working days. Your onboarding contact will be in touch.

Warm regards,  
Aarti Nair  
HR Business Partner  
Company ABC  
📧 peopleops@companyabc.com  
🌐 www.companyabc.com
"""

        # GPT call
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict HR assistant at Company ABC. Never modify employee data. You generate formal offer letters ONLY using the input metadata. Do NOT hallucinate or assume anything."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            timeout=40
        )

        gpt_output = response.choices[0].message.content.strip()

        # Final sanity check to prevent hallucination
        if emp["name"].lower() not in gpt_output.lower():
            raise ValueError("⚠️ GPT output does not contain correct employee name.")

        print("✅ Offer letter generated by GPT.")
        return gpt_output

    except Exception as e:
        print(f"⚠️ GPT failed ({e}). Falling back to Jinja2 template...")
        emp = load_employee_metadata(emp_name)
        return generate_offer_letter_jinja(emp)

# CLI run
if __name__ == "__main__":
    emp_name = input("Enter employee name: ").strip()
    letter = generate_offer_letter(emp_name)
    print("\n📄 Final Offer Letter:\n")
    print(letter)
