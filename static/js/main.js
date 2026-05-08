// Theme Toggle
const themeToggleBtn = document.getElementById('themeToggle');
const htmlRoot = document.getElementById('html-root');

// Check local storage for theme preference
if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    htmlRoot.classList.add('dark');
} else {
    htmlRoot.classList.remove('dark');
}

if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
        if (htmlRoot.classList.contains('dark')) {
            htmlRoot.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        } else {
            htmlRoot.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }
    });
}

// Translations dictionary
const translations = {
    en: {
        brand_name: "HR System",
        nav_dashboard: "Dashboard",
        nav_tasks: "Tasks",
        nav_my_tasks: "My Tasks",
        nav_employees: "Employees",
        nav_jobs: "Job Postings",
        nav_logout: "Logout",
        welcome: "Welcome",
        admin_dash_title: "Overview",
        admin_dash_subtitle: "Track your company's progress and tasks.",
        btn_new_task: "New Task",
        stat_total_tasks: "Total Tasks",
        stat_completed_tasks: "Completed Tasks",
        stat_employees: "Total Employees",
        recent_tasks: "Recent Tasks",
        view_all: "View all",
        th_title: "Task Title",
        th_assignee: "Assignee",
        th_status: "Status",
        th_deadline: "Deadline",
        th_action: "Action",
        th_priority: "Priority",
        no_tasks: "No tasks found.",
        completion_rate: "Completion Rate",
        system_status: "System Status",
        
        hr_dash_title: "HR Dashboard",
        hr_dash_subtitle: "Manage your assigned tasks and active job postings.",
        employee_dash_title: "Employee Dashboard",
        employee_dash_subtitle: "Manage your assigned tasks and communicate with the team.",
        btn_post_job: "Post Job",
        stat_my_tasks: "My Assigned Tasks",
        stat_pending: "Pending Actions",
        stat_active_jobs: "Active Job Posts",
        my_recent_tasks: "My Recent Tasks",
        
        tasks_title: "Task Management",
        tasks_subtitle: "View and manage system tasks.",
        btn_create_task: "Create Task",
        modal_new_task: "Create New Task",
        label_title: "Task Title",
        label_desc: "Description",
        label_assignee: "Assign To",
        label_priority: "Priority",
        label_deadline: "Deadline",
        btn_save: "Save Task",
        btn_cancel: "Cancel",

        jobs_title: "Job Openings",
        jobs_subtitle: "Manage internal and external job postings.",
        no_jobs_title: "No Active Jobs",
        no_jobs_desc: "Get started by creating a new job posting.",
        modal_new_job: "Post New Job",
        label_job_title: "Job Title",
        label_department: "Department",
        btn_publish: "Publish Job",
        
        employees_title: "Employees Directory",
        employees_subtitle: "View all registered staff members.",
        no_employees: "No employees found.",
        
        login_title: "Welcome Back",
        login_subtitle: "Sign in to the HR Management Prototype",
        label_email: "Email Address",
        label_password: "Password",
        remember_me: "Remember me",
        forgot_pwd: "Forgot password?",
        btn_login: "Sign in"
    },
    ar: {
        brand_name: "نظام الموارد البشرية",
        nav_dashboard: "لوحة القيادة",
        nav_tasks: "المهام",
        nav_my_tasks: "مهامي",
        nav_employees: "الموظفين",
        nav_jobs: "الوظائف الشاغرة",
        nav_logout: "تسجيل خروج",
        welcome: "مرحباً",
        admin_dash_title: "نظرة عامة",
        admin_dash_subtitle: "تتبع تقدم الشركة والمهام.",
        btn_new_task: "مهمة جديدة",
        stat_total_tasks: "إجمالي المهام",
        stat_completed_tasks: "المهام المنجزة",
        stat_employees: "إجمالي الموظفين",
        recent_tasks: "أحدث المهام",
        view_all: "عرض الكل",
        th_title: "عنوان المهمة",
        th_assignee: "المكلف",
        th_status: "الحالة",
        th_deadline: "الموعد النهائي",
        th_action: "إجراء",
        th_priority: "الأولوية",
        no_tasks: "لا توجد مهام.",
        completion_rate: "معدل الإنجاز",
        system_status: "حالة النظام",
        
        hr_dash_title: "لوحة الموارد البشرية",
        hr_dash_subtitle: "إدارة مهامك وإعلانات الوظائف.",
        employee_dash_title: "لوحة الموظف",
        employee_dash_subtitle: "إدارة المهام المعينة لك والتواصل مع الفريق.",
        btn_post_job: "نشر وظيفة",
        stat_my_tasks: "المهام المسندة لي",
        stat_pending: "إجراءات معلقة",
        stat_active_jobs: "الوظائف النشطة",
        my_recent_tasks: "مهامي الأخيرة",
        
        tasks_title: "إدارة المهام",
        tasks_subtitle: "عرض وإدارة مهام النظام.",
        btn_create_task: "إنشاء مهمة",
        modal_new_task: "إنشاء مهمة جديدة",
        label_title: "عنوان المهمة",
        label_desc: "الوصف",
        label_assignee: "تعيين إلى",
        label_priority: "الأولوية",
        label_deadline: "الموعد النهائي",
        btn_save: "حفظ المهمة",
        btn_cancel: "إلغاء",

        jobs_title: "الوظائف المتاحة",
        jobs_subtitle: "إدارة الإعلانات الوظيفية الداخلية والخارجية.",
        no_jobs_title: "لا توجد وظائف نشطة",
        no_jobs_desc: "ابدأ بإنشاء إعلان وظيفي جديد.",
        modal_new_job: "نشر وظيفة جديدة",
        label_job_title: "المسمى الوظيفي",
        label_department: "القسم",
        btn_publish: "نشر الوظيفة",

        employees_title: "دليل الموظفين",
        employees_subtitle: "عرض جميع أعضاء فريق العمل.",
        no_employees: "لم يتم العثور على موظفين.",
        
        login_title: "مرحباً بعودتك",
        login_subtitle: "قم بتسجيل الدخول إلى نموذج النظام",
        label_email: "البريد الإلكتروني",
        label_password: "كلمة المرور",
        remember_me: "تذكرني",
        forgot_pwd: "نسيت كلمة المرور؟",
        btn_login: "تسجيل الدخول"
    }
};

