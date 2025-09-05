# Apartment Resident Issue Ticketing System

A comprehensive web-based ticketing system for apartment residents to report and track maintenance issues.

## Features

### Core Features
- **Issue Submission Form** with validation
- **Flat Number** and **Block Selection** (A, B, C, D, P, Q, R, S, T, U, General Area, Basement Parking, Podium, Club House)
- **Problem Type Categories** (Plumbing, Electrical, Civil, Light, Flooring, etc.)
- **Automatic Date Setting** (defaults to today)
- **Contact Number Validation**
- **CSV/Excel Export** functionality

### Advanced Features
- **Ticket Filtering** by Block, Problem Type, and Status
- **Search Functionality** across all ticket data
- **Real-time Statistics** dashboard
- **Responsive Design** with Bootstrap
- **Form Validation** (client-side and server-side)
- **Flash Messages** for user feedback

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Start

1. **Clone or Download** the project files to your desired directory

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   python app.py
   ```

4. **Access the Application**
   - Open your web browser
   - Navigate to: `http://localhost:5000`

## File Structure

```
apartment-ticketing/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── tickets.csv           # Generated CSV file (auto-created)
├── tickets_export.xlsx   # Generated Excel export (auto-created)
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Main form page
    └── tickets.html      # Tickets view page
```

## Usage Guide

### Submitting a New Ticket
1. Navigate to the home page
2. Fill in all required fields:
   - Flat Number
   - Block (dropdown selection)
   - Problem Type (dropdown selection)
   - Date of Issue (defaults to today)
   - Contact Number (10+ digits)
3. Optionally add a description
4. Click "Submit Ticket"

### Viewing Tickets
1. Click "View Tickets" in the navigation
2. Use filters to narrow down results:
   - Filter by Block
   - Filter by Problem Type
   - Filter by Status
   - Search across all fields
3. View real-time statistics
4. Export data to Excel

### Exporting Data
- Click "Export Excel" button on the tickets page
- Downloads an Excel file with all ticket data
- Filename includes timestamp for easy organization

## Configuration

### Customizing Options

Edit `app.py` to modify:

**Block Options:**
```python
BLOCK_OPTIONS = ['A', 'B', 'C', 'D', 'P', 'Q', 'R', 'S', 'T', 'U', 
                 'General Area', 'Basement Parking', 'Podium', 'Club House']
```

**Problem Types:**
```python
PROBLEM_TYPES = ['Plumbing', 'Electrical', 'Civil', 'Light', 'Flooring', 
                 'AC/Heating', 'Water Supply', 'Drainage', 'Painting', 
                 'Door/Window', 'Other']
```

### Security
- Change the secret key in `app.py`:
  ```python
  app.secret_key = 'your-unique-secret-key-here'
  ```

## Deployment Options

### Local Development
- Run `python app.py`
- Access at `http://localhost:5000`

### Production Deployment

#### Option 1: Using Gunicorn (Recommended)
1. Install Gunicorn:
   ```bash
   pip install gunicorn
   ```

2. Run with Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

#### Option 2: Using Docker
1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD ["python", "app.py"]
   ```

2. Build and run:
   ```bash
   docker build -t apartment-ticketing .
   docker run -p 5000:5000 apartment-ticketing
   ```

#### Option 3: Cloud Deployment
- **Heroku**: Add `Procfile` with `web: gunicorn app:app`
- **Railway**: Direct deployment from GitHub
- **PythonAnywhere**: Upload files and configure WSGI

## Data Storage

### CSV Format
Tickets are stored in `tickets.csv` with the following columns:
- Ticket ID (auto-generated: TKT001, TKT002, etc.)
- Flat No
- Block No
- Problem Type
- Date Raised
- Contact Number
- Status (defaults to "Open")
- Created At (timestamp)

### Excel Export
- Same data structure as CSV
- Generated on-demand
- Includes timestamp in filename

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Change port in `app.py`: `app.run(port=5001)`
   - Or kill existing process

2. **Module Not Found**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **CSV File Permissions**
   - Ensure write permissions in the application directory
   - Check if `tickets.csv` is open in Excel (close it)

4. **Template Not Found**
   - Ensure `templates/` directory exists
   - Check file paths are correct

### Debug Mode
- Debug mode is enabled by default in development
- Disable for production by setting `debug=False` in `app.run()`

## Future Enhancements

### Planned Features
- **Email Notifications** for ticket updates
- **Admin Dashboard** for ticket management
- **Status Updates** (In Progress, Resolved, Closed)
- **File Attachments** for issue photos
- **Resident Authentication** system
- **Maintenance Staff Portal**
- **SMS Notifications**
- **Equal Priority System** (all tickets treated equally)
- **Due Date Tracking**
- **Reporting Analytics**

### Database Migration
For larger deployments, consider migrating from CSV to:
- SQLite (built-in Python)
- PostgreSQL (production)
- MySQL (production)

## Support

For issues or feature requests:
1. Check the troubleshooting section
2. Review the code comments
3. Test with sample data

## License

This project is open-source and available for modification and distribution.

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Compatibility:** Python 3.8+, Modern Web Browsers