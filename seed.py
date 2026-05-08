import sqlite3
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute("INSERT INTO tasks (title, description, assigned_to, status, priority, deadline) VALUES ('Prepare Payroll Report', 'Generate and review the payroll report for April 2026.', 2, 'Completed', 'High', '2026-04-30')")
conn.commit()
conn.close()
