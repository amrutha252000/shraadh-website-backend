import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from datetime import datetime
import json
import requests

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

    # gc = gspread.service_account(filename='sb2.json')
    # sheet = gc.open("Shraadh Calculator Submissions")
    # worksheet = sheet.get_worksheet(0)


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
 
        prompt = 'Based on Vedic astrology (Panchang), for a person who passed away on 01/01/2001 at 11:11 AM in goa, calculate the following for the year 2025: 1. The name of the annual Shraadh tithi (e.g., "Krishna Paksha, Ashtami"). 2. The exact Gregorian date and time in 2025 for that annual Shraadh tithi, formatted as "MM/DD/YYYY at HH:MM AM/PM". 3. The single corresponding date from the Pitru Paksha 2025 calendar (September 7 to September 21, 2025) that matches the tithi, formatted as "MM/DD/YYYY (Name of Shraddha)". Provide the answer as a JSON object with three keys. For example: { "annualTithiName": "Ashadha Shukla Shashthi", "annualTithiDateTime": "06/07/2025 at 10:45 AM", "pitruPakshaDate": "12/09/2025 (Shashthi Shraddha)"' 
        chatHistory = []
        chatHistory.append({"role": "user", "parts": [{ "text": prompt }] })
        
        payload = {
            "contents" : chatHistory,
            "generationConfig" : {
                "responseMimeType" : "application/json",
                "responseSchema" : {
                    "type" : "OBJECT",
                    "properties" : {
                        "annualTithiName": { "type": "STRING" },
                        "annualTithiDateTime": { "type": "STRING" },
                        "pitruPakshaDate": { "type": "STRING" }
                    },
                    "required" : ["annualTithiName", "annualTithiDateTime", "pitruPakshaDate"]
                }
            }
        } 
        
        apiKey = "AIzaSyA00PdUAuGWu6X7IS7uIwMJcc2wmsXVZy4"
        apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={apiKey}"
        # print(apiUrl)


        try:
            headers = {
            'Content-Type': 'application/json'
            }
            response = requests.post(apiUrl, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            # print(result)
            all_tithi = result['candidates'][0]['content']['parts'][0]['text']

            json_data = json.loads(all_tithi)
            annualTithiDateTime = json_data['annualTithiDateTime']
            annualTithiName = json_data['annualTithiName']
            pitruPakshaDate = json_data['pitruPakshaDate']
            # print( annualTithiDateTime, annualTithiName, pitruPakshaDate)

            ans = {
                "annualTithiDateTime": annualTithiDateTime,
                "annualTithiName": annualTithiName,
                "pitruPakshaDate": pitruPakshaDate
            }

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

        # return jsonify({"status": "success", "message": "Data saved successfully!"})  , 200
        return ans

    except Exception as e:
        print(f"An error occurred during form submission: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500

# This part is not needed for Render, but good for local testing
if __name__ == '__main__':
    # For local testing, you would need to set the environment variable
    # or revert to reading from the file.
    app.run(debug=True)