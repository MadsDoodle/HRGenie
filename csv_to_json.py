import pandas as pd
import os
import glob

def find_and_convert_csv():
    """
    Finds the first CSV file in the current directory, converts it to JSON,
    and saves it with the same base name.
    """
    try:
        # Search for any file ending with .csv in the current directory
        csv_files = glob.glob('*.csv')
        if not csv_files:
            print("❌ Error: No CSV file found in the directory.")
            return

        # Use the first CSV file found
        input_csv_path = csv_files[0]
        print(f"✅ Found CSV file: {input_csv_path}")

        # Read the CSV file
        df = pd.read_csv(input_csv_path)

        # Convert the DataFrame to a JSON string
        json_string = df.to_json(orient='records', indent=4)

        # Create the output filename by replacing .csv with .json
        json_filename = os.path.splitext(input_csv_path)[0] + ".json"

        # Write the JSON string to the new file
        with open(json_filename, 'w') as f:
            f.write(json_string)

        print(f"✅ Successfully converted '{input_csv_path}' to '{json_filename}'")

    except Exception as e:
        print(f"An error occurred: {e}")

# --- Run the conversion process ---
if __name__ == "__main__":
    find_and_convert_csv()