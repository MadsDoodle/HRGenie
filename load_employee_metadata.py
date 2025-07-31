import json

def load_employee_metadata(employee_name: str, metadata_file="Employee_List.json") -> dict:
    import json

    try:
        with open(metadata_file, "r") as f:
            employees = json.load(f)

        for emp in employees:
            if emp.get("Employee Name", "").strip().lower() == employee_name.strip().lower():
                # Normalize keys to match what the rest of your code expects
                return {
                    "name": emp["Employee Name"],
                    "team": emp["Department"],
                    "band": emp["Band"],
                    "base_salary": emp["Base Salary (INR)"],
                    "performance_bonus": emp["Performance Bonus (INR)"],
                    "retention_bonus": emp["Retention Bonus (INR)"],
                    "ctc": emp["Total CTC (INR)"],
                    "location": emp["Location"],
                    "joining_date": emp["Joining Date"]
                }

        raise ValueError(f"❌ Employee '{employee_name}' not found in {metadata_file}")

    except FileNotFoundError:
        raise FileNotFoundError(f"📁 Metadata file not found: {metadata_file}")
    except json.JSONDecodeError:
        raise ValueError(f"❌ JSON decoding failed for {metadata_file}")
