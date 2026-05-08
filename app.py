from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from database import get_db_connection, init_db
import os
import io
from fpdf import FPDF
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super_secret_prototype_key' # In a real app, use environment variables

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Utility Functions ---
def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def login_required(role=None):
    def wrapper(fn):
        def decorated_view(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash("Unauthorized access.", "error")
                return redirect(url_for('login'))
            return fn(*args, **kwargs)
        # Rename function name to avoid endpoints overwriting
        decorated_view.__name__ = fn.__name__
        return decorated_view
    return wrapper

# --- Context Processors ---
@app.context_processor
def inject_user():
    user = None
    unread_notifications = []
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
        conn = get_db_connection()
        unread_notifications = conn.execute('SELECT * FROM notifications WHERE user_id = ? AND is_read = 0 ORDER BY timestamp DESC', (session['user_id'],)).fetchall()
        conn.close()
    return dict(current_user=user, unread_notifications=unread_notifications)

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'Admin':
            return redirect(url_for('admin_dashboard'))
        elif session.get('role') == 'HR':
            return redirect(url_for('hr_dashboard'))
        elif session.get('role') == 'Employee':
            return redirect(url_for('employee_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            
            if user['role'] == 'Admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'HR':
                return redirect(url_for('hr_dashboard'))
            else:
                return redirect(url_for('employee_dashboard'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Admin Routes ---

@app.route('/admin')
@login_required(role='Admin')
def admin_dashboard():
    conn = get_db_connection()
    tasks_count = conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
    completed_tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE status = "Completed"').fetchone()[0]
    users_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    
    recent_tasks = conn.execute('SELECT tasks.*, users.name as assignee FROM tasks LEFT JOIN users ON tasks.assigned_to = users.id ORDER BY tasks.id DESC LIMIT 5').fetchall()
    conn.close()
    
    return render_template('dashboard_admin.html', 
                           tasks_count=tasks_count, 
                           completed_tasks=completed_tasks, 
                           users_count=users_count,
                           recent_tasks=recent_tasks)

@app.route('/admin/tasks', methods=['GET'])
@login_required(role='Admin')
def admin_tasks():
    conn = get_db_connection()
    tasks = conn.execute('SELECT tasks.*, users.name as assignee FROM tasks LEFT JOIN users ON tasks.assigned_to = users.id').fetchall()
    users = conn.execute('SELECT * FROM users WHERE role IN ("HR", "Employee")').fetchall()
    conn.close()
    
    return render_template('tasks.html', tasks=tasks, users=users, is_admin=True)

@app.route('/admin/employees')
@login_required(role='Admin')
def admin_employees():
    conn = get_db_connection()
    employees = conn.execute('SELECT * FROM users WHERE role != "Admin"').fetchall()
    conn.close()
    return render_template('employees.html', employees=employees)


# --- HR Routes ---

@app.route('/hr')
@login_required(role='HR')
def hr_dashboard():
    conn = get_db_connection()
    user_id = session['user_id']
    my_tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE assigned_to = ?', (user_id,)).fetchone()[0]
    pending_tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE assigned_to = ? AND status != "Completed"', (user_id,)).fetchone()[0]
    my_jobs = conn.execute('SELECT COUNT(*) FROM jobs WHERE created_by = ?', (user_id,)).fetchone()[0]
    
    recent_tasks = conn.execute('SELECT * FROM tasks WHERE assigned_to = ? ORDER BY id DESC LIMIT 5', (user_id,)).fetchall()
    conn.close()
    
    return render_template('dashboard_hr.html', 
                           my_tasks=my_tasks, 
                           pending_tasks=pending_tasks, 
                           my_jobs=my_jobs,
                           recent_tasks=recent_tasks)

@app.route('/hr/tasks', methods=['GET', 'POST'])
@login_required(role='HR')
def hr_tasks():
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'POST':
        task_id = request.form['task_id']
        new_status = request.form['status']
        
        attachment_path = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != '':
                if not file.filename.lower().endswith('.pdf'):
                    flash('Only PDF files are allowed.', 'error')
                    return redirect(request.url)
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                attachment_path = f"uploads/{filename}"

        if attachment_path:
            conn.execute('UPDATE tasks SET status = ?, completion_attachment_path = ? WHERE id = ? AND assigned_to = ?', (new_status, attachment_path, task_id, user_id))
        else:
            conn.execute('UPDATE tasks SET status = ? WHERE id = ? AND assigned_to = ?', (new_status, task_id, user_id))
            
        conn.commit()
        flash('Task status updated.', 'success')
        return redirect(url_for('hr_tasks'))
        
    tasks = conn.execute('SELECT * FROM tasks WHERE assigned_to = ?', (user_id,)).fetchall()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    
    return render_template('tasks.html', tasks=tasks, users=users, is_admin=False)

@app.route('/task/<int:task_id>/pdf')
@login_required()
def download_task_pdf(task_id):
    conn = get_db_connection()
    task = conn.execute('SELECT tasks.*, users.name as assignee FROM tasks LEFT JOIN users ON tasks.assigned_to = users.id WHERE tasks.id = ?', (task_id,)).fetchone()
    conn.close()

    if not task:
        flash("Task not found.", "error")
        return redirect(url_for('hr_tasks'))

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", size=20, style="B")
    pdf.cell(0, 15, text=f"Task Report: #{task['id']}", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)

    # Details
    pdf.set_font("Helvetica", size=12, style="B")
    pdf.cell(40, 10, text="Title:", new_x="RIGHT")
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, text=str(task['title']), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", size=12, style="B")
    pdf.cell(40, 10, text="Assignee:", new_x="RIGHT")
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, text=str(task['assignee'] or 'Unassigned'), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", size=12, style="B")
    pdf.cell(40, 10, text="Status:", new_x="RIGHT")
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, text=str(task['status']), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", size=12, style="B")
    pdf.cell(40, 10, text="Priority:", new_x="RIGHT")
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, text=str(task['priority']), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", size=12, style="B")
    pdf.cell(40, 10, text="Deadline:", new_x="RIGHT")
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, text=str(task['deadline'] or 'N/A'), new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(10)
    
    # Description
    pdf.set_font("Helvetica", size=12, style="B")
    pdf.cell(0, 10, text="Description:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, text=str(task['description'] or 'No description provided.'))

    # Output to an in-memory bytes buffer
    pdf_bytes = pdf.output()
    buffer = io.BytesIO(pdf_bytes)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Task_{task['id']}.pdf",
        mimetype='application/pdf'
    )

@app.route('/hr/jobs', methods=['GET', 'POST'])
@login_required(role='HR')
def hr_jobs():
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'POST':
        title = request.form['title']
        department = request.form['department']
        description = request.form['description']
        
        conn.execute('INSERT INTO jobs (title, department, description, created_by) VALUES (?, ?, ?, ?)',
                     (title, department, description, user_id))
        conn.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('hr_jobs'))
        
    jobs = conn.execute('SELECT jobs.*, users.name as creator FROM jobs JOIN users ON jobs.created_by = users.id').fetchall()
    conn.close()
    
    return render_template('jobs.html', jobs=jobs)

# --- Shared Routes (Tasks & Messages & Notifications) ---

@app.route('/tasks/create', methods=['POST'])
@login_required()
def create_task():
    title = request.form['title']
    description = request.form['description']
    assigned_to = request.form['assigned_to']
    priority = request.form['priority']
    deadline = request.form['deadline']
    
    attachment_path = None
    if 'attachment' in request.files:
        file = request.files['attachment']
        if file and file.filename != '':
            if not file.filename.lower().endswith('.pdf'):
                flash('Only PDF files are allowed.', 'error')
                return redirect(request.referrer)
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            attachment_path = f"uploads/{filename}"

    conn = get_db_connection()
    if attachment_path:
        conn.execute('INSERT INTO tasks (title, description, assigned_to, priority, deadline, attachment_path) VALUES (?, ?, ?, ?, ?, ?)',
                     (title, description, assigned_to, priority, deadline, attachment_path))
    else:
        conn.execute('INSERT INTO tasks (title, description, assigned_to, priority, deadline) VALUES (?, ?, ?, ?, ?)',
                     (title, description, assigned_to, priority, deadline))
    
    conn.execute('INSERT INTO notifications (user_id, message) VALUES (?, ?)',
                 (assigned_to, f"You have been assigned a new task: {title}"))
    
    conn.commit()
    conn.close()
    
    flash('Task created successfully!', 'success')
    role = session.get('role')
    if role == 'Admin':
        return redirect(url_for('admin_tasks'))
    elif role == 'HR':
        return redirect(url_for('hr_tasks'))
    else:
        return redirect(url_for('employee_tasks'))

@app.route('/notifications/read', methods=['POST'])
@login_required()
def read_notifications():
    conn = get_db_connection()
    conn.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    return {'status': 'success'}

# --- Employee Routes ---

@app.route('/employee')
@login_required(role='Employee')
def employee_dashboard():
    conn = get_db_connection()
    user_id = session['user_id']
    my_tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE assigned_to = ?', (user_id,)).fetchone()[0]
    pending_tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE assigned_to = ? AND status != "Completed"', (user_id,)).fetchone()[0]
    
    recent_tasks = conn.execute('SELECT * FROM tasks WHERE assigned_to = ? ORDER BY id DESC LIMIT 5', (user_id,)).fetchall()
    conn.close()
    
    return render_template('dashboard_employee.html', 
                           my_tasks=my_tasks, 
                           pending_tasks=pending_tasks, 
                           recent_tasks=recent_tasks)

@app.route('/employee/tasks', methods=['GET', 'POST'])
@login_required(role='Employee')
def employee_tasks():
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'POST':
        task_id = request.form['task_id']
        new_status = request.form['status']
        
        attachment_path = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != '':
                if not file.filename.lower().endswith('.pdf'):
                    flash('Only PDF files are allowed.', 'error')
                    return redirect(request.url)
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                attachment_path = f"uploads/{filename}"

        if attachment_path:
            conn.execute('UPDATE tasks SET status = ?, completion_attachment_path = ? WHERE id = ? AND assigned_to = ?', (new_status, attachment_path, task_id, user_id))
        else:
            conn.execute('UPDATE tasks SET status = ? WHERE id = ? AND assigned_to = ?', (new_status, task_id, user_id))
            
        conn.commit()
        flash('Task status updated.', 'success')
        return redirect(url_for('employee_tasks'))
        
    tasks = conn.execute('SELECT * FROM tasks WHERE assigned_to = ?', (user_id,)).fetchall()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    
    return render_template('tasks.html', tasks=tasks, users=users, is_admin=False)

@app.route('/messages', methods=['GET', 'POST'])
@login_required()
def messages():
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'POST':
        receiver_id = request.form['receiver_id']
        message_text = request.form['message']
        
        conn.execute('INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)',
                     (user_id, receiver_id, message_text))
        conn.execute('INSERT INTO notifications (user_id, message) VALUES (?, ?)',
                     (receiver_id, f"New message from {session.get('name')}"))
        conn.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('messages'))
        
    received_msgs = conn.execute('''
        SELECT messages.*, users.name as sender_name 
        FROM messages 
        JOIN users ON messages.sender_id = users.id 
        WHERE receiver_id = ? 
        ORDER BY timestamp DESC
    ''', (user_id,)).fetchall()
    
    users = conn.execute('SELECT * FROM users WHERE id != ?', (user_id,)).fetchall()
    conn.close()
    
    return render_template('messages.html', messages=received_msgs, users=users)

if __name__ == '__main__':
    # Auto-initialize DB for prototype simplicity
    if not os.path.exists('database.db'):
        init_db()
    app.run(debug=False, port=5000)
