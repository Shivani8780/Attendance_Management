from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import pandas as pd
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# Constants
EMPLOYEE_FILE = 'employees.xlsx'  # Path to the employee records Excel file
ATTENDANCE_FILE = 'attendance_records.xlsx'  # Path to the attendance records Excel file

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize the database
def init_db():
    try:
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            employee_name TEXT,
            date TEXT,
            time_in TEXT,
            time_out TEXT
        )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    finally:
        conn.close()

# Home route to show dashboard
@app.route('/')
def index():
    try:
        # Load the employee records from the Excel file
        employee_df = pd.read_excel(EMPLOYEE_FILE)
        total_employees = len(employee_df)  # Total number of employees

        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("SELECT * FROM attendance")
        records = c.fetchall()

        # Calculate the attendance percentage for each employee
        attendance_percentages = {}
        c.execute("SELECT DISTINCT employee_id FROM attendance")
        employees = c.fetchall()

        for employee in employees:
            employee_id = employee[0]
            c.execute("SELECT COUNT(*) FROM attendance WHERE employee_id = ?", (employee_id,))
            total_days = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM attendance WHERE employee_id = ? AND time_out IS NOT NULL", (employee_id,))
            present_days = c.fetchone()[0]

            if total_days > 0:
                percentage = (present_days / total_days) * 100
            else:
                percentage = 0

            # Store the attendance percentage
            attendance_percentages[employee_id] = percentage

        # Calculate total attendance percentage for today
        today = datetime.today().strftime('%Y-%m-%d')
        c.execute("SELECT COUNT(DISTINCT employee_id) FROM attendance WHERE date = ? AND time_out IS NOT NULL", (today,))
        present_employees = c.fetchone()[0]

        if total_employees > 0:
            total_percentage = (present_employees / total_employees) * 100
        else:
            total_percentage = 0

        return render_template('index.html', records=records, attendance_percentages=attendance_percentages, total_percentage=total_percentage)
    except Exception as e:
        logging.error(f"Error in index route: {e}")
        return render_template('index.html', records=[], attendance_percentages={}, total_percentage=0)
    finally:
        conn.close()

# Route to handle QR code scanning
@app.route('/attendance', methods=['GET'])
def mark_attendance():
    employee_id = request.args.get('employee_id')
    if not employee_id:
        return jsonify({'status': 'error', 'message': 'Invalid QR code'})

    date_today = datetime.today().strftime('%Y-%m-%d')
    time_now = datetime.now().strftime('%H:%M:%S')

    try:
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()

        # Check if the employee is already signed in today
        c.execute("SELECT * FROM attendance WHERE employee_id = ? AND date = ? AND time_out IS NULL", (employee_id, date_today))
        record = c.fetchone()

        if record:
            # Employee is signed in, so sign them out
            c.execute("UPDATE attendance SET time_out = ? WHERE id = ?", (time_now, record[0]))
            message = f'Signed out for {employee_id}'
        else:
            # Employee is not signed in, so sign them in
            c.execute("INSERT INTO attendance (employee_id, employee_name, date, time_in, time_out) VALUES (?, ?, ?, ?, ?)", 
                      (employee_id, '', date_today, time_now, None))
            message = f'Signed in for {employee_id}'

        conn.commit()
        return jsonify({'status': 'success', 'message': message})
    except Exception as e:
        logging.error(f"Error in mark_attendance route: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred'})
    finally:
        conn.close()

# Route to mark time-out
@app.route('/mark_out/<int:record_id>')
def mark_out(record_id):
    time_out = datetime.now().strftime('%H:%M:%S')

    try:
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("UPDATE attendance SET time_out = ? WHERE id = ?", (time_out, record_id))
        conn.commit()
    except Exception as e:
        logging.error(f"Error in mark_out route: {e}")
    finally:
        conn.close()

    return redirect(url_for('index'))

# Logout route to mark logout
@app.route('/logout/<int:record_id>')
def logout(record_id):
    time_out = datetime.now().strftime('%H:%M:%S')

    try:
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("UPDATE attendance SET time_out = ? WHERE id = ?", (time_out, record_id))
        conn.commit()
    except Exception as e:
        logging.error(f"Error in logout route: {e}")
    finally:
        conn.close()

    return redirect(url_for('index'))

def main():
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()