import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- Secure Google Sheets Setup ---
# This will read the credentials from a secure environment variable on Render
try:
    # The JSON content is stored in an environment variable as a string
    credentials_json = os.environ.get('GSPREAD_CREDENTIALS')
    if not credentials_json:
        raise ValueError("GSPREAD_CREDENTIALS environment variable not set.")
    
    # Convert the string back to a dictionary
    credentials_dict = eval(credentials_json)
    
    gc = gspread.service_account_from_dict(credentials_dict)
    
    # --- IMPORTANT: Enter your Google Sheet name here ---
    sheet = gc.open("Shraadh Calculator Submissions").sheet1

except Exception as e:
    print(f"CRITICAL ERROR: Could not connect to Google Sheets. {e}")
    # If the app can't connect to the sheet on startup, we'll handle it gracefully
    sheet = None

@app.route('/submit', methods=['POST'])
def submit_form():
    if not sheet:
        return jsonify({"status": "error", "message": "Backend service is not configured correctly."}), 500

    try:
        data = request.get_json()
        
        # --- Input Validation ---
        required_fields = ['name', 'phone', 'death_date', 'death_time', 'death_place']
        if not all(field in data and data[field] for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields."}), 400

        # Prepare the row data
        new_row = [
            data.get('name'),
            data.get('phone'),
            data.get('email', 'N/A'), # Handle optional email
            data.get('death_date'),
            data.get('death_time'),
            data.get('death_place'),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]

        # Append the new row to the sheet
        sheet.append_row(new_row)

        return jsonify({"status": "success", "message": "Data saved successfully!"}), 200

    except Exception as e:
        print(f"An error occurred during form submission: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500

# This part is not needed for Render, but good for local testing
if __name__ == '__main__':
    # For local testing, you would need to set the environment variable
    # or revert to reading from the file.
    app.run(debug=False)