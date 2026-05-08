import sqlite3
import os

DB_PATH = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Tasks Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            assigned_to INTEGER,
            status TEXT DEFAULT 'Pending',
            priority TEXT DEFAULT 'Normal',
            deadline TEXT,
            attachment_path TEXT,
            completion_attachment_path TEXT,
            FOREIGN KEY (assigned_to) REFERENCES users (id)
        )
    ''')

    # Messages Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    ''')

    # Jobs Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            department TEXT NOT NULL,
            description TEXT,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')

    # Notifications Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            is_read BOOLEAN DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Pre-populate dummy users if the table is empty
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        c.execute('''
            INSERT INTO users (name, email, password, role)
            VALUES 
            ('CEO Manager', 'ceo@hotmail.com', 'ceo123456', 'Admin'),
            ('HR Employee', 'hr@hotmail.com', 'hr123456', 'HR'),
            ('Accounting Employee', 'acount@hotmail.com', 'ac1233456', 'Employee')
        ''')
        
        # Add robust demo data to simulate an active environment
        c.execute('''
            INSERT INTO tasks (title, description, assigned_to, status, priority, deadline)
            VALUES
            ('Review Q3 OKRs', 'Review and approve the objectives for Q3.', 2, 'Pending', 'High', '2026-06-01'),
            ('Onboard New Developer', 'Complete the onboarding process for the new Python dev.', 2, 'In Progress', 'Normal', '2026-05-15'),
            ('Prepare Financial Report', 'Compile the monthly financial summary for the board meeting.', 3, 'Pending', 'High', '2026-05-10'),
            ('Update Invoice Templates', 'Revise the corporate invoice templates with the new branding.', 3, 'Completed', 'Normal', '2026-05-01')
        ''')
        
        c.execute('''
            INSERT INTO messages (sender_id, receiver_id, message)
            VALUES
            (2, 1, 'Hello, the new developer onboarding is going well!'),
            (3, 1, 'The financial report draft is ready for your review.'),
            (1, 3, 'Please prioritize the financial report this week.'),
            (1, 2, 'Are the Q3 OKRs finalized yet?')
        ''')
        
        c.execute('''
            INSERT INTO notifications (user_id, message, is_read)
            VALUES
            (1, 'You have 2 new unread messages from your team.', 0),
            (2, 'You have been assigned a new task: Review Q3 OKRs', 0),
            (3, 'You have been assigned a new task: Prepare Financial Report', 0)
        ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully with default accounts.")
