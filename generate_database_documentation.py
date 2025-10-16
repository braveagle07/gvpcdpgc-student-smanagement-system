import os
import django
from django.conf import settings
import sqlite3
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CollegeERP.settings')
django.setup()

from info.models import *

def generate_database_documentation():
    print("Generating comprehensive database documentation...")
    
    # Connect to database for detailed analysis
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Create HTML content for PDF conversion
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>College ERP Database Documentation</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
                border-bottom: 3px solid #3498db;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            h2 {{
                color: #34495e;
                background: #ecf0f1;
                padding: 15px;
                border-left: 5px solid #3498db;
                margin-top: 30px;
            }}
            h3 {{
                color: #2c3e50;
                border-bottom: 2px solid #bdc3c7;
                padding-bottom: 10px;
            }}
            .table-info {{
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                margin: 15px 0;
            }}
            .field-info {{
                background: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 3px;
                padding: 10px;
                margin: 5px 0;
            }}
            .field-name {{
                font-weight: bold;
                color: #495057;
            }}
            .field-type {{
                color: #6c757d;
                font-style: italic;
            }}
            .field-constraint {{
                color: #dc3545;
                font-weight: bold;
            }}
            .record-count {{
                background: #d4edda;
                color: #155724;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }}
            .summary-stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }}
            .stat-number {{
                font-size: 2em;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .stat-label {{
                font-size: 0.9em;
                opacity: 0.9;
            }}
            .relationship-diagram {{
                background: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                text-align: center;
            }}
            .entity-box {{
                display: inline-block;
                background: #3498db;
                color: white;
                padding: 10px 15px;
                margin: 5px;
                border-radius: 5px;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                margin-top: 50px;
                padding-top: 20px;
                border-top: 2px solid #ecf0f1;
                color: #7f8c8d;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏫 College ERP System - Database Documentation</h1>
            
            <div class="summary-stats">
                <div class="stat-card">
                    <div class="stat-number">{User.objects.count()}</div>
                    <div class="stat-label">Total Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{Student.objects.count()}</div>
                    <div class="stat-label">Students</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{Teacher.objects.count()}</div>
                    <div class="stat-label">Teachers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{Class.objects.count()}</div>
                    <div class="stat-label">Classes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{Course.objects.count()}</div>
                    <div class="stat-label">Courses</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{AssignTime.objects.count()}</div>
                    <div class="stat-label">Timetable Entries</div>
                </div>
            </div>
            
            <h2>📊 Database Overview</h2>
            <p><strong>Generated on:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p><strong>Database Type:</strong> SQLite3</p>
            <p><strong>Total Tables:</strong> 28</p>
            <p><strong>Application Tables:</strong> 12</p>
            <p><strong>Django System Tables:</strong> 16</p>
    """
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    # Application tables (info_*)
    app_tables = [table[0] for table in tables if table[0].startswith('info_')]
    system_tables = [table[0] for table in tables if not table[0].startswith('info_')]
    
    html_content += f"""
            <h2>🗄️ Application Tables (info_*)</h2>
            <p>The following tables contain the core business logic and data for the College ERP system:</p>
    """
    
    # Process application tables
    for table_name in sorted(app_tables):
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Get table description based on model
        table_description = get_table_description(table_name)
        
        html_content += f"""
            <div class="table-info">
                <h3>📋 {table_name}</h3>
                <p><strong>Description:</strong> {table_description}</p>
                <p><strong>Record Count:</strong> <span class="record-count">{count} records</span></p>
                <h4>Fields:</h4>
        """
        
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            constraints = []
            if pk:
                constraints.append("PRIMARY KEY")
            if not_null:
                constraints.append("NOT NULL")
            if default_val is not None:
                constraints.append(f"DEFAULT: {default_val}")
            
            constraint_text = f" <span class='field-constraint'>({', '.join(constraints)})</span>" if constraints else ""
            
            html_content += f"""
                <div class="field-info">
                    <span class="field-name">{col_name}</span> 
                    <span class="field-type">{col_type}</span>{constraint_text}
                </div>
            """
        
        html_content += "</div>"
    
    # Add relationship information
    html_content += """
            <h2>🔗 Entity Relationships</h2>
            <div class="relationship-diagram">
                <h3>Core Entity Relationships</h3>
                <p><strong>User Management:</strong></p>
                <div class="entity-box">User</div> → <div class="entity-box">Student</div>
                <div class="entity-box">User</div> → <div class="entity-box">Teacher</div>
                
                <p><strong>Academic Structure:</strong></p>
                <div class="entity-box">Dept</div> → <div class="entity-box">Course</div>
                <div class="entity-box">Dept</div> → <div class="entity-box">Class</div>
                <div class="entity-box">Class</div> → <div class="entity-box">Student</div>
                
                <p><strong>Teaching Assignments:</strong></p>
                <div class="entity-box">Teacher</div> + <div class="entity-box">Course</div> + <div class="entity-box">Class</div> → <div class="entity-box">Assign</div>
                <div class="entity-box">Assign</div> → <div class="entity-box">AssignTime</div>
                
                <p><strong>Academic Records:</strong></p>
                <div class="entity-box">Student</div> + <div class="entity-box">Course</div> → <div class="entity-box">StudentCourse</div>
                <div class="entity-box">StudentCourse</div> → <div class="entity-box">Marks</div>
                <div class="entity-box">Assign</div> → <div class="entity-box">MarksClass</div>
                
                <p><strong>Attendance System:</strong></p>
                <div class="entity-box">Assign</div> → <div class="entity-box">AttendanceClass</div>
                <div class="entity-box">Student</div> + <div class="entity-box">Course</div> + <div class="entity-box">AttendanceClass</div> → <div class="entity-box">Attendance</div>
                <div class="entity-box">Student</div> + <div class="entity-box">Course</div> → <div class="entity-box">AttendanceTotal</div>
                
                <p><strong>Assignment System:</strong></p>
                <div class="entity-box">Teacher</div> + <div class="entity-box">Course</div> + <div class="entity-box">Class</div> → <div class="entity-box">Assignment</div>
                <div class="entity-box">Student</div> + <div class="entity-box">Assignment</div> → <div class="entity-box">AssignmentSubmission</div>
                <div class="entity-box">Teacher</div> + <div class="entity-box">Course</div> + <div class="entity-box">Class</div> → <div class="entity-box">StudyMaterial</div>
            </div>
    """
    
    # Add sample data section
    html_content += """
            <h2>📝 Sample Data Overview</h2>
    """
    
    # Add sample data for key tables
    key_tables = [
        ('info_dept', 'Departments'),
        ('info_course', 'Courses'),
        ('info_class', 'Classes'),
        ('info_teacher', 'Teachers'),
        ('info_student', 'Students (First 5)'),
        ('info_assign', 'Teaching Assignments'),
        ('info_assigntime', 'Timetable Entries (First 10)')
    ]
    
    for table_name, description in key_tables:
        try:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            
            if rows:
                html_content += f"""
                    <div class="table-info">
                        <h3>{description}</h3>
                        <table border="1" style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                            <tr style="background: #f8f9fa;">
                """
                for col_name in col_names:
                    html_content += f"<th style='padding: 8px; border: 1px solid #dee2e6;'>{col_name}</th>"
                html_content += "</tr>"
                
                for row in rows:
                    html_content += "<tr>"
                    for cell in row:
                        html_content += f"<td style='padding: 8px; border: 1px solid #dee2e6;'>{str(cell) if cell is not None else 'NULL'}</td>"
                    html_content += "</tr>"
                
                html_content += "</table></div>"
        except Exception as e:
            html_content += f"<p>Error loading {description}: {str(e)}</p>"
    
    # Add system tables section
    html_content += """
            <h2>⚙️ Django System Tables</h2>
            <p>The following tables are managed by Django framework:</p>
    """
    
    for table_name in sorted(system_tables):
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        table_description = get_system_table_description(table_name)
        
        html_content += f"""
            <div class="table-info">
                <h3>🔧 {table_name}</h3>
                <p><strong>Description:</strong> {table_description}</p>
                <p><strong>Record Count:</strong> <span class="record-count">{count} records</span></p>
            </div>
        """
    
    # Add technical details
    html_content += f"""
            <h2>🔧 Technical Details</h2>
            <div class="table-info">
                <h3>Database Configuration</h3>
                <p><strong>Engine:</strong> SQLite3</p>
                <p><strong>Location:</strong> db.sqlite3</p>
                <p><strong>Django Version:</strong> 5.2.7</p>
                <p><strong>Python Version:</strong> 3.14.0</p>
                <p><strong>Custom User Model:</strong> info.User</p>
            </div>
            
            <div class="table-info">
                <h3>Key Features</h3>
                <ul>
                    <li>✅ User Authentication & Authorization</li>
                    <li>✅ Student & Teacher Management</li>
                    <li>✅ Course & Class Management</li>
                    <li>✅ Timetable Management</li>
                    <li>✅ Attendance Tracking</li>
                    <li>✅ Marks & Grade Management</li>
                    <li>✅ Assignment System</li>
                    <li>✅ Study Material Management</li>
                    <li>✅ Admin Panel Integration</li>
                    <li>✅ REST API Support</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>Generated by College ERP System Database Documentation Tool</p>
                <p>For technical support, contact the system administrator</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save HTML file
    with open('database_documentation.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    conn.close()
    
    print("Database documentation generated successfully!")
    print("File created: database_documentation.html")
    print("To convert to PDF, open the HTML file in a web browser and use 'Print to PDF'")
    
    return True

def get_table_description(table_name):
    descriptions = {
        'info_user': 'Main user accounts for students, teachers, and administrators with authentication details',
        'info_dept': 'Academic departments in the college (e.g., Computer Science, Electronics)',
        'info_course': 'Individual courses/subjects offered by departments',
        'info_class': 'Class sections with semester information for each department',
        'info_student': 'Student personal information and academic enrollment details',
        'info_teacher': 'Teacher personal information and department assignments',
        'info_assign': 'Teaching assignments linking teachers to courses and classes',
        'info_assigntime': 'Timetable entries specifying when and where classes are conducted',
        'info_attendanceclass': 'Attendance session records for each class meeting',
        'info_attendance': 'Individual student attendance records for each class',
        'info_attendancetotal': 'Aggregated attendance statistics for students per course',
        'info_attendancerange': 'Date range configuration for attendance tracking periods',
        'info_studentcourse': 'Student enrollment records linking students to courses',
        'info_marks': 'Individual marks/grades for students in various assessments',
        'info_marksclass': 'Mark category definitions for different types of assessments',
        'info_assignment': 'Teacher-created assignments with deadlines and requirements',
        'info_assignmentsubmission': 'Student submissions for assignments with grading',
        'info_studymaterial': 'Educational resources shared by teachers with students'
    }
    return descriptions.get(table_name, 'Application data table for College ERP system')

def get_system_table_description(table_name):
    descriptions = {
        'django_migrations': 'Database migration history tracking schema changes',
        'django_content_type': 'Content type definitions for Django models',
        'django_admin_log': 'Administrative action logs for audit trail',
        'django_session': 'User session data for maintaining login state',
        'auth_permission': 'System permissions for user access control',
        'auth_group': 'User groups for role-based access control',
        'auth_group_permissions': 'Many-to-many relationship between groups and permissions',
        'info_user_groups': 'Many-to-many relationship between users and groups',
        'info_user_user_permissions': 'Many-to-many relationship between users and permissions',
        'authtoken_token': 'API authentication tokens for REST API access',
        'sqlite_sequence': 'SQLite internal sequence tracking for auto-increment fields'
    }
    return descriptions.get(table_name, 'Django framework system table')

if __name__ == "__main__":
    generate_database_documentation()
