from load_employee_metadata import load_employee_metadata
from fallback_jinja import generate_offer_letter_jinja

if __name__ == "__main__":
    emp_name = input("Enter employee name: ").strip()
    emp = load_employee_metadata(emp_name)
    offer_letter = generate_offer_letter_jinja(emp)

    print("\n📄 Final Offer Letter:\n")
    print(offer_letter)