// Language Toggle
const langToggleBtn = document.getElementById('langToggle');
const langToggleLoginBtn = document.getElementById('langToggleLogin');
let currentLang = localStorage.getItem('lang') || 'en';

function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    htmlRoot.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
    htmlRoot.setAttribute('lang', lang);
    
    // Update texts
    document.querySelectorAll('[data-lang]').forEach(el => {
        const key = el.getAttribute('data-lang');
        if (translations[lang][key]) {
            el.textContent = translations[lang][key];
        }
    });

    // RTL fix for Lucide Icons margin
    if(lang === 'ar') {
        document.querySelectorAll('i[data-lucide]').forEach(icon => {
            if(icon.classList.contains('mr-2')) { icon.classList.remove('mr-2'); icon.classList.add('ml-2'); }
            if(icon.classList.contains('mr-3')) { icon.classList.remove('mr-3'); icon.classList.add('ml-3'); }
        });
    } else {
        document.querySelectorAll('i[data-lucide]').forEach(icon => {
            if(icon.classList.contains('ml-2')) { icon.classList.remove('ml-2'); icon.classList.add('mr-2'); }
            if(icon.classList.contains('ml-3')) { icon.classList.remove('ml-3'); icon.classList.add('mr-3'); }
        });
    }
}

// Initial set
setLanguage(currentLang);

if (langToggleBtn) {
    langToggleBtn.addEventListener('click', () => {
        setLanguage(currentLang === 'en' ? 'ar' : 'en');
    });
}
if (langToggleLoginBtn) {
    langToggleLoginBtn.addEventListener('click', (e) => {
        e.preventDefault();
        setLanguage(currentLang === 'en' ? 'ar' : 'en');
    });
}

// Animated Counters
document.addEventListener('DOMContentLoaded', () => {
    const counters = document.querySelectorAll('.animate-counter');
    const speed = 200;

    counters.forEach(counter => {
        const updateCount = () => {
            const target = +counter.getAttribute('data-target');
            const count = +counter.innerText;
            const inc = target / speed;

            if (count < target) {
                counter.innerText = Math.ceil(count + inc);
                setTimeout(updateCount, 1);
            } else {
                counter.innerText = target;
            }
        };
        updateCount();
    });
});
