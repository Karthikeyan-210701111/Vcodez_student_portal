from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment variables from .env
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY')

@app.route('/')
def index():
    return render_template('index.html', details=None)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email'].strip().lower()
    phone = str(data['phone']).strip()

    try:
        xl = pd.ExcelFile('DA B5.xlsx')
        users_df      = xl.parse('FINAL ASSESMENT', dtype={'Phone Number': str})
        domain_df     = xl.parse('DOMAIN')
        mode_df       = xl.parse('MODE')
        session_df    = xl.parse('SESSION DATE')
        ass1_df       = xl.parse('ASSESMENT 1')
        ass2_df       = xl.parse('ASSESMENT 2')
        project_df    = xl.parse('PROJECT TITLE')
        reg_df        = xl.parse('REGISTRATION DATE')
        att_df        = xl.parse('ATTENDNACE')
    except Exception as e:
        return jsonify({"success": False, "message": f"Data load error: {e}"}), 500

    # Normalize user
    users_df['Email'] = users_df['Email'].astype(str).str.strip().str.lower()
    users_df['Phone Number'] = users_df['Phone Number'].astype(str).str.strip()
    user_row = users_df[(users_df['Email'] == email) & (users_df['Phone Number'] == phone)]
    if user_row.empty:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    name = user_row.iloc[0]['Name']

    # Helper function to get value from two-column sheets
    def get_value(df, col):
        df[df.columns[1]] = df[df.columns[1]].astype(str).str.strip().str.lower()
        row = df[df[df.columns[1]] == email]
        return row.iloc[0][col] if not row.empty else 'N/A'

    domain            = get_value(domain_df,    'Domain')
    mode              = get_value(mode_df,      'Mode')
    project_title     = get_value(project_df,   'project title')
    registration_date = get_value(reg_df,       'Registration date ')
    start_date        = get_value(session_df,   'Started date')
    assessment1       = get_value(ass1_df,      'Assenment1')
    assessment2       = get_value(ass2_df,      'Assesment1')

    # --- ✅ Attendance Logic with P/N and A/N ---
    att_df['Email'] = att_df['Email'].astype(str).str.strip().str.lower()
    att_row = att_df[att_df['Email'] == email]

    if not att_row.empty:
        attendance_cols = [col for col in att_df.columns if col not in ['Email', 'Name']]
        present = 0
        total = 0

        for col in attendance_cols:
            status = str(att_row.iloc[0].get(col, '')).strip().upper()
            if status == 'P/N':
                present += 1
                total += 1
            elif status == 'A/N':
                total += 1

        attendance_summary = f"{present}/{total} sessions"
    else:
        attendance_summary = "No record"

    session['details'] = {
        'name':               str(name),
        'email':              str(email),
        'phone':              str(phone),
        'domain':             str(domain),
        'mode':               str(mode),
        'project_title':      str(project_title),
        'registration_date':  str(registration_date),
        'start_date':         str(start_date),
        'assessment1':        str(assessment1),
        'assessment2':        str(assessment2),
        'attendance':         attendance_summary
    }

    return jsonify({"success": True, "redirect": "/details"})

@app.route('/details')
def details():
    if 'details' not in session:
        return redirect(url_for('index'))
    return render_template('details.html', details=session['details'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
