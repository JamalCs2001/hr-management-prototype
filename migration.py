import sqlite3

def migrate():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # 1. Add column to tasks
    try:
        c.execute('ALTER TABLE tasks ADD COLUMN attachment_path TEXT')
        print("Added attachment_path to tasks.")
    except sqlite3.OperationalError as e:
        print(f"Column might already exist: {e}")
    
    # 2. Create messages table
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
    print("Messages table verified/created.")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate()
