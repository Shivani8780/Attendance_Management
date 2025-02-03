import qrcode
import pandas as pd
import os

# Constants
EMPLOYEE_FILE = 'employees.xlsx'  # Path to the employee records Excel file
QR_CODE_DIR = 'qrcodes'  # Directory to save QR codes

# Ensure the directory exists
os.makedirs(QR_CODE_DIR, exist_ok=True)

# Load employee data
try:
    employee_df = pd.read_excel(EMPLOYEE_FILE)
except FileNotFoundError:
    print(f"Error: The file {EMPLOYEE_FILE} was not found.")
    exit(1)

def generate_qr_code(employee_id):
    # Data to encode in the QR code
    data = f"http://192.168.1.45/attendance?employee_id={employee_id}"
    
    # Generate QR code
    qr = qrcode.make(data)
    
    # Save the QR code as an image file
    qr_path = os.path.join(QR_CODE_DIR, f"{employee_id}.png")
    qr.save(qr_path)
    print(f"QR code generated for Employee_ID: {employee_id} at {qr_path}")

# Generate QR codes for all employees
if 'Employee_ID' in employee_df.columns:
    for index, row in employee_df.iterrows():
        employee_id = row['Employee_ID']
        generate_qr_code(employee_id)
    print("All QR codes generated successfully.")
else:
    print("Error: 'Employee_ID' column not found in the Excel file.")