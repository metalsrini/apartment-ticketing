import os
import sqlite3
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

Base = declarative_base()

class Ticket(Base):
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True)
    ticket_id = Column(String(10), unique=True, nullable=False)
    flat_no = Column(String(10), nullable=False)
    block_no = Column(String(20), nullable=False)
    problem_type = Column(String(50), nullable=False)
    date_raised = Column(Date, nullable=False)
    contact_number = Column(String(15), nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False, default='Open')
    # Priority column removed - all tickets equal
    assigned_to = Column(String(100), default='Unassigned')
    due_date = Column(Date)
    action_taken = Column(Text, default='')
    notes = Column(Text, default='')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'Ticket ID': self.ticket_id,
            'Flat No': self.flat_no,
            'Block No': self.block_no,
            'Problem Type': self.problem_type,
            'Date Raised': self.date_raised.strftime('%Y-%m-%d') if self.date_raised else '',
            'Contact Number': self.contact_number,
            'Description': self.description or '',
            'Status': self.status,
            'Assigned To': self.assigned_to or 'Unassigned',
            'Due Date': self.due_date.strftime('%Y-%m-%d') if self.due_date else '',
            'Action Taken': self.action_taken or '',
            'Notes': self.notes or '',
            'Created At': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'Updated At': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }

class DatabaseManager:
    def __init__(self, database_url=None):
        if database_url:
            self.database_url = database_url
        else:
            # Default to SQLite for local deployment
            self.database_url = 'sqlite:///tickets.db'
        
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        # Check if notes column exists, if not add it
        self.migrate_add_notes_column()
    
    def migrate_add_notes_column(self):
        """Add notes column if it doesn't exist"""
        try:
            # Check if notes column exists
            with self.engine.connect() as conn:
                result = conn.execute("PRAGMA table_info(tickets)")
                columns = [row[1] for row in result.fetchall()]
                
                if 'notes' not in columns:
                    conn.execute("ALTER TABLE tickets ADD COLUMN notes TEXT DEFAULT ''")
                    conn.commit()
                    print("Added 'notes' column to tickets table")
        except Exception as e:
            print(f"Migration error: {str(e)}")
            pass
        
    def migrate_from_csv(self, csv_file='tickets.csv'):
        """Migrate existing CSV data to database"""
        if not os.path.exists(csv_file):
            print(f"CSV file {csv_file} not found. Skipping migration.")
            return
            
        try:
            df = pd.read_csv(csv_file)
            session = self.SessionLocal()
            
            for _, row in df.iterrows():
                # Check if ticket already exists
                existing = session.query(Ticket).filter_by(ticket_id=row['Ticket ID']).first()
                if existing:
                    continue
                    
                ticket = Ticket(
                    ticket_id=row['Ticket ID'],
                    flat_no=str(row['Flat No']),
                    block_no=str(row['Block No']),
                    problem_type=str(row['Problem Type']),
                    date_raised=pd.to_datetime(row['Date Raised']).date() if pd.notna(row['Date Raised']) else None,
                    contact_number=str(row['Contact Number']),
                    description=str(row['Description']) if pd.notna(row['Description']) else '',
                    status=str(row['Status']),
                    # Priority removed from CSV import
                    assigned_to=str(row['Assigned To']),
                    due_date=pd.to_datetime(row['Due Date']).date() if pd.notna(row['Due Date']) else None,
                    action_taken=str(row.get('Action Taken', '')) if pd.notna(row.get('Action Taken', '')) else '',
                    created_at=pd.to_datetime(row['Created At']) if pd.notna(row['Created At']) else datetime.utcnow(),
                    updated_at=pd.to_datetime(row['Updated At']) if pd.notna(row['Updated At']) else datetime.utcnow()
                )
                session.add(ticket)
            
            session.commit()
            session.close()
            print(f"Successfully migrated {len(df)} tickets from CSV to database.")
            
        except Exception as e:
            print(f"Error migrating CSV data: {str(e)}")
            session.rollback()
            session.close()
    
    def get_all_tickets(self):
        """Get all tickets as list of dictionaries"""
        session = self.SessionLocal()
        tickets = session.query(Ticket).all()
        result = [ticket.to_dict() for ticket in tickets]
        session.close()
        return result
    
    def add_ticket(self, ticket_data):
        """Add new ticket to database"""
        session = self.SessionLocal()
        try:
            # Map dictionary keys to model field names
            ticket = Ticket(
                ticket_id=str(ticket_data['Ticket ID']),
                flat_no=str(ticket_data['Flat No']),
                block_no=str(ticket_data['Block No']),
                problem_type=str(ticket_data['Problem Type']),
                date_raised=pd.to_datetime(ticket_data['Date Raised']).date() if ticket_data.get('Date Raised') else None,
                contact_number=str(ticket_data['Contact Number']),
                description=str(ticket_data.get('Description', '')),
                status=str(ticket_data.get('Status', 'Open')),
                # Priority removed from ticket creation
                assigned_to=str(ticket_data.get('Assigned To', 'Unassigned')),
                due_date=pd.to_datetime(ticket_data['Due Date']).date() if ticket_data.get('Due Date') else None,
                action_taken=str(ticket_data.get('Action Taken', '')),
                created_at=pd.to_datetime(ticket_data['Created At']) if ticket_data.get('Created At') else datetime.utcnow(),
                updated_at=pd.to_datetime(ticket_data['Updated At']) if ticket_data.get('Updated At') else datetime.utcnow()
            )
            session.add(ticket)
            session.commit()
            session.close()
            return True
        except Exception as e:
            session.rollback()
            session.close()
            print(f"Error adding ticket: {str(e)}")
            return False
    
    def update_ticket(self, ticket_id, field, value):
        """Update specific field of a ticket"""
        session = self.SessionLocal()
        try:
            ticket = session.query(Ticket).filter_by(ticket_id=ticket_id).first()
            if ticket:
                setattr(ticket, field.lower().replace(' ', '_'), value)
                ticket.updated_at = datetime.utcnow()
                session.commit()
                session.close()
                return True
            session.close()
            return False
        except Exception as e:
            session.rollback()
            session.close()
            print(f"Error updating ticket: {str(e)}")
            return False
    
    def delete_ticket(self, ticket_id):
        """Delete a ticket by ticket_id"""
        session = self.SessionLocal()
        try:
            ticket = session.query(Ticket).filter_by(ticket_id=ticket_id).first()
            if ticket:
                session.delete(ticket)
                session.commit()
                session.close()
                return True
            session.close()
            return False
        except Exception as e:
            session.rollback()
            session.close()
            print(f"Error deleting ticket: {str(e)}")
            return False
    
    def get_next_ticket_id(self):
        """Generate next ticket ID"""
        session = self.SessionLocal()
        last_ticket = session.query(Ticket).order_by(Ticket.id.desc()).first()
        session.close()
        
        if not last_ticket:
            return 'TKT001'
        
        last_id = last_ticket.ticket_id
        num = int(last_id[3:]) + 1
        return f'TKT{num:03d}'

# Database configuration based on environment
def get_database_config():
    """Get database configuration based on environment variables"""
    db_type = os.getenv('DB_TYPE', 'sqlite')  # sqlite, postgresql, mysql
    
    if db_type == 'postgresql':
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'tickets_db')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        return f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    elif db_type == 'mysql':
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '3306')
        db_name = os.getenv('DB_NAME', 'tickets_db')
        db_user = os.getenv('DB_USER', 'root')
        db_password = os.getenv('DB_PASSWORD', '')
        return f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    else:  # Default to SQLite
        db_path = os.getenv('DB_PATH', 'tickets.db')
        return f'sqlite:///{db_path}'

# Initialize database manager
db_manager = DatabaseManager(get_database_config())