import sqlite3
import os

DB_PATH = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except PermissionError:
            pass # On Windows it might be locked, but Render is Linux so it will work.

    conn = get_db_connection()
    c = conn.cursor()

    # Companies Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            is_online BOOLEAN DEFAULT 0,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            leave_balance INTEGER DEFAULT 21,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')

    # Tasks Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            assigned_to INTEGER,
            status TEXT DEFAULT 'Pending',
            priority TEXT DEFAULT 'Normal',
            deadline TEXT,
            attachment_path TEXT,
            completion_attachment_path TEXT,
            FOREIGN KEY (company_id) REFERENCES companies (id),
            FOREIGN KEY (assigned_to) REFERENCES users (id)
        )
    ''')

    # Messages Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            sender_id INTEGER,
            receiver_id INTEGER,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id),
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    ''')

    # Jobs Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            department TEXT NOT NULL,
            description TEXT,
            created_by INTEGER,
            FOREIGN KEY (company_id) REFERENCES companies (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')

    # Notifications Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            user_id INTEGER,
            message TEXT,
            is_read BOOLEAN DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Leave Requests Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company_id INTEGER NOT NULL,
            days INTEGER NOT NULL,
            start_date DATE NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'Pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')

    # Pre-populate companies
    c.execute('SELECT COUNT(*) FROM companies')
    if c.fetchone()[0] == 0:
        c.execute('''
            INSERT INTO companies (name)
            VALUES 
            ('Asasat'),
            ('Sierra Asasat'),
            ('GEG'),
            ('Geocontrole'),
            ('Ghoson')
        ''')
        
        # Pre-populate dummy users
        c.execute('''
            INSERT INTO users (company_id, name, email, password, role)
            VALUES 
            (1, 'Asasat Owner', 'ceo@asasat.com', 'ceo123', 'Admin'),
            (1, 'Asasat HR', 'hr@asasat.com', 'hr123', 'HR'),
            (1, 'Asasat Accounting', 'acc@asasat.com', 'acc123', 'Employee'),
            
            (2, 'Sierra Manager', 'manager@sierra.com', 'mgr123', 'Admin'),
            (2, 'Sierra HR', 'hr@sierra.com', 'hr123', 'HR'),
            (2, 'Sierra Accounting', 'acc@sierra.com', 'acc123', 'Employee'),
            
            (3, 'GEG Manager', 'manager@geg.com', 'geg123', 'Admin'),
            (3, 'GEG HR', 'hr@geg.com', 'hr123', 'HR'),
            (3, 'GEG Accounting', 'acc@geg.com', 'acc123', 'Employee'),
            
            (4, 'Geocontrole Manager', 'manager@geocontrole.com', 'mgr123', 'Admin'),
            (4, 'Geocontrole HR', 'hr@geocontrole.com', 'hr123', 'HR'),
            (4, 'Geocontrole Accounting', 'acc@geocontrole.com', 'acc123', 'Employee'),
            
            (5, 'Ghoson Manager', 'manager@ghoson.com', 'mgr123', 'Admin'),
            (5, 'Ghoson HR', 'hr@ghoson.com', 'hr123', 'HR'),
            (5, 'Ghoson Accounting', 'acc@ghoson.com', 'acc123', 'Employee')
        ''')
        
        # Add robust demo data to simulate an active environment
        c.execute('''
            INSERT INTO tasks (company_id, title, description, assigned_to, status, priority, deadline)
            VALUES
            (1, 'Review Asasat OKRs', 'Review and approve the objectives for Q3.', 2, 'Pending', 'High', '2026-06-01'),
            (1, 'Onboard New Developer', 'Complete the onboarding process for the new Python dev.', 2, 'In Progress', 'Normal', '2026-05-15'),
            (3, 'Prepare GEG Financial Report', 'Compile the monthly financial summary for the board meeting.', 9, 'Pending', 'High', '2026-05-10')
        ''')
        
        c.execute('''
            INSERT INTO messages (company_id, sender_id, receiver_id, message)
            VALUES
            (1, 2, 1, 'Hello, the new developer onboarding is going well!'),
            (3, 9, 7, 'Self note: financial report draft is ready for review.')
        ''')
        
        c.execute('''
            INSERT INTO notifications (company_id, user_id, message, is_read)
            VALUES
            (1, 1, 'You have 1 new unread message from your team.', 0),
            (1, 2, 'You have been assigned a new task: Review Asasat OKRs', 0)
        ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully with default accounts.")

