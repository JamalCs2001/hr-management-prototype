# HR Management System Prototype

A modern, responsive HR Management dashboard built with Flask and Tailwind CSS. This prototype demonstrates a complete workflow for internal team collaboration, task delegation, and communication across multiple organizational roles.

## 🚀 Features

* **Multi-Role Authentication**: Distinct dashboards and permissions for **CEO (Admin)**, **HR**, and **Employees**.
* **Task Management**:
  * Create, assign, and track tasks.
  * Support for attaching dual PDF files (Initial Instructions & Final Completion Reports).
  * Quick status updates (Pending, In Progress, Completed).
* **Communication Center**:
  * Real-time internal messaging system between employees.
  * Instant notification bell with unread badges and drop-down alerts for new tasks and messages.
* **Employee Directory**: Manage the team, view employee details, and onboard new staff members.
* **Modern UI/UX**:
  * Stunning Glassmorphism design system using Tailwind CSS.
  * Seamless Dark/Light mode toggle with an animated loading overlay to prevent Flash of Unstyled Content (FOUC).
  * Bilingual support (English / Arabic RTL layout).

## 🛠️ Tech Stack

* **Backend**: Python, Flask
* **Database**: SQLite
* **Frontend**: HTML5, Tailwind CSS (via CDN), Vanilla JavaScript
* **Icons**: Lucide Icons

## 📋 Prerequisites

* Python 3.8+
* Pip (Python package manager)

## ⚙️ Local Setup

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd hr-management-prototype
   ```

2. **Create a virtual environment (Recommended)**
   ```bash
   python -m venv venv
   
   # Activate on Windows:
   venv\Scripts\activate
   
   # Activate on macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install Flask Werkzeug
   ```

4. **Initialize the Database**
   The application will automatically create `database.db` and the required tables when you run it for the first time. The `database.py` file handles the schema and injects default users.

5. **Run the Application**
   ```bash
   python app.py
   ```

6. **Access the Dashboard**
   Open your browser and navigate to: `http://127.0.0.1:5000`

## 🔑 Default Accounts (For Testing)

If you haven't modified the database seed script, you can log in using the following credentials:

| Role | Email | Password |
| :--- | :--- | :--- |
| **CEO/Admin** | `ceo@hotmail.com` | `ceo123456` |
| **HR** | `hr@hotmail.com` | `hr123456` |
| **Employee** | `employee@hotmail.com` | `emp123456` |
| **Accounting** | `acount@hotmail.com` | `ac1233456` |

*(Note: Passwords are hashed using `werkzeug.security` before being stored in the database).*

## 📁 Project Structure

```
hr-management-prototype/
│
├── app.py                 # Main Flask application logic & routes
├── database.py            # SQLite schema definition and initial data seeding
├── static/                # Static assets
│   ├── css/               # Custom CSS overrides
│   ├── js/                # Main JavaScript (Dark mode logic, UI interactions)
│   └── uploads/           # Directory for uploaded Task PDFs
│
├── templates/             # HTML templates (Jinja2)
│   ├── base.html          # Global layout, Sidebar, Header, Notification UI
│   ├── login.html         # Authentication interface
│   ├── dashboard_*.html   # Role-specific dashboards
│   ├── tasks.html         # Unified task management table
│   └── messages.html      # Internal communication UI
│
└── README.md
```

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
