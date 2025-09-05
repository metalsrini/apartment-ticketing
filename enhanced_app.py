from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
import csv
import os
from datetime import datetime, timedelta
import pandas as pd
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from functools import wraps

# Import database manager
try:
    from database import db_manager
    USE_DATABASE = True
except ImportError:
    USE_DATABASE = False
    print("Database module not available. Using CSV fallback.")

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Authentication configuration
USER_CREDENTIALS = {
    'admin': {
        'password': 'admin',
        'role': 'admin'
    },
    'superadmin': {
        'password': 'superadmin',
        'role': 'superadmin'
    }
}

# Configuration
CSV_FILE = 'tickets.csv'
CSV_HEADERS = ['Ticket ID', 'Flat No', 'Block No', 'Problem Type', 'Date Raised', 'Contact Number', 'Description', 'Status', 'Assigned To', 'Due Date', 'Action Taken', 'Notes', 'Created At', 'Updated At']

# Enhanced options
BLOCK_OPTIONS = ['A', 'B', 'C', 'D', 'P', 'Q', 'R', 'S', 'T', 'U', 'General Area', 'Basement Parking', 'Podium', 'Club House']
PROBLEM_TYPES = ['Plumbing', 'Electrical', 'Civil', 'Light', 'Flooring', 'AC/Heating', 'Water Supply', 'Drainage', 'Painting', 'Door/Window', 'Elevator', 'Security', 'Cleaning', 'Other']
STATUS_OPTIONS = ['Open', 'In Progress', 'Resolved', 'Closed', 'On Hold']
# Priority system removed - all tickets are equal priority
STAFF_MEMBERS = ['Unassigned', 'John Doe (Plumber)', 'Jane Smith (Electrician)', 'Mike Johnson (Maintenance)', 'Sarah Wilson (Cleaner)']

# Email configuration (set these in production)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': '',  # Set your email
    'password': '',  # Set your app password
    'enabled': False  # Set to True to enable email notifications
}

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    """Decorator to require superadmin role for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login', next=request.url))
        if session.get('role') != 'superadmin':
            flash('Access denied. Superadmin privileges required.', 'error')
            return redirect(url_for('view_tickets'))
        return f(*args, **kwargs)
    return decorated_function

def initialize_csv():
    """Initialize CSV file with headers if it doesn't exist"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADERS)

def initialize_database():
    """Initialize database and migrate CSV data if needed"""
    if USE_DATABASE:
        try:
            db_manager.create_tables()
            # Migrate existing CSV data if database is empty
            tickets = db_manager.get_all_tickets()
            if not tickets and os.path.exists(CSV_FILE):
                db_manager.migrate_from_csv(CSV_FILE)
                print("CSV data migrated to database successfully.")
        except Exception as e:
            print(f"Database initialization error: {str(e)}")
            return False
    return True

def get_next_ticket_id():
    """Generate next ticket ID"""
    if USE_DATABASE:
        return db_manager.get_next_ticket_id()
    else:
        try:
            df = pd.read_csv(CSV_FILE)
            if len(df) == 0:
                return 'TKT001'
            last_id = df['Ticket ID'].iloc[-1]
            num = int(last_id[3:]) + 1
            return f'TKT{num:03d}'
        except:
            return 'TKT001'

def get_all_tickets():
    """Get all tickets from database or CSV"""
    if USE_DATABASE:
        return db_manager.get_all_tickets()
    else:
        try:
            df = pd.read_csv(CSV_FILE)
            # Fill NaN values with empty strings to prevent float subscriptable errors
            df = df.fillna('')
            # Convert to records and ensure all values are strings
            tickets = df.to_dict('records')
            # Clean up any remaining float values
            for ticket in tickets:
                for key, value in ticket.items():
                    if pd.isna(value) or isinstance(value, float):
                        ticket[key] = ''
            return tickets
        except Exception as e:
            print(f"Error reading tickets from CSV: {str(e)}")
            return []

def add_ticket(ticket_data):
    """Add ticket to database or CSV"""
    if USE_DATABASE:
        return db_manager.add_ticket(ticket_data)
    else:
        try:
            # Save to CSV
            df = pd.read_csv(CSV_FILE)
            new_row = pd.DataFrame([ticket_data])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
            return True
        except Exception as e:
            print(f"Error adding ticket to CSV: {str(e)}")
            return False

