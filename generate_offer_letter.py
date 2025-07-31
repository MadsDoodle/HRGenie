import os
import openai
from dotenv import load_dotenv
from datetime import datetime
from retriever import retrieve_relevant_chunks
from load_employee_metadata import load_employee_metadata
from fallback_jinja import generate_offer_letter_jinja  # 👈 fallback

# Load OpenAI key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_offer_letter(emp_name: str) -> str:
    try:
        # Load metadata and vector chunks
        emp = load_employee_metadata(emp_name)
        chunks = retrieve_relevant_chunks(f"Generate offer letter for {emp_name} with policies", top_k=5)
        context = "\n\n".join(chunks)
        today = datetime.today().strftime("%B %d, %Y")

        # GPT prompt
        prompt = f"""
You are an HR assistant at Company ABC. Your task is to generate a formal offer letter
in the same structure and tone as the example provided below. Be sure to include a 
tabular compensation structure just like in the example.

==================== 📄 SAMPLE OFFER LETTER FORMAT ====================

📄 Offer Letter – Company ABC 
Date: July 28, 2025 
Candidate Name: Jane Doe 
Position: Software Engineer 
Band Level: L3 
Location: Bangalore 
Joining Date: August 12, 2025

1. 🎯 Appointment Details 
We are delighted to offer you the position of Software Engineer in the Engineering team at 
Company ABC. This is a full-time role based out of our Bangalore office. Your employment 
will be governed by the terms outlined in this letter and the Employee Handbook.

2. 💰 Compensation Structure  

Please create a table with the following compensation components using the provided employee data:

- Base Salary (INR): {emp['base_salary']:,}  
- Performance Bonus (INR): {emp['performance_bonus']:,}  
- Retention Bonus (INR): {emp['retention_bonus']:,}  
- Total CTC (INR): {emp['ctc']:,}  

Ensure the format matches the sample offer letter structure.


Performance bonuses are disbursed quarterly, subject to performance evaluation.
 

Performance bonuses are disbursed quarterly, subject to performance evaluation.

3. 🏖 Leave Entitlements (Band L3) 
You are entitled to 18 days of paid leave annually, structured as follows:
● Earned Leave: 10 days  
● Sick Leave: 6 days  
● Casual Leave: 2 days  

Leave resets each January. Carry-forward is allowed up to 10 days. All leaves must be 
applied via HRMS with manager approval.

4. 🏢 Work From Office Policy (Engineering Team) 
You are expected to follow a hybrid working model with a minimum of 3 days/week in 
office (suggested: Monday, Tuesday, Thursday). Exceptions for full-remote during sprints 
may be approved by your manager.  
You are eligible for:  
● Rs. 1,000/month internet reimbursement  
● One-time Rs. 5,000 home-office setup support  

5. ✈ Travel Policy (Band L3) 
You will be eligible for official travel as per Band L3 norms:
● Domestic Travel: Economy flights standard  
● International Travel: Allowed for conferences and client meetings  
● Hotel Cap: Rs. 4,000/night  
● Per Diem: Rs. 3,000/day (domestic), USD 60/day (international)  

All travel must be approved by your reporting manager and booked via the designated platform.

6. 🔒 Confidentiality & IP Clause 
You are expected to maintain strict confidentiality of all proprietary data, financials, 
codebases, and client information. All work products created during employment shall 
remain the intellectual property of Company ABC.  
A separate NDA and IP Agreement will be shared along with this letter.

7. 🚨 Termination & Exit 
● Either party may terminate the employment with 60 days' notice  
● During probation (first 3 months), a 15-day notice period applies  
● All company property and access must be returned on final working day  

8. ✅ Next Steps 
Please confirm your acceptance of this offer by signing and returning this letter via 
DocuSign within 5 working days.  
Upon acceptance, your onboarding buddy and People Ops partner will reach out with 
pre-joining formalities.

Warm regards,  
Aarti Nair  
HR Business Partner  
Company ABC  
📧 peopleops@companyabc.com  
🌐 www.companyabc.com  

=======================================================================

📌 EMPLOYEE DATA  
Date: {today}
Name: {emp['name']}
Band Level: {emp['band']}
Team: {emp['team']}
Location: {emp['location']}
Joining Date: {emp['joining_date']}
CTC: {emp['ctc']} 

📚 POLICY CONTEXT  
{context}

🎯 TASK  
Generate a complete, personalized offer letter using the structure and format shown above.  
Follow the same order, tone, and section headers. Format the Compensation Structure as a table, and adjust any bonuses, leave entitlements, WFO policy, or travel clauses based on the candidate's team and band.
Do not include any commentary or explanation — just return the final offer letter.
"""


        # GPT Call
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional HR offer letter generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            timeout=40      ##kitne der baad gpt band hoga
        )

        gpt_output = response.choices[0].message.content.strip()

        if "Offer Letter" not in gpt_output or len(gpt_output) < 300:
            raise ValueError("GPT output too short or malformed.")

        print("✅ Offer letter generated by GPT-4o.")
        return gpt_output

    except Exception as e:
        print(f"⚠️ GPT failed ({e}). Falling back to Jinja2...")
        emp = load_employee_metadata(emp_name)
        chunks = retrieve_relevant_chunks(f"Generate offer letter for {emp_name}", top_k=5)
        return  generate_offer_letter_jinja(emp, chunks)

# Run
if __name__ == "__main__":
    emp_name = input("Enter employee name: ").strip()
    
    
    
    result = generate_offer_letter(emp_name) #for gpt inference
    print("\n📄 Final Offer Letter:\n")
    print(result)
