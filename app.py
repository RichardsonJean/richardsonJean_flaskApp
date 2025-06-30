from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import os
import re


app = Flask(__name__)
app.secret_key = 'your_secret_key'  

DB_NAME = 'patients.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                dob TEXT NOT NULL,
                therapist TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    dob = request.form.get('dob', '').strip()
    therapist = request.form.get('therapist', '').strip()

    # Validation
    errors = []
    name_pattern = re.compile(r"^[A-Za-z\s'\-]+$")

    if not first_name:
        errors.append("First name is required.")
    elif not name_pattern.match(first_name):
        errors.append("First name can only contain letters, spaces, apostrophes, and hyphens.")

    if not last_name:
        errors.append("Last name is required.")
    elif not name_pattern.match(last_name):
        errors.append("Last name can only contain letters, spaces, apostrophes, and hyphens.")

    if not therapist:
        errors.append("Therapist name is required.")
    elif not name_pattern.match(therapist):
        errors.append("Therapist name can only contain letters, spaces, apostrophes, and hyphens.")

    if not dob:
        errors.append("Date of birth is required.")
    else:
        try:
            dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
            today = datetime.today().date() 
            if dob_date >= today:
                errors.append("Date of birth must be in the past.")
        except ValueError:
            errors.append("Invalid date format.")

    if errors:
        return render_template(
            'form.html',
            errors=errors,
            form_data={
                'first_name': first_name,
                'last_name': last_name,
                'dob': dob,
                'therapist': therapist
            }
        )


    # Save to DB
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO patients (first_name, last_name, dob, therapist)
            VALUES (?, ?, ?, ?)
        ''', (first_name, last_name, dob, therapist))
        conn.commit()

    return render_template('confirmation.html',
                           first_name=first_name,
                           last_name=last_name,
                           dob=dob,
                           therapist=therapist)

if __name__ == '__main__':
    if not os.path.exists(DB_NAME):
        init_db()
    app.run(debug=True)
