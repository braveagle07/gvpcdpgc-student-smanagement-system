import os
import webbrowser
from datetime import datetime

def convert_html_to_pdf():
    """
    Convert the HTML documentation to PDF using browser automation
    """
    print("Converting HTML documentation to PDF...")
    
    # Get the current directory
    current_dir = os.getcwd()
    html_file = os.path.join(current_dir, 'database_documentation.html')
    
    if not os.path.exists(html_file):
        print("Error: database_documentation.html not found!")
        return False
    
    # Open the HTML file in the default browser
    print(f"Opening {html_file} in your default browser...")
    webbrowser.open(f'file://{html_file}')
    
    print("\n" + "="*60)
    print("PDF CONVERSION INSTRUCTIONS:")
    print("="*60)
    print("1. The HTML file should now be open in your browser")
    print("2. Press Ctrl+P (or Cmd+P on Mac) to open the print dialog")
    print("3. In the print dialog:")
    print("   - Select 'Save as PDF' as the destination")
    print("   - Choose 'More settings' and set:")
    print("     * Paper size: A4 or Letter")
    print("     * Margins: Minimum or None")
    print("     * Scale: 100%")
    print("     * Background graphics: ON (to preserve colors)")
    print("4. Click 'Save' and choose a location for your PDF")
    print("5. The PDF will be generated with all the database documentation")
    print("="*60)
    
    # Also create a simple text version
    create_text_summary()
    
    return True

def create_text_summary():
    """
    Create a simple text summary of the database structure
    """
    print("\nCreating text summary...")
    
    summary_content = f"""
COLLEGE ERP SYSTEM - DATABASE DOCUMENTATION SUMMARY
Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

DATABASE OVERVIEW:
==================
- Database Type: SQLite3
- Total Tables: 28
- Application Tables: 12
- Django System Tables: 16

APPLICATION TABLES (info_*):
============================
1. info_user - Main user accounts (students, teachers, admins)
2. info_dept - Academic departments
3. info_course - Individual courses/subjects
4. info_class - Class sections with semester info
5. info_student - Student personal information
6. info_teacher - Teacher personal information
7. info_assign - Teaching assignments (teacher + course + class)
8. info_assigntime - Timetable entries (when/where classes happen)
9. info_attendanceclass - Attendance session records
10. info_attendance - Individual student attendance
11. info_attendancetotal - Aggregated attendance statistics
12. info_attendancerange - Date range configuration
13. info_studentcourse - Student enrollment records
14. info_marks - Individual marks/grades
15. info_marksclass - Mark category definitions
16. info_assignment - Teacher-created assignments
17. info_assignmentsubmission - Student assignment submissions
18. info_studymaterial - Educational resources

DJANGO SYSTEM TABLES:
=====================
- django_migrations - Schema change history
- django_content_type - Model content types
- django_admin_log - Admin action logs
- django_session - User session data
- auth_permission - System permissions
- auth_group - User groups
- auth_group_permissions - Group-permission relationships
- info_user_groups - User-group relationships
- info_user_user_permissions - User-permission relationships
- authtoken_token - API authentication tokens
- sqlite_sequence - Auto-increment sequence tracking

KEY RELATIONSHIPS:
==================
- User → Student/Teacher (one-to-one)
- Dept → Course/Class (one-to-many)
- Teacher + Course + Class → Assign (many-to-many)
- Assign → AssignTime (one-to-many)
- Student + Course → StudentCourse (many-to-many)
- StudentCourse → Marks (one-to-many)
- Assign → AttendanceClass (one-to-many)
- Student + AttendanceClass → Attendance (many-to-many)
- Teacher + Course + Class → Assignment (one-to-many)
- Student + Assignment → AssignmentSubmission (many-to-many)

FEATURES:
=========
✓ User Authentication & Authorization
✓ Student & Teacher Management
✓ Course & Class Management
✓ Timetable Management
✓ Attendance Tracking
✓ Marks & Grade Management
✓ Assignment System
✓ Study Material Management
✓ Admin Panel Integration
✓ REST API Support

For detailed field information, constraints, and sample data,
please refer to the HTML documentation file.
"""
    
    with open('database_summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print("Text summary created: database_summary.txt")

if __name__ == "__main__":
    convert_html_to_pdf()