def update_ticket_data(ticket_id, field, value):
    """Update ticket in database or CSV"""
    if USE_DATABASE:
        return db_manager.update_ticket(ticket_id, field, value)
    else:
        try:
            df = pd.read_csv(CSV_FILE)
            mask = df['Ticket ID'] == ticket_id
            if mask.any():
                df.loc[mask, field] = value
                df.loc[mask, 'Updated At'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                df.to_csv(CSV_FILE, index=False)
                return True
            return False
        except Exception as e:
            print(f"Error updating ticket in CSV: {str(e)}")
            return False

def calculate_due_date():
    """Calculate standard due date for all tickets"""
    return (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

def send_email_notification(to_email, subject, body):
    """Send email notification"""
    if not EMAIL_CONFIG['enabled'] or not EMAIL_CONFIG['email']:
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['email']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['email'], to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for admin access"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username]['password'] == password:
            session['logged_in'] = True
            session['username'] = username
            session['role'] = USER_CREDENTIALS[username]['role']
            flash('Login successful!', 'success')
            
            # Redirect to next page or tickets view
            next_page = request.args.get('next')
            return redirect(next_page or url_for('view_tickets'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/')
def index():
    """Main page with ticket submission form"""
    initialize_csv()
    initialize_database()
    return render_template('enhanced_index.html', 
                         block_options=BLOCK_OPTIONS, 
                         problem_types=PROBLEM_TYPES,
                         today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/submit', methods=['POST'])
def submit_ticket():
    """Handle ticket submission"""
    errors = validate_form_data(request.form)
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('index'))
    
    # Prepare enhanced ticket data
    ticket_id = get_next_ticket_id()
    problem_type = request.form['problem_type']
    # Set standard due date for all tickets
    due_date = calculate_due_date()
    
    ticket_data = {
        'Ticket ID': ticket_id,
        'Flat No': request.form['flat_no'].strip(),
        'Block No': request.form['block_no'],
        'Problem Type': problem_type,
        'Date Raised': request.form['date_raised'],
        'Contact Number': request.form['contact_number'].strip(),
        'Description': request.form.get('description', '').strip(),
        'Status': 'Open',
        # Priority removed - all tickets equal
        
        'Due Date': due_date,
        'Created At': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Updated At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save ticket
    try:
        if not add_ticket(ticket_data):
            flash('Error saving ticket. Please try again.', 'error')
            return redirect(url_for('index'))
        
        flash(f'Ticket {ticket_id} submitted successfully!', 'success')
        
        # Send email notification (if configured)
        if EMAIL_CONFIG['enabled']:
            subject = f"New Ticket Submitted - {ticket_id}"
            body = f"""
            <h3>New Maintenance Ticket</h3>
            <p><strong>Ticket ID:</strong> {ticket_id}</p>
            <p><strong>Flat:</strong> {request.form['flat_no']}</p>
            <p><strong>Block:</strong> {request.form['block_no']}</p>
            <p><strong>Problem:</strong> {problem_type}</p>
            <!-- Priority removed - all tickets equal -->
            <p><strong>Due Date:</strong> {due_date}</p>
            <p><strong>Contact:</strong> {request.form['contact_number']}</p>
            """
            # You would send this to management email
            # send_email_notification('management@apartment.com', subject, body)
        
    except Exception as e:
        flash(f'Error saving ticket: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/tickets')
@login_required
def view_tickets():
    """View all tickets with enhanced features"""
    try:
        tickets = get_all_tickets()
        df = pd.DataFrame(tickets) if tickets else pd.DataFrame()
        
        # Calculate statistics
        stats = {
            'total': len(tickets),
            'open': len(df[df['Status'] == 'Open']),
            'in_progress': len(df[df['Status'] == 'In Progress']),
            'resolved': len(df[df['Status'] == 'Resolved']),
            # Priority stats removed - all tickets equal
            'overdue': 0  # Calculate overdue tickets
        }
        
        # Calculate overdue tickets
        today = datetime.now().date()
        for ticket in tickets:
            try:
                due_date = datetime.strptime(ticket['Due Date'], '%Y-%m-%d').date()
                if due_date < today and ticket['Status'] not in ['Resolved', 'Closed']:
                    stats['overdue'] += 1
            except:
                pass
        
        return render_template('enhanced_tickets.html', 
                             tickets=tickets, 
                             stats=stats,
                             status_options=STATUS_OPTIONS,
                             # Priority options removed
                             staff_members=STAFF_MEMBERS)
    except Exception as e:
        flash(f'Error loading tickets: {str(e)}', 'error')
        return render_template('enhanced_tickets.html', tickets=[], stats={})

@app.route('/update_ticket', methods=['POST'])
@login_required
def update_ticket():
    """Update ticket with comprehensive fields"""
    ticket_id = request.form.get('ticket_id')
    status = request.form.get('status')
    due_date = request.form.get('due_date')
    action_taken = request.form.get('action_taken')
    assigned_to = request.form.get('assigned_to')
    notes = request.form.get('notes')
    

    try:
        if USE_DATABASE:
            # Update multiple fields in database
            updates_made = []
            
            if status:
                if db_manager.update_ticket(ticket_id, 'status', status):
                    updates_made.append('status')
            
            if due_date:
                if db_manager.update_ticket(ticket_id, 'due_date', due_date):
                    updates_made.append('due date')
            
            if action_taken:
                if db_manager.update_ticket(ticket_id, 'action_taken', action_taken):
                    updates_made.append('action taken')
            
            if assigned_to:
                if db_manager.update_ticket(ticket_id, 'assigned_to', assigned_to):
                    updates_made.append('assigned to')
            
            if notes:
                if db_manager.update_ticket(ticket_id, 'notes', notes):
                    updates_made.append('notes')
            
            if updates_made:
                success_message = f'Ticket {ticket_id} updated successfully! Updated: {", ".join(updates_made)}'
            else:
                success_message = f'No changes made to ticket {ticket_id}!'
                
        else:
            # Update in CSV
            df = pd.read_csv(CSV_FILE, dtype=str)
            # Fill NaN values with empty strings to prevent dtype issues
            df = df.fillna('')
            
            # Find and update the ticket
            mask = df['Ticket ID'] == ticket_id
            if mask.any():
                updates_made = []
                
                # Ensure proper data types to avoid pandas warnings
                if status:
                    df.loc[mask, 'Status'] = str(status)
                    updates_made.append('status')
                
                if due_date:
                    df.loc[mask, 'Due Date'] = str(due_date)
                    updates_made.append('due date')
                
                if action_taken:
                    df.loc[mask, 'Action Taken'] = str(action_taken)
                    updates_made.append('action taken')
                
                if assigned_to:
                    df.loc[mask, 'Assigned To'] = str(assigned_to)
                    updates_made.append('assigned to')
                
                if notes:
                    df.loc[mask, 'Notes'] = str(notes)
                    updates_made.append('notes')
                
                # Update timestamp
                df.loc[mask, 'Updated At'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Save back to CSV
                df.to_csv(CSV_FILE, index=False)
                
                if updates_made:
                    success_message = f'Ticket {ticket_id} updated successfully! Updated: {", ".join(updates_made)}'
                else:
                    success_message = f'No changes made to ticket {ticket_id}!'
            else:
                return jsonify({'success': False, 'message': f'Ticket {ticket_id} not found!'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating ticket: {str(e)}'})
    
    # Check if this is an AJAX request (fetch API or XMLHttpRequest)
    is_ajax = (request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 
               'application/json' in request.headers.get('Accept', '') or
               request.headers.get('Content-Type') == 'application/json')
    
    if is_ajax:
        return jsonify({'success': True, 'message': success_message})
    else:
        flash(success_message, 'success')
        return redirect(url_for('view_tickets'))

@app.route('/delete_ticket/<ticket_id>', methods=['POST'])
@superadmin_required
def delete_ticket(ticket_id):
    """Delete a ticket - SuperAdmin only"""
    try:
        if USE_DATABASE:
            # Delete from database
            if db_manager.delete_ticket(ticket_id):
                flash(f'Ticket {ticket_id} has been permanently deleted.', 'success')
            else:
                flash(f'Ticket {ticket_id} not found or could not be deleted.', 'error')
        else:
            # Delete from CSV
            df = pd.read_csv(CSV_FILE, dtype=str)
            df = df.fillna('')
            
            # Find the ticket
            mask = df['Ticket ID'] == ticket_id
            if mask.any():
                # Remove the ticket row
                df = df[~mask]
                # Save back to CSV
                df.to_csv(CSV_FILE, index=False)
                flash(f'Ticket {ticket_id} has been permanently deleted.', 'success')
            else:
                flash(f'Ticket {ticket_id} not found.', 'error')
                
    except Exception as e:
        flash(f'Error deleting ticket: {str(e)}', 'error')
    
    return redirect(url_for('view_tickets'))

@app.route('/api/tickets')
def api_tickets():
    """API endpoint for tickets data"""
    try:
        df = pd.read_csv(CSV_FILE)
        return jsonify(df.to_dict('records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reports')
@login_required
def reports():
    """Generate reports and analytics - requires admin login"""
    try:
        tickets = get_all_tickets()
        df = pd.DataFrame(tickets) if tickets else pd.DataFrame()
        
        if df.empty:
            # Handle empty dataframe
            reports_data = {
                'total_tickets': 0,
                'open_tickets': 0,
                'in_progress_tickets': 0,
                'resolved_tickets': 0,
                'block_summary': {},
                # Priority summary removed

                'status_chart_data': {'labels': [], 'data': []},
                # Priority chart data removed
                'block_chart_data': {'labels': [], 'data': []},
                'problem_chart_data': {'labels': [], 'data': []}
            }
        else:
            # Calculate summary statistics
            total_tickets = len(df)
            open_tickets = len(df[df['Status'] == 'Open'])
            in_progress_tickets = len(df[df['Status'] == 'In Progress'])
            resolved_tickets = len(df[df['Status'] == 'Resolved'])
            
            # Block summary with detailed breakdown
            block_summary = {}
            for block in df['Block No'].unique():
                block_df = df[df['Block No'] == block]
                block_summary[block] = {
                    'total': len(block_df),
                    'open': len(block_df[block_df['Status'] == 'Open']),
                    'in_progress': len(block_df[block_df['Status'] == 'In Progress']),
                    'resolved': len(block_df[block_df['Status'] == 'Resolved']),
                    'completed': len(block_df[block_df['Status'].isin(['Resolved', 'Closed'])])
                }
            
            # Priority summary removed - all tickets equal
            
            # Chart data
            status_counts = df['Status'].value_counts()
            # Priority counts removed
            block_counts = df['Block No'].value_counts()
            problem_counts = df['Problem Type'].value_counts()
            
            reports_data = {
                'total_tickets': total_tickets,
                'open_tickets': open_tickets,
                'in_progress_tickets': in_progress_tickets,
                'resolved_tickets': resolved_tickets,
                'block_summary': block_summary,
                # Priority summary removed

                'status_chart_data': {
                    'labels': status_counts.index.tolist(),
                    'data': status_counts.values.tolist()
                },
                # Priority chart data removed,
                'block_chart_data': {
                    'labels': block_counts.index.tolist(),
                    'data': block_counts.values.tolist()
                },
                'problem_chart_data': {
                    'labels': problem_counts.index.tolist(),
                    'data': problem_counts.values.tolist()
                }
            }
        
        return render_template('reports.html', reports=reports_data)
    except Exception as e:
        flash('Error generating reports. Please try again.', 'error')
        return redirect(url_for('view_tickets'))

@app.route('/export')
def export_tickets():
    """Export tickets as Excel file with enhanced data"""
    try:
        df = pd.read_csv(CSV_FILE)
        excel_file = 'tickets_export.xlsx'
        
        # Create Excel writer with multiple sheets
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main tickets sheet
            df.to_excel(writer, sheet_name='All Tickets', index=False)
            
            # Summary sheets
            df.groupby('Status').size().to_excel(writer, sheet_name='By Status')
            df.groupby('Block No').size().to_excel(writer, sheet_name='By Block')
            df.groupby('Problem Type').size().to_excel(writer, sheet_name='By Problem Type')
            # Priority grouping removed
        
        return send_file(excel_file, as_attachment=True, 
                        download_name=f'tickets_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
    except Exception as e:
        flash(f'Error exporting tickets: {str(e)}', 'error')
        return redirect(url_for('view_tickets'))

# Cloud deployment configuration
if __name__ == '__main__':
    # Get port from environment (for cloud platforms)
    port = int(os.environ.get('PORT', 5002))
    
    # Production vs development settings
    if os.environ.get('FLASK_ENV') == 'production':
        # Production settings
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Development settings
        app.run(host='0.0.0.0', port=port, debug=True)