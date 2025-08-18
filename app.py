from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)
CORS(app) # This allows your website to talk to this backend

# --- Google Sheets Setup ---
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# --- IMPORTANT: Enter your Google Sheet name here ---
sheet = client.open("Shraadh Calculator Submissions").sheet1

@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        data = request.get_json()

        # Prepare the row data
        new_row = [
            data.get('name'),
            data.get('phone'),
            data.get('email'),
            data.get('death_date'),
            data.get('death_time'),
            data.get('death_place'),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Add a timestamp
        ]

        # Append the new row to the sheet
        sheet.append_row(new_row)

        return jsonify({"status": "success", "message": "Data saved successfully!"}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500

if __name__ == '__main__':
    app.run(debug=True)