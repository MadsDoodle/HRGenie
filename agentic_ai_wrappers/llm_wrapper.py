import csv
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

class CSVToJSONConverter:
    """Convert CSV employee data to JSON format"""
    
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
    
    def convert_csv_to_json(self, output_json_path: str = "Employee_List.json") -> str:
        """Convert CSV to JSON and save to file"""
        try:
            employees = []
            
            with open(self.csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # Clean and convert data types
                    employee = {
                        "Employee Name": row["Employee Name"].strip(),
                        "Department": row["Department"].strip(),
                        "Band": row["Band"].strip(),
                        "Base Salary (INR)": int(float(row["Base Salary (INR)"])),
                        "Performance Bonus (INR)": int(float(row["Performance Bonus (INR)"])),
                        "Retention Bonus (INR)": int(float(row["Retention Bonus (INR)"])),
                        "Total CTC (INR)": int(float(row["Total CTC (INR)"])),
                        "Location": row["Location"].strip(),
                        "Joining Date": row["Joining Date"].strip()
                    }
                    employees.append(employee)
            
            # Save to JSON file
            with open(output_json_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(employees, jsonfile, indent=2, ensure_ascii=False)
            
            print(f"✅ Successfully converted {len(employees)} employees from CSV to JSON")
            print(f"📁 JSON file saved as: {output_json_path}")
            
            return output_json_path
            
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ CSV file not found: {self.csv_file_path}")
        except Exception as e:
            raise Exception(f"❌ Error converting CSV to JSON: {str(e)}")

class EmployeeMetadataLoader:
    """Core tool for loading employee data from JSON"""
    
    def __init__(self, metadata_file: str = "Employee_List.json"):
        self.metadata_file = metadata_file
        self._cache = None
    
    def load_employee_metadata(self, employee_name: str) -> Dict[str, Any]:
        """Load specific employee metadata"""
        try:
            with open(self.metadata_file, "r", encoding='utf-8') as f:
                employees = json.load(f)

            for emp in employees:
                if emp.get("Employee Name", "").strip().lower() == employee_name.strip().lower():
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

            raise ValueError(f"❌ Employee '{employee_name}' not found in {self.metadata_file}")

        except FileNotFoundError:
            raise FileNotFoundError(f"📁 Metadata file not found: {self.metadata_file}")
        except json.JSONDecodeError:
            raise ValueError(f"❌ JSON decoding failed for {self.metadata_file}")
    
    def load_all_employees(self) -> List[Dict[str, Any]]:
        """Load all employees for searches and listings"""
        if self._cache is None:
            try:
                with open(self.metadata_file, "r", encoding='utf-8') as f:
                    employees = json.load(f)
                
                self._cache = []
                for emp in employees:
                    self._cache.append({
                        "name": emp["Employee Name"],
                        "team": emp["Department"],
                        "band": emp["Band"],
                        "base_salary": emp["Base Salary (INR)"],
                        "performance_bonus": emp["Performance Bonus (INR)"],
                        "retention_bonus": emp["Retention Bonus (INR)"],
                        "ctc": emp["Total CTC (INR)"],
                        "location": emp["Location"],
                        "joining_date": emp["Joining Date"]
                    })
            except Exception as e:
                raise e
        
        return self._cache

class EmployeeAgentSystem:
    """LLM Wrapper that acts as an agentic system for employee queries"""
    
    def __init__(self, metadata_file: str = "Employee_List.json"):
        self.loader = EmployeeMetadataLoader(metadata_file)
        self.hr_policies = {
            "leave_entitlements": {
                "L1": {"total": 12, "earned": 6, "sick": 4, "casual": 2, "wfo_days": "4/week"},
                "L2": {"total": 15, "earned": 8, "sick": 5, "casual": 2, "wfo_days": "3-4/week"},
                "L3": {"total": 18, "earned": 10, "sick": 6, "casual": 2, "wfo_days": "3/week"},
                "L4": {"total": 20, "earned": 12, "sick": 6, "casual": 2, "wfo_days": "2-3/week"},
                "L5": {"total": "Unlimited", "earned": "NA", "sick": "NA", "casual": "NA", "wfo_days": "0-2/week"}
            },
            "travel_entitlements": {
                "L1": {"flight": "Economy (VP approval)", "hotel_cap": 2000, "per_diem_domestic": 1500, "per_diem_intl": 30},
                "L2": {"flight": "Economy (>6hrs)", "hotel_cap": 3000, "per_diem_domestic": 2000, "per_diem_intl": 40},
                "L3": {"flight": "Economy standard", "hotel_cap": 4000, "per_diem_domestic": 3000, "per_diem_intl": 60},
                "L4": {"flight": "Premium Economy", "hotel_cap": 6000, "per_diem_domestic": 4500, "per_diem_intl": 80},
                "L5": {"flight": "Business class", "hotel_cap": 10000, "per_diem_domestic": 7500, "per_diem_intl": 120}
            }
        }
    
    def extract_employee_names(self, query: str) -> List[str]:
        """Extract potential employee names from user query"""
        potential_names = []
        
        # Look for patterns like "Martha Bennett", "Christopher Higgins", etc.
        name_patterns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', query)
        potential_names.extend(name_patterns)
        
        # Also check if user mentions specific names from our employee list
        try:
            all_employees = self.loader.load_all_employees()
            for emp in all_employees:
                name = emp['name'].lower()
                # Check both full name and partial matches
                if name in query.lower():
                    potential_names.append(emp['name'])
                else:
                    # Check for first name or last name matches
                    name_parts = name.split()
                    for part in name_parts:
                        if len(part) > 2 and part in query.lower():
                            potential_names.append(emp['name'])
                            break
        except:
            pass
        
        # Remove duplicates while preserving order
        seen = set()
        unique_names = []
        for name in potential_names:
            if name.lower() not in seen:
                seen.add(name.lower())
                unique_names.append(name)
        
        return unique_names
    
    def categorize_query(self, query: str) -> Dict[str, Any]:
        """Analyze the user query to understand intent"""
        query_lower = query.lower()
        
        categories = {
            "employee_lookup": any(word in query_lower for word in ["who is", "find", "employee", "person", "staff", "member", "show me", "tell me about"]),
            "salary_inquiry": any(word in query_lower for word in ["salary", "ctc", "compensation", "pay", "bonus", "earnings", "income"]),
            "leave_policy": any(word in query_lower for word in ["leave", "vacation", "sick", "holiday", "time off", "pto"]),
            "travel_policy": any(word in query_lower for word in ["travel", "trip", "flight", "hotel", "per diem", "business travel"]),
            "team_inquiry": any(word in query_lower for word in ["team", "department", "who works in", "members", "works in"]),
            "location_inquiry": any(word in query_lower for word in ["location", "where", "based", "office", "city"]),
            "band_inquiry": any(word in query_lower for word in ["band", "level", "grade", "position level"]),
            "general_info": any(word in query_lower for word in ["info", "details", "about", "profile", "background"]),
            "list_all": any(word in query_lower for word in ["list all", "show all", "all employees", "everyone", "complete list"]),
            "statistics": any(word in query_lower for word in ["how many", "count", "total", "statistics", "stats"])
        }
        
        return {
            "primary_intent": max(categories.keys(), key=lambda k: categories[k]),
            "all_intents": [k for k, v in categories.items() if v],
            "extracted_names": self.extract_employee_names(query)
        }
    
    def format_employee_info(self, employee_data: Dict[str, Any], context: str = "general") -> str:
        """Format employee information based on context"""
        name = employee_data['name']
        team = employee_data['team']
        band = employee_data['band']
        location = employee_data['location']
        joining_date = employee_data['joining_date']
        
        base_info = f"👤 **{name}**\n"
        base_info += f"🏢 Department: {team}\n"
        base_info += f"🏷️ Band Level: {band}\n"
        base_info += f"📍 Location: {location}\n"
        base_info += f"📅 Joining Date: {joining_date}\n"
        
        if context == "salary" or context == "general":
            base_info += f"\n💰 **Compensation Details:**\n"
            base_info += f"   • Total CTC: ₹{employee_data['ctc']:,}\n"
            base_info += f"   • Base Salary: ₹{employee_data['base_salary']:,}\n"
            base_info += f"   • Performance Bonus: ₹{employee_data['performance_bonus']:,}\n"
            base_info += f"   • Retention Bonus: ₹{employee_data['retention_bonus']:,}\n"
        
        if context == "leave" or context == "general":
            leave_info = self.hr_policies["leave_entitlements"].get(band, {})
            if leave_info:
                base_info += f"\n🏖️ **Leave Entitlements:**\n"
                base_info += f"   • Total Annual Leave: {leave_info['total']} days\n"
                base_info += f"   • Earned Leave: {leave_info['earned']} days\n"
                base_info += f"   • Sick Leave: {leave_info['sick']} days\n"
                base_info += f"   • Casual Leave: {leave_info['casual']} days\n"
                base_info += f"   • WFO Requirement: {leave_info['wfo_days']}\n"
        
        if context == "travel" or context == "general":
            travel_info = self.hr_policies["travel_entitlements"].get(band, {})
            if travel_info:
                base_info += f"\n✈️ **Travel Entitlements:**\n"
                base_info += f"   • Flight Class: {travel_info['flight']}\n"
                base_info += f"   • Hotel Cap: ₹{travel_info['hotel_cap']}/night\n"
                base_info += f"   • Per Diem (Domestic): ₹{travel_info['per_diem_domestic']}/day\n"
                base_info += f"   • Per Diem (International): ${travel_info['per_diem_intl']}/day\n"
        
        return base_info
    
    def get_company_statistics(self) -> str:
        """Generate company statistics"""
        try:
            all_employees = self.loader.load_all_employees()
            
            # Basic stats
            total_employees = len(all_employees)
            
            # Department breakdown
            dept_stats = {}
            band_stats = {}
            location_stats = {}
            
            for emp in all_employees:
                # Department stats
                dept = emp['team']
                dept_stats[dept] = dept_stats.get(dept, 0) + 1
                
                # Band stats
                band = emp['band']
                band_stats[band] = band_stats.get(band, 0) + 1
                
                # Location stats
                location = emp['location']
                location_stats[location] = location_stats.get(location, 0) + 1
            
            response = f"📊 **Company Statistics** (Total: {total_employees} employees)\n\n"
            
            response += "🏢 **Department Breakdown:**\n"
            for dept, count in sorted(dept_stats.items()):
                percentage = (count / total_employees) * 100
                response += f"   • {dept}: {count} employees ({percentage:.1f}%)\n"
            
            response += "\n🏷️ **Band Distribution:**\n"
            for band, count in sorted(band_stats.items()):
                percentage = (count / total_employees) * 100
                response += f"   • {band}: {count} employees ({percentage:.1f}%)\n"
            
            response += f"\n📍 **Locations:** {len(location_stats)} different cities\n"
            top_locations = sorted(location_stats.items(), key=lambda x: x[1], reverse=True)[:5]
            response += "   Top locations:\n"
            for location, count in top_locations:
                response += f"   • {location}: {count} employee{'s' if count > 1 else ''}\n"
            
            return response
            
        except Exception as e:
            return f"❌ Sorry, I couldn't generate statistics: {str(e)}"
    
    def process_query(self, user_query: str) -> str:
        """Main method to process user queries and return responses"""
        try:
            # Analyze the query
            analysis = self.categorize_query(user_query)
            primary_intent = analysis["primary_intent"]
            extracted_names = analysis["extracted_names"]
            
            # Handle different types of queries
            if primary_intent == "statistics":
                return self.get_company_statistics()
            
            elif primary_intent == "list_all":
                return self._handle_list_all_query()
            
            elif extracted_names:
                return self._handle_specific_employee_query(extracted_names, primary_intent, user_query)
            
            elif primary_intent == "team_inquiry":
                return self._handle_team_query(user_query)
            
            elif primary_intent in ["leave_policy", "travel_policy"]:
                return self._handle_policy_query(primary_intent, user_query)
            
            else:
                return self._handle_general_query(user_query)
                
        except Exception as e:
            return f"❌ Sorry, I encountered an error: {str(e)}. Please try rephrasing your question."
    
    def _handle_specific_employee_query(self, names: List[str], intent: str, query: str) -> str:
        """Handle queries about specific employees"""
        response = ""
        found_employees = 0
        
        for name in names:
            try:
                employee_data = self.loader.load_employee_metadata(name)
                found_employees += 1
                
                if intent == "salary_inquiry":
                    response += self.format_employee_info(employee_data, "salary") + "\n\n"
                elif intent == "leave_policy":
                    response += self.format_employee_info(employee_data, "leave") + "\n\n"
                elif intent == "travel_policy":
                    response += self.format_employee_info(employee_data, "travel") + "\n\n"
                elif intent == "location_inquiry":
                    response += f"📍 {employee_data['name']} is based in {employee_data['location']}\n"
                elif intent == "band_inquiry":
                    response += f"🏷️ {employee_data['name']} is at Band {employee_data['band']} level\n"
                else:
                    response += self.format_employee_info(employee_data, "general") + "\n\n"
                
            except ValueError:
                # Try fuzzy matching for similar names
                similar_names = self._find_similar_names(name)
                if similar_names:
                    response += f"❓ Couldn't find '{name}'. Did you mean: {', '.join(similar_names[:3])}?\n\n"
                else:
                    response += f"❌ Sorry, I couldn't find an employee named '{name}' in our records.\n\n"
        
        if found_employees == 0:
            response += "💡 Try using the full name or check the spelling. You can also ask 'list all employees' to see available names."
        
        return response.strip()
    
    def _find_similar_names(self, query_name: str) -> List[str]:
        """Find similar employee names using simple string matching"""
        try:
            all_employees = self.loader.load_all_employees()
            similar = []
            
            query_lower = query_name.lower()
            for emp in all_employees:
                name_lower = emp['name'].lower()
                # Check if any part of the query matches any part of the employee name
                if any(part in name_lower for part in query_lower.split()) or \
                   any(part in query_lower for part in name_lower.split()):
                    similar.append(emp['name'])
            
            return similar[:5]  # Return top 5 matches
        except:
            return []
    
    def _handle_list_all_query(self) -> str:
        """Handle requests to list all employees"""
        try:
            all_employees = self.loader.load_all_employees()
            
            response = f"📋 **All Employees ({len(all_employees)} total):**\n\n"
            
            # Group by department
            departments = {}
            for emp in all_employees:
                dept = emp['team']
                if dept not in departments:
                    departments[dept] = []
                departments[dept].append(emp)
            
            for dept, members in sorted(departments.items()):
                response += f"🏢 **{dept}** ({len(members)} members):\n"
                for emp in sorted(members, key=lambda x: x['name']):
                    response += f"   • {emp['name']} ({emp['band']}) - {emp['location']}\n"
                response += "\n"
            
            return response.strip()
            
        except Exception as e:
            return f"❌ Sorry, I couldn't retrieve the employee list: {str(e)}"
    
    def _handle_team_query(self, query: str) -> str:
        """Handle team-related queries"""
        try:
            all_employees = self.loader.load_all_employees()
            
            # Extract team name from query
            departments = set(emp['team'] for emp in all_employees)
            mentioned_dept = None
            
            for dept in departments:
                if dept.lower() in query.lower():
                    mentioned_dept = dept
                    break
            
            if mentioned_dept:
                team_members = [emp for emp in all_employees if emp['team'] == mentioned_dept]
                response = f"🏢 **{mentioned_dept} Department** ({len(team_members)} members):\n\n"
                
                # Sort by band level, then by name
                team_members.sort(key=lambda x: (x['band'], x['name']))
                
                for emp in team_members:
                    response += f"👤 **{emp['name']}** ({emp['band']})\n"
                    response += f"   📍 Location: {emp['location']}\n"
                    response += f"   💰 CTC: ₹{emp['ctc']:,}\n"
                    response += f"   📅 Joined: {emp['joining_date']}\n\n"
                
                return response.strip()
            else:
                # Show all departments
                dept_summary = {}
                for emp in all_employees:
                    dept = emp['team']
                    if dept not in dept_summary:
                        dept_summary[dept] = 0
                    dept_summary[dept] += 1
                
                response = "🏢 **Departments Overview:**\n\n"
                for dept, count in sorted(dept_summary.items()):
                    response += f"• **{dept}**: {count} employees\n"
                
                response += "\n💡 Ask about a specific department like 'Show me Engineering team' for detailed information."
                return response
                
        except Exception as e:
            return f"❌ Sorry, I couldn't retrieve team information: {str(e)}"
    
    def _handle_policy_query(self, policy_type: str, query: str) -> str:
        """Handle policy-related queries"""
        # Check if a specific band is mentioned
        mentioned_band = None
        for band in ["L1", "L2", "L3", "L4", "L5"]:
            if band.lower() in query.lower():
                mentioned_band = band
                break
        
        if policy_type == "leave_policy":
            response = "🏖️ **Leave Policy Information:**\n\n"
            
            if mentioned_band:
                details = self.hr_policies["leave_entitlements"].get(mentioned_band, {})
                if details:
                    response += f"**Band {mentioned_band} Leave Entitlements:**\n"
                    response += f"• Total Annual Leave: {details['total']} days\n"
                    response += f"• Earned Leave: {details['earned']} days\n"
                    response += f"• Sick Leave: {details['sick']} days\n"
                    response += f"• Casual Leave: {details['casual']} days\n"
                    response += f"• WFO Requirement: {details['wfo_days']}\n"
            else:
                for band, details in self.hr_policies["leave_entitlements"].items():
                    response += f"**Band {band}:**\n"
                    response += f"• Total Leave: {details['total']} days\n"
                    response += f"• WFO Requirement: {details['wfo_days']}\n\n"
            
        elif policy_type == "travel_policy":
            response = "✈️ **Travel Policy Information:**\n\n"
            
            if mentioned_band:
                details = self.hr_policies["travel_entitlements"].get(mentioned_band, {})
                if details:
                    response += f"**Band {mentioned_band} Travel Entitlements:**\n"
                    response += f"• Flight Class: {details['flight']}\n"
                    response += f"• Hotel Cap: ₹{details['hotel_cap']}/night\n"
                    response += f"• Per Diem (Domestic): ₹{details['per_diem_domestic']}/day\n"
                    response += f"• Per Diem (International): ${details['per_diem_intl']}/day\n"
            else:
                for band, details in self.hr_policies["travel_entitlements"].items():
                    response += f"**Band {band}:**\n"
                    response += f"• Flight: {details['flight']}\n"
                    response += f"• Hotel Cap: ₹{details['hotel_cap']}/night\n"
                    response += f"• Per Diem: ₹{details['per_diem_domestic']} (domestic)\n\n"
        
        return response
    
    def _handle_general_query(self, query: str) -> str:
        """Handle general queries"""
        return ("🤖 **Employee Information Assistant**\n\n"
                "I can help you with:\n"
                "• Employee information (salary, team, location, band level)\n"
                "• Leave policies and entitlements by band\n"
                "• Travel policies and allowances\n"
                "• Department information and member lists\n"
                "• Company statistics and breakdowns\n\n"
                "**Try asking:**\n"
                "• 'Show me Martha Bennett's information'\n"
                "• 'What's the leave policy for L3?'\n"
                "• 'List all employees in Engineering'\n"
                "• 'Travel allowances for different bands'\n"
                "• 'Company statistics'\n"
                "• 'Who works in Sales department?'\n\n"
                "**Available Employees:** Martha Bennett, Christopher Higgins, Tiffany Bradshaw, Julie Rodriguez, Emily Brown, and 15 more...")


def main():
    """Main function to demonstrate the complete system"""
    
    print("🔄 Starting Employee Information System...")
    print("=" * 60)
    
    # Step 1: Convert CSV to JSON
    print("📋 Step 1: Converting CSV to JSON...")
    converter = CSVToJSONConverter("Employee_List.csv")
    
    try:
        json_file = converter.convert_csv_to_json("Employee_List.json")
        print(f"✅ Conversion successful: {json_file}")
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        # Create a sample JSON file for demo purposes
        sample_data = [
            {
                "Employee Name": "Martha Bennett",
                "Department": "Sales",
                "Band": "L1",
                "Base Salary (INR)": 411477,
                "Performance Bonus (INR)": 60657,
                "Retention Bonus (INR)": 22227,
                "Total CTC (INR)": 494361,
                "Location": "Aimeebury",
                "Joining Date": "2025-05-02"
            },
            {
                "Employee Name": "Christopher Higgins",
                "Department": "HR",
                "Band": "L3",
                "Base Salary (INR)": 1405700,
                "Performance Bonus (INR)": 178939,
                "Retention Bonus (INR)": 95532,
                "Total CTC (INR)": 1680171,
                "Location": "New Amanda",
                "Joining Date": "2025-05-12"
            }
        ]
        
        with open("Employee_List.json", "w") as f:
            json.dump(sample_data, f, indent=2)
        print("📝 Created sample JSON file for demo")
    
    print("\n" + "=" * 60)
    
    # Step 2: Initialize the Agent System
    print("🤖 Step 2: Initializing Employee Agent System...")
    agent = EmployeeAgentSystem("Employee_List.json")
    print("✅ Agent system ready!")
    
    print("\n" + "=" * 60)
    
    # Step 3: Demo Queries
    print("🎯 Step 3: Running Demo Queries...")
    
    demo_queries = [
        "Show me Martha Bennett's information",
        "What's Christopher Higgins' salary?",
        "List all employees in Sales",
        "What are the leave entitlements for L3 band?",
        "Company statistics",
        "Who works in HR department?",
        "Travel policy for L5 band"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n📝 Demo Query {i}: {query}")
        print("-" * 50)
        response = agent.process_query(query)
        print(response)
        print("=" * 60)
    
    # Step 4: Interactive Mode
    print("\n🎮 Step 4: Interactive Mode")
    print("Type your questions below (type 'quit' to exit):")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n💬 Your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
                print("👋 Thank you for using the Employee Information System!")
                break
            
            if user_input:
                print("\n🤖 Assistant:")
                response = agent.process_query(user_input)
                print(response)
                print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()