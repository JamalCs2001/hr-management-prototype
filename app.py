from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from database import get_db_connection, init_db
import os
import io
from fpdf import FPDF
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_prototype_key' # In a real app, use environment variables

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Mapping for dynamic roles for Asasat users
ASASAT_DYNAMIC_ROLES = {
    1: 'Owner',
    2: 'Employee',
    3: 'Chairman',
    4: 'Employee',
    5: 'Employee'
}

def _arabic_plural(n, singular, dual, plural):
    """Apply Arabic grammar rules for number-noun agreement."""
    if n == 1:
        return f"قبل {singular}"           # قبل ساعة
    elif n == 2:
        return f"قبل {dual}"               # قبل ساعتين
    elif 3 <= n <= 10:
        return f"قبل {n} {plural}"         # قبل 5 ساعات
    else:
        return f"قبل {n} {singular}"       # قبل 11 ساعة

@app.template_filter('timeago')
def timeago_filter(dt_string):
    if not dt_string:
        return 'غير معروف'
    try:
        dt = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
        now = datetime.utcnow()
        diff = now - dt
        
        days = diff.days
        seconds = diff.seconds
        
        if days > 0:
            return _arabic_plural(days, 'يوم', 'يومين', 'أيام')
        
        hours = seconds // 3600
        if hours > 0:
            return _arabic_plural(hours, 'ساعة', 'ساعتين', 'ساعات')
            
        minutes = seconds // 60
        if minutes > 0:
            return _arabic_plural(minutes, 'دقيقة', 'دقيقتين', 'دقائق')
            
        return "الآن"
    except Exception as e:
        return dt_string

# --- Utility Functions ---
def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def get_visible_users(user_id, active_company_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        conn.close()
        return []
        
    if user['company_id'] == 1:
        users = conn.execute('SELECT * FROM users WHERE company_id = ?', (active_company_id,)).fetchall()
    elif user['role'] in ['Admin', 'HR']:
        users = conn.execute('SELECT * FROM users WHERE company_id = ?', (active_company_id,)).fetchall()
    else:
        users = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchall()
        
    conn.close()
    return users

def login_required(roles=None, allow_asasat=False):
    def wrapper(fn):
        def decorated_view(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
                
            if allow_asasat and session.get('base_company_id') == 1:
                pass
            elif roles:
                allowed_roles = [roles] if isinstance(roles, str) else roles
                if session.get('role') not in allowed_roles:
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
    active_company = None
    dynamic_role = None
    unread_notifications = []
    companies = []
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
        if user:
            conn = get_db_connection()
            unread_notifications = conn.execute('SELECT * FROM notifications WHERE user_id = ? AND is_read = 0 ORDER BY timestamp DESC', (session['user_id'],)).fetchall()
            
            # Active company logic
            active_company_id = session.get('active_company_id', user['company_id'])
            active_company = conn.execute('SELECT * FROM companies WHERE id = ?', (active_company_id,)).fetchone()
            
            # If user is Asasat employee, give them "Companies" list and dynamic role
            if user['company_id'] == 1:
                companies = conn.execute('SELECT * FROM companies').fetchall()
                dynamic_role = ASASAT_DYNAMIC_ROLES.get(active_company_id, 'Representative')
            else:
                dynamic_role = user['role']
                
            conn.close()
    return dict(current_user=user, 
                unread_notifications=unread_notifications, 
                active_company=active_company,
                dynamic_role=dynamic_role,
                companies=companies)

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
            conn = get_db_connection()
            conn.execute('UPDATE users SET is_online = 1, last_seen = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
            conn.commit()
            conn.close()
            
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            session['base_company_id'] = user['company_id']
            session['active_company_id'] = user['company_id']
            
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
    if 'user_id' in session:
        conn = get_db_connection()
        conn.execute('UPDATE users SET is_online = 0, last_seen = CURRENT_TIMESTAMP WHERE id = ?', (session['user_id'],))
        conn.commit()
        conn.close()
    session.clear()
    return redirect(url_for('login'))

@app.route('/switch_company/<int:company_id>', methods=['GET', 'POST'])
def switch_company(company_id):
    if 'user_id' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Not logged in'}), 401
        return redirect(url_for('login'))
        
    # Only Asasat users can switch
    if session.get('base_company_id') == 1:
        session['active_company_id'] = company_id
        # If AJAX request, return JSON instead of redirect
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            conn = get_db_connection()
            company = conn.execute('SELECT * FROM companies WHERE id = ?', (company_id,)).fetchone()
            conn.close()
            return jsonify({
                'status': 'success',
                'company_id': company_id,
                'company_name': company['name'] if company else 'Unknown'
            })
        flash('Switched company workspace successfully.', 'success')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        flash('Unauthorized to switch companies.', 'error')
        
    return redirect(request.referrer or url_for('index'))

# --- Admin Routes ---

@app.route('/admin')
@login_required(roles='Admin')
def admin_dashboard():
    conn = get_db_connection()
    active_company_id = session.get('active_company_id')
    tasks_count = conn.execute('SELECT COUNT(*) FROM tasks WHERE company_id = ?', (active_company_id,)).fetchone()[0]
    completed_tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE status = "Completed" AND company_id = ?', (active_company_id,)).fetchone()[0]
    users_count = conn.execute('SELECT COUNT(*) FROM users WHERE company_id = ?', (active_company_id,)).fetchone()[0]
    
    recent_tasks = conn.execute('SELECT tasks.*, users.name as assignee FROM tasks LEFT JOIN users ON tasks.assigned_to = users.id WHERE tasks.company_id = ? ORDER BY tasks.id DESC LIMIT 5', (active_company_id,)).fetchall()
    conn.close()
    
    return render_template('dashboard_admin.html', 
                           tasks_count=tasks_count, 
                           completed_tasks=completed_tasks, 
                           users_count=users_count,
                           recent_tasks=recent_tasks)

@app.route('/admin/tasks', methods=['GET'])
@login_required(roles='Admin')
def admin_tasks():
    conn = get_db_connection()
    active_company_id = session.get('active_company_id')
    tasks = conn.execute('SELECT tasks.*, users.name as assignee FROM tasks LEFT JOIN users ON tasks.assigned_to = users.id WHERE tasks.company_id = ?', (active_company_id,)).fetchall()
    conn.close()
    
    users = get_visible_users(session['user_id'], active_company_id)
    users = [u for u in users if u['role'] in ('HR', 'Employee')]
    
    return render_template('tasks.html', tasks=tasks, users=users, is_admin=True)

@app.route('/admin/employees')
@login_required(roles=['Admin', 'HR'], allow_asasat=True)
def admin_employees():
    active_company_id = session.get('active_company_id')
    employees = get_visible_users(session['user_id'], active_company_id)
    employees = [e for e in employees if e['role'] != 'Admin']
    return render_template('employees.html', employees=employees)


# --- HR Routes ---

@app.route('/hr')
@login_required(roles='HR')
def hr_dashboard():
    conn = get_db_connection()
    user_id = session['user_id']
    active_company_id = session.get('active_company_id')
    my_tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE assigned_to = ? AND company_id = ?', (user_id, active_company_id)).fetchone()[0]
    pending_tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE assigned_to = ? AND status != "Completed" AND company_id = ?', (user_id, active_company_id)).fetchone()[0]
    my_jobs = conn.execute('SELECT COUNT(*) FROM jobs WHERE created_by = ? AND company_id = ?', (user_id, active_company_id)).fetchone()[0]
    
    recent_tasks = conn.execute('SELECT * FROM tasks WHERE assigned_to = ? AND company_id = ? ORDER BY id DESC LIMIT 5', (user_id, active_company_id)).fetchall()
    conn.close()
    
    return render_template('dashboard_hr.html', 
                           my_tasks=my_tasks, 
                           pending_tasks=pending_tasks, 
                           my_jobs=my_jobs,
                           recent_tasks=recent_tasks)

@app.route('/hr/tasks', methods=['GET', 'POST'])
@login_required(roles='HR')
def hr_tasks():
    user_id = session['user_id']
    active_company_id = session.get('active_company_id')
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
        
    tasks = conn.execute('SELECT * FROM tasks WHERE assigned_to = ? AND company_id = ?', (user_id, active_company_id)).fetchall()
    conn.close()
    
    users = get_visible_users(user_id, active_company_id)
    
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
@login_required(roles='HR')
def hr_jobs():
    user_id = session['user_id']
    active_company_id = session.get('active_company_id')
    conn = get_db_connection()
    
    if request.method == 'POST':
        title = request.form['title']
        department = request.form['department']
        description = request.form['description']
        
        conn.execute('INSERT INTO jobs (title, department, description, created_by, company_id) VALUES (?, ?, ?, ?, ?)',
                     (title, department, description, user_id, active_company_id))
        conn.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('hr_jobs'))
        
    jobs = conn.execute('SELECT jobs.*, users.name as creator FROM jobs JOIN users ON jobs.created_by = users.id WHERE jobs.company_id = ?', (active_company_id,)).fetchall()
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
    active_company_id = session.get('active_company_id')
    if attachment_path:
        conn.execute('INSERT INTO tasks (title, description, assigned_to, priority, deadline, attachment_path, company_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (title, description, assigned_to, priority, deadline, attachment_path, active_company_id))
    else:
        conn.execute('INSERT INTO tasks (title, description, assigned_to, priority, deadline, company_id) VALUES (?, ?, ?, ?, ?, ?)',
                     (title, description, assigned_to, priority, deadline, active_company_id))
    
    conn.execute('INSERT INTO notifications (user_id, message, company_id) VALUES (?, ?, ?)',
                 (assigned_to, f"You have been assigned a new task: {title}", active_company_id))
    
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
@login_required(roles='Employee')
def employee_dashboard():
    conn = get_db_connection()
    user_id = session['user_id']
    active_company_id = session.get('active_company_id')
    my_tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE assigned_to = ? AND company_id = ?', (user_id, active_company_id)).fetchone()[0]
    pending_tasks = conn.execute('SELECT COUNT(*) FROM tasks WHERE assigned_to = ? AND status != "Completed" AND company_id = ?', (user_id, active_company_id)).fetchone()[0]
    
    recent_tasks = conn.execute('SELECT * FROM tasks WHERE assigned_to = ? AND company_id = ? ORDER BY id DESC LIMIT 5', (user_id, active_company_id)).fetchall()
    conn.close()
    
    return render_template('dashboard_employee.html', 
                           my_tasks=my_tasks, 
                           pending_tasks=pending_tasks, 
                           recent_tasks=recent_tasks)

@app.route('/employee/tasks', methods=['GET', 'POST'])
@login_required(roles='Employee')
def employee_tasks():
    user_id = session['user_id']
    active_company_id = session.get('active_company_id')
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
        
    tasks = conn.execute('SELECT * FROM tasks WHERE assigned_to = ? AND company_id = ?', (user_id, active_company_id)).fetchall()
    conn.close()
    
    users = get_visible_users(user_id, active_company_id)
    
    return render_template('tasks.html', tasks=tasks, users=users, is_admin=False)

@app.route('/messages', methods=['GET', 'POST'])
@login_required()
def messages():
    user_id = session['user_id']
    active_company_id = session.get('active_company_id')
    conn = get_db_connection()
    
    if request.method == 'POST':
        receiver_id = request.form['receiver_id']
        message_text = request.form['message']
        
        conn.execute('INSERT INTO messages (sender_id, receiver_id, message, company_id) VALUES (?, ?, ?, ?)',
                     (user_id, receiver_id, message_text, active_company_id))
        conn.execute('INSERT INTO notifications (user_id, message, company_id) VALUES (?, ?, ?)',
                     (receiver_id, f"New message from {session.get('name')}", active_company_id))
        conn.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('messages'))
        
    received_msgs = conn.execute('''
        SELECT messages.*, users.name as sender_name 
        FROM messages 
        JOIN users ON messages.sender_id = users.id 
        WHERE receiver_id = ? AND messages.company_id = ?
        ORDER BY timestamp DESC
    ''', (user_id, active_company_id)).fetchall()
    conn.close()
    
    users = get_visible_users(user_id, active_company_id)
    users = [u for u in users if u['id'] != user_id]
    
    return render_template('messages.html', messages=received_msgs, users=users)

# Auto-initialize DB on Render / gunicorn
if not os.path.exists('database.db'):
    init_db()

if __name__ == '__main__':
    app.run(debug=False, port=5000)
