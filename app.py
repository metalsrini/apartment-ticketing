from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import csv
import os
from datetime import datetime
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Configuration
CSV_FILE = 'tickets.csv'
CSV_HEADERS = ['Ticket ID', 'Flat No', 'Block No', 'Problem Type', 'Date Raised', 'Contact Number', 'Description', 'Status', 'Created At']

# Block options
BLOCK_OPTIONS = ['A', 'B', 'C', 'D', 'P', 'Q', 'R', 'S', 'T', 'U', 'General Area', 'Basement Parking', 'Podium', 'Club House']

# Problem type options
PROBLEM_TYPES = ['Plumbing', 'Electrical', 'Civil', 'Light', 'Flooring', 'AC/Heating', 'Water Supply', 'Drainage', 'Painting', 'Door/Window', 'Other']

def initialize_csv():
    """Initialize CSV file with headers if it doesn't exist"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADERS)

def get_next_ticket_id():
    """Generate next ticket ID"""
    try:
        df = pd.read_csv(CSV_FILE)
        if len(df) == 0:
            return 'TKT001'
        last_id = df['Ticket ID'].iloc[-1]
        num = int(last_id[3:]) + 1
        return f'TKT{num:03d}'
    except:
        return 'TKT001'

def validate_form_data(data):
    """Validate form data"""
    errors = []
    
    if not data.get('flat_no') or not data['flat_no'].strip():
        errors.append('Flat number is required')
    
    if not data.get('block_no') or data['block_no'] not in BLOCK_OPTIONS:
        errors.append('Valid block selection is required')
    
    if not data.get('problem_type') or data['problem_type'] not in PROBLEM_TYPES:
        errors.append('Valid problem type selection is required')
    
    if not data.get('contact_number') or not data['contact_number'].strip():
        errors.append('Contact number is required')
    elif len(data['contact_number'].strip()) < 10:
        errors.append('Contact number must be at least 10 digits')
    
    return errors

@app.route('/')
def index():
    """Main page with ticket submission form"""
    return render_template('index.html', 
                         block_options=BLOCK_OPTIONS, 
                         problem_types=PROBLEM_TYPES,
                         today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/submit', methods=['POST'])
def submit_ticket():
    """Handle ticket submission"""
    # Validate form data
    errors = validate_form_data(request.form)
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('index'))
    
    # Prepare ticket data
    ticket_id = get_next_ticket_id()
    ticket_data = [
        ticket_id,
        request.form['flat_no'].strip(),
        request.form['block_no'],
        request.form['problem_type'],
        request.form['date_raised'],
        request.form['contact_number'].strip(),
        request.form.get('description', '').strip(),
        'Open',
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ]
    
    # Append to CSV
    try:
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(ticket_data)
        
        flash(f'Ticket {ticket_id} submitted successfully!', 'success')
    except Exception as e:
        flash(f'Error saving ticket: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/tickets')
def view_tickets():
    """View all tickets"""
    try:
        df = pd.read_csv(CSV_FILE)
        tickets = df.to_dict('records')
        return render_template('tickets.html', tickets=tickets)
    except Exception as e:
        flash(f'Error loading tickets: {str(e)}', 'error')
        return render_template('tickets.html', tickets=[])

@app.route('/export')
def export_tickets():
    """Export tickets as Excel file"""
    try:
        df = pd.read_csv(CSV_FILE)
        excel_file = 'tickets_export.xlsx'
        df.to_excel(excel_file, index=False)
        return send_file(excel_file, as_attachment=True, download_name=f'tickets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
    except Exception as e:
        flash(f'Error exporting tickets: {str(e)}', 'error')
        return redirect(url_for('view_tickets'))

if __name__ == '__main__':
    initialize_csv()
    app.run(debug=True, host='0.0.0.0', port=5001)