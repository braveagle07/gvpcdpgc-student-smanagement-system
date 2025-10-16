from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse
from .models import Dept, Class, Student, Attendance, Course, Teacher, Assign, AttendanceTotal, time_slots, \
    DAYS_OF_WEEK, AssignTime, AttendanceClass, StudentCourse, Marks, MarksClass, Assignment, AssignmentSubmission, StudyMaterial
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model


User = get_user_model()

# Create your views here.


@login_required
def index(request):
    if request.user.is_teacher:
        return render(request, 'info/t_homepage.html')
    if request.user.is_student:
        return render(request, 'info/homepage.html')
    if request.user.is_superuser:
        return render(request, 'info/admin_page.html')
    return render(request, 'info/logout.html')


@login_required()
def attendance(request, stud_id):
    stud = Student.objects.get(USN=stud_id)
    ass_list = Assign.objects.filter(class_id_id=stud.class_id)
    att_list = []
    for ass in ass_list:
        try:
            a = AttendanceTotal.objects.get(student=stud, course=ass.course)
        except AttendanceTotal.DoesNotExist:
            a = AttendanceTotal(student=stud, course=ass.course)
            a.save()
        att_list.append(a)
    return render(request, 'info/attendance.html', {'att_list': att_list})


@login_required()
def attendance_detail(request, stud_id, course_id):
    stud = get_object_or_404(Student, USN=stud_id)
    cr = get_object_or_404(Course, id=course_id)
    att_list = Attendance.objects.filter(course=cr, student=stud).order_by('date')
    return render(request, 'info/att_detail.html', {'att_list': att_list, 'cr': cr})


# Teacher Views

@login_required
def t_clas(request, teacher_id, choice):
    teacher1 = get_object_or_404(Teacher, id=teacher_id)
    return render(request, 'info/t_clas.html', {'teacher1': teacher1, 'choice': choice})


@login_required()
def t_student(request, assign_id):
    ass = Assign.objects.get(id=assign_id)
    att_list = []
    for stud in ass.class_id.student_set.all():
        try:
            a = AttendanceTotal.objects.get(student=stud, course=ass.course)
        except AttendanceTotal.DoesNotExist:
            a = AttendanceTotal(student=stud, course=ass.course)
            a.save()
        att_list.append(a)
    return render(request, 'info/t_students.html', {'att_list': att_list})


@login_required()
def t_class_date(request, assign_id):
    now = timezone.now()
    ass = get_object_or_404(Assign, id=assign_id)
    att_list = ass.attendanceclass_set.filter(date__lte=now).order_by('-date')
    return render(request, 'info/t_class_date.html', {'att_list': att_list})


@login_required()
def cancel_class(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    assc.status = 2
    assc.save()
    return HttpResponseRedirect(reverse('t_class_date', args=(assc.assign_id,)))


@login_required()
def t_attendance(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    ass = assc.assign
    c = ass.class_id
    context = {
        'ass': ass,
        'c': c,
        'assc': assc,
    }
    return render(request, 'info/t_attendance.html', context)


@login_required()
def edit_att(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    cr = assc.assign.course
    att_list = Attendance.objects.filter(attendanceclass=assc, course=cr)
    context = {
        'assc': assc,
        'att_list': att_list,
    }
    return render(request, 'info/t_edit_att.html', context)


@login_required()
def confirm(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    ass = assc.assign
    cr = ass.course
    cl = ass.class_id
    for i, s in enumerate(cl.student_set.all()):
        status = request.POST[s.USN]
        if status == 'present':
            status = 'True'
        else:
            status = 'False'
        if assc.status == 1:
            try:
                a = Attendance.objects.get(course=cr, student=s, date=assc.date, attendanceclass=assc)
                a.status = status
                a.save()
            except Attendance.DoesNotExist:
                a = Attendance(course=cr, student=s, status=status, date=assc.date, attendanceclass=assc)
                a.save()
        else:
            a = Attendance(course=cr, student=s, status=status, date=assc.date, attendanceclass=assc)
            a.save()
            assc.status = 1
            assc.save()

    return HttpResponseRedirect(reverse('t_class_date', args=(ass.id,)))


@login_required()
def t_attendance_detail(request, stud_id, course_id):
    stud = get_object_or_404(Student, USN=stud_id)
    cr = get_object_or_404(Course, id=course_id)
    att_list = Attendance.objects.filter(course=cr, student=stud).order_by('date')
    return render(request, 'info/t_att_detail.html', {'att_list': att_list, 'cr': cr})


@login_required()
def change_att(request, att_id):
    a = get_object_or_404(Attendance, id=att_id)
    a.status = not a.status
    a.save()
    return HttpResponseRedirect(reverse('t_attendance_detail', args=(a.student.USN, a.course_id)))


@login_required()
def t_extra_class(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    c = ass.class_id
    context = {
        'ass': ass,
        'c': c,
    }
    return render(request, 'info/t_extra_class.html', context)


@login_required()
def e_confirm(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    cr = ass.course
    cl = ass.class_id
    assc = ass.attendanceclass_set.create(status=1, date=request.POST['date'])
    assc.save()

    for i, s in enumerate(cl.student_set.all()):
        status = request.POST[s.USN]
        if status == 'present':
            status = 'True'
        else:
            status = 'False'
        date = request.POST['date']
        a = Attendance(course=cr, student=s, status=status, date=date, attendanceclass=assc)
        a.save()

    return HttpResponseRedirect(reverse('t_clas', args=(ass.teacher_id, 1)))


@login_required()
def t_report(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    sc_list = []
    for stud in ass.class_id.student_set.all():
        a = StudentCourse.objects.get(student=stud, course=ass.course)
        sc_list.append(a)
    return render(request, 'info/t_report.html', {'sc_list': sc_list})


@login_required()
def timetable(request, class_id):
    asst = AssignTime.objects.filter(assign__class_id=class_id)
    matrix = [['' for i in range(12)] for j in range(6)]

    for i, d in enumerate(DAYS_OF_WEEK):
        t = 0
        for j in range(12):
            if j == 0:
                matrix[i][0] = d[0]
                continue
            if j == 4 or j == 8:
                continue
            try:
                # Get the first assignment for this period and day
                a = asst.filter(period=time_slots[t][0], day=d[0]).first()
                if a:
                    matrix[i][j] = a.assign.course_id
            except:
                pass
            t += 1

    context = {'matrix': matrix}
    return render(request, 'info/timetable.html', context)


@login_required()
def t_timetable(request, teacher_id):
    asst = AssignTime.objects.filter(assign__teacher_id=teacher_id)
    class_matrix = [[True for i in range(12)] for j in range(6)]
    for i, d in enumerate(DAYS_OF_WEEK):
        t = 0
        for j in range(12):
            if j == 0:
                class_matrix[i][0] = d[0]
                continue
            if j == 4 or j == 8:
                continue
            try:
                # Get the first assignment for this period and day
                # Since a teacher can teach multiple classes, we'll show the first one
                a = asst.filter(period=time_slots[t][0], day=d[0]).first()
                if a:
                    class_matrix[i][j] = a
            except:
                pass
            t += 1

    context = {
        'class_matrix': class_matrix,
    }
    return render(request, 'info/t_timetable.html', context)


# Timetable Management Views
@login_required()
def manage_timetable(request, class_id):
    """Admin view to manage timetable for a specific class"""
    if not request.user.is_superuser:
        return redirect('index')
    
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.method == 'POST':
        # Handle timetable updates
        for day in DAYS_OF_WEEK:
            for time_slot in time_slots:
                period = time_slot[0]
                day_name = day[0]
                
                # Get the assignment ID from the form
                assign_id = request.POST.get(f'{day_name}_{period}')
                
                if assign_id and assign_id != '':
                    try:
                        assign = get_object_or_404(Assign, id=assign_id)
                        # Create or update AssignTime
                        assign_time, created = AssignTime.objects.get_or_create(
                            assign=assign,
                            period=period,
                            day=day_name
                        )
                    except:
                        pass
                else:
                    # Remove existing assignment for this slot
                    AssignTime.objects.filter(
                        assign__class_id=class_obj,
                        period=period,
                        day=day_name
                    ).delete()
        
        return redirect('manage_timetable', class_id=class_id)
    
    # Get current timetable
    current_timetable = {}
    for assign_time in AssignTime.objects.filter(assign__class_id=class_obj):
        key = f"{assign_time.day}_{assign_time.period}"
        current_timetable[key] = assign_time.assign.id
    
    # Get all assignments for this class
    assignments = Assign.objects.filter(class_id=class_obj)
    
    context = {
        'class_obj': class_obj,
        'assignments': assignments,
        'current_timetable': current_timetable,
        'time_slots': time_slots,
        'days': DAYS_OF_WEEK,
    }
    return render(request, 'info/manage_timetable.html', context)


@login_required()
def admin_timetable_list(request):
    """Admin view to list all classes for timetable management"""
    if not request.user.is_superuser:
        return redirect('index')
    
    classes = Class.objects.all().order_by('dept__name', 'sem', 'section')
    
    context = {
        'classes': classes,
    }
    return render(request, 'info/admin_timetable_list.html', context)


@login_required()
def free_teachers(request, asst_id):
    asst = get_object_or_404(AssignTime, id=asst_id)
    ft_list = []
    t_list = Teacher.objects.filter(assign__class_id__id=asst.assign.class_id_id)
    for t in t_list:
        at_list = AssignTime.objects.filter(assign__teacher=t)
        if not any([True if at.period == asst.period and at.day == asst.day else False for at in at_list]):
            ft_list.append(t)

    return render(request, 'info/free_teachers.html', {'ft_list': ft_list})


# student marks


@login_required()
def marks_list(request, stud_id):
    stud = Student.objects.get(USN=stud_id, )
    ass_list = Assign.objects.filter(class_id_id=stud.class_id)
    sc_list = []
    for ass in ass_list:
        try:
            sc = StudentCourse.objects.get(student=stud, course=ass.course)
        except StudentCourse.DoesNotExist:
            sc = StudentCourse(student=stud, course=ass.course)
            sc.save()
            sc.marks_set.create(type='I', name='Internal test 1')
            sc.marks_set.create(type='I', name='Internal test 2')
            sc.marks_set.create(type='I', name='Internal test 3')
            sc.marks_set.create(type='E', name='Event 1')
            sc.marks_set.create(type='E', name='Event 2')
            sc.marks_set.create(type='S', name='Semester End Exam')
        sc_list.append(sc)

    return render(request, 'info/marks_list.html', {'sc_list': sc_list})


# teacher marks


@login_required()
def t_marks_list(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    
    # Check if the current user is the teacher assigned to this course
    if not request.user.is_teacher or ass.teacher.user != request.user:
        return redirect('index')
    
    m_list = MarksClass.objects.filter(assign=ass)
    return render(request, 'info/t_marks_list.html', {'m_list': m_list})


@login_required()
def t_marks_entry(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    ass = mc.assign
    
    # Check if the current user is the teacher assigned to this course
    if not request.user.is_teacher or ass.teacher.user != request.user:
        return redirect('index')
    
    c = ass.class_id
    context = {
        'ass': ass,
        'c': c,
        'mc': mc,
    }
    return render(request, 'info/t_marks_entry.html', context)


@login_required()
def marks_confirm(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    ass = mc.assign
    
    # Check if the current user is the teacher assigned to this course
    if not request.user.is_teacher or ass.teacher.user != request.user:
        return redirect('index')
    
    cr = ass.course
    cl = ass.class_id
    for s in cl.student_set.all():
        mark = request.POST[s.USN]
        sc = StudentCourse.objects.get(course=cr, student=s)
        m = sc.marks_set.get(name=mc.name)
        m.marks1 = mark
        m.save()
    mc.status = True
    mc.save()

    return HttpResponseRedirect(reverse('t_marks_list', args=(ass.id,)))


@login_required()
def edit_marks(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    ass = mc.assign
    
    # Check if the current user is the teacher assigned to this course
    if not request.user.is_teacher or ass.teacher.user != request.user:
        return redirect('index')
    
    cr = mc.assign.course
    stud_list = mc.assign.class_id.student_set.all()
    m_list = []
    for stud in stud_list:
        sc = StudentCourse.objects.get(course=cr, student=stud)
        m = sc.marks_set.get(name=mc.name)
        m_list.append(m)
    context = {
        'mc': mc,
        'm_list': m_list,
    }
    return render(request, 'info/edit_marks.html', context)


@login_required()
def student_marks(request, assign_id):
    ass = Assign.objects.get(id=assign_id)
    
    # Check if the current user is the teacher assigned to this course
    if not request.user.is_teacher or ass.teacher.user != request.user:
        return redirect('index')
    
    sc_list = StudentCourse.objects.filter(student__in=ass.class_id.student_set.all(), course=ass.course)
    return render(request, 'info/t_student_marks.html', {'sc_list': sc_list})


@login_required()
def add_teacher(request):
    if not request.user.is_superuser:
        return redirect("/")

    if request.method == 'POST':
        dept = get_object_or_404(Dept, id=request.POST['dept'])
        name = request.POST['full_name']
        id = request.POST['id'].lower()
        dob = request.POST['dob']
        sex = request.POST['sex']
        
        # Creating a User with teacher username and password format
        # USERNAME: firstname + underscore + unique ID
        # PASSWORD: firstname + underscore + year of birth(YYYY)
        user = User.objects.create_user(
            username=name.split(" ")[0].lower() + '_' + id,
            password=name.split(" ")[0].lower() + '_' + dob.replace("-","")[:4]
        )
        user.save()

        Teacher(
            user=user,
            id=id,
            dept=dept,
            name=name,
            sex=sex,
            DOB=dob
        ).save()
        return redirect('/')
    
    all_dept = Dept.objects.order_by('-id')
    context = {'all_dept': all_dept}

    return render(request, 'info/add_teacher.html', context)


@login_required()
def add_student(request):
    # If the user is not admin, they will be redirected to home
    if not request.user.is_superuser:
        return redirect("/")

    if request.method == 'POST':
        # Retrieving all the form data that has been inputted
        class_id = get_object_or_404(Class, id=request.POST['class'])
        name = request.POST['full_name']
        usn = request.POST['usn']
        dob = request.POST['dob']
        sex = request.POST['sex'] 

        # Creating a User with student username and password format
        # USERNAME: firstname + underscore + last 3 digits of USN
        # PASSWORD: firstname + underscore + year of birth(YYYY)
        user = User.objects.create_user(
            username=name.split(" ")[0].lower() + '_' + request.POST['usn'][-3:],
            password=name.split(" ")[0].lower() + '_' + dob.replace("-","")[:4]
        )
        user.save()

        # Creating a new student instance with given data and saving it.
        Student(
            user=user,
            USN=usn,
            class_id=class_id,
            name=name,
            sex=sex,
            DOB=dob
        ).save()
        return redirect('/')
    
    all_classes = Class.objects.order_by('-id')
    context = {'all_classes': all_classes}
    return render(request, 'info/add_student.html', context)


# Assignment Views for Teachers
@login_required()
def teacher_assignments(request, teacher_id):
    if not request.user.is_teacher:
        return redirect('index')
    
    teacher = get_object_or_404(Teacher, id=teacher_id)
    assignments = Assignment.objects.filter(teacher=teacher, is_active=True).order_by('-created_at')
    
    context = {
        'teacher': teacher,
        'assignments': assignments,
    }
    return render(request, 'info/t_assignments.html', context)


@login_required()
def create_assignment(request, teacher_id):
    if not request.user.is_teacher:
        return redirect('index')
    
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        course_id = request.POST.get('course')
        class_id = request.POST.get('class_id')
        due_date = request.POST.get('due_date')
        max_marks = request.POST.get('max_marks', 100)
        
        # Verify that the teacher is assigned to this class and course
        assign_obj = get_object_or_404(Assign, teacher=teacher, class_id=class_id, course=course_id)
        course = assign_obj.course
        class_obj = assign_obj.class_id
        
        assignment = Assignment.objects.create(
            title=title,
            description=description,
            course=course,
            teacher=teacher,
            class_id=class_obj,
            due_date=due_date,
            max_marks=max_marks
        )
        
        return redirect('teacher_assignments', teacher_id=teacher_id)
    
    # Get teacher's assigned classes and courses
    assigned_classes = Assign.objects.filter(teacher=teacher).values_list('class_id', flat=True).distinct()
    classes = Class.objects.filter(id__in=assigned_classes)
    
    # Get teacher's assignments for context
    teacher_assignments = Assign.objects.filter(teacher=teacher).select_related('class_id', 'course')
    
    context = {
        'teacher': teacher,
        'classes': classes,
        'teacher_assignments': teacher_assignments,
    }
    return render(request, 'info/t_create_assignment.html', context)


@login_required()
def assignment_submissions(request, teacher_id, assignment_id):
    if not request.user.is_teacher:
        return redirect('index')
    
    teacher = get_object_or_404(Teacher, id=teacher_id)
    assignment = get_object_or_404(Assignment, id=assignment_id, teacher=teacher)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment).order_by('-submitted_at')
    
    context = {
        'teacher': teacher,
        'assignment': assignment,
        'submissions': submissions,
    }
    return render(request, 'info/t_assignment_submissions.html', context)


@login_required()
def grade_assignment(request, teacher_id, submission_id):
    if not request.user.is_teacher:
        return redirect('index')
    
    teacher = get_object_or_404(Teacher, id=teacher_id)
    submission = get_object_or_404(AssignmentSubmission, id=submission_id, assignment__teacher=teacher)
    
    if request.method == 'POST':
        marks_obtained = request.POST.get('marks_obtained')
        feedback = request.POST.get('feedback')
        
        submission.marks_obtained = marks_obtained
        submission.feedback = feedback
        submission.save()
        
        return redirect('assignment_submissions', teacher_id=teacher_id, assignment_id=submission.assignment.id)
    
    context = {
        'teacher': teacher,
        'submission': submission,
    }
    return render(request, 'info/t_grade_assignment.html', context)


# Study Material Views for Teachers
@login_required()
def teacher_study_materials(request, teacher_id):
    if not request.user.is_teacher:
        return redirect('index')
    
    teacher = get_object_or_404(Teacher, id=teacher_id)
    materials = StudyMaterial.objects.filter(teacher=teacher, is_active=True).order_by('-created_at')
    
    context = {
        'teacher': teacher,
        'materials': materials,
    }
    return render(request, 'info/t_study_materials.html', context)


@login_required()
def create_study_material(request, teacher_id):
    if not request.user.is_teacher:
        return redirect('index')
    
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        material_type = request.POST.get('material_type')
        course_id = request.POST.get('course')
        class_id = request.POST.get('class_id')
        content = request.POST.get('content', '')
        external_link = request.POST.get('external_link', '')
        
        # Verify that the teacher is assigned to this class and course
        assign_obj = get_object_or_404(Assign, teacher=teacher, class_id=class_id, course=course_id)
        course = assign_obj.course
        class_obj = assign_obj.class_id
        
        material = StudyMaterial.objects.create(
            title=title,
            description=description,
            material_type=material_type,
            course=course,
            teacher=teacher,
            class_id=class_obj,
            content=content,
            external_link=external_link
        )
        
        # Handle file upload if provided
        if 'file_upload' in request.FILES:
            material.file_upload = request.FILES['file_upload']
            material.save()
        
        return redirect('teacher_study_materials', teacher_id=teacher_id)
    
    # Get teacher's assigned classes and courses
    assigned_classes = Assign.objects.filter(teacher=teacher).values_list('class_id', flat=True).distinct()
    classes = Class.objects.filter(id__in=assigned_classes)
    
    # Get teacher's assignments for context
    teacher_assignments = Assign.objects.filter(teacher=teacher).select_related('class_id', 'course')
    
    context = {
        'teacher': teacher,
        'classes': classes,
        'teacher_assignments': teacher_assignments,
    }
    return render(request, 'info/t_create_study_material.html', context)


# Assignment Views for Students
@login_required()
def student_assignments(request, student_id):
    if not request.user.is_student:
        return redirect('index')
    
    student = get_object_or_404(Student, USN=student_id)
    
    # Get assignments for student's class
    assignments = Assignment.objects.filter(class_id=student.class_id, is_active=True).order_by('-created_at')
    
    # Get submission status for each assignment
    assignment_data = []
    for assignment in assignments:
        try:
            submission = AssignmentSubmission.objects.get(assignment=assignment, student=student)
            assignment_data.append({
                'assignment': assignment,
                'submission': submission,
                'is_submitted': submission.is_submitted,
                'marks_obtained': submission.marks_obtained,
                'feedback': submission.feedback
            })
        except AssignmentSubmission.DoesNotExist:
            assignment_data.append({
                'assignment': assignment,
                'submission': None,
                'is_submitted': False,
                'marks_obtained': None,
                'feedback': None
            })
    
    context = {
        'student': student,
        'assignment_data': assignment_data,
        'now': timezone.now(),
    }
    return render(request, 'info/student_assignments.html', context)


@login_required()
def submit_assignment(request, student_id, assignment_id):
    if not request.user.is_student:
        return redirect('index')
    
    student = get_object_or_404(Student, USN=student_id)
    assignment = get_object_or_404(Assignment, id=assignment_id, class_id=student.class_id)
    
    # Check if already submitted
    try:
        submission = AssignmentSubmission.objects.get(assignment=assignment, student=student)
        if submission.is_submitted:
            return redirect('student_assignments', student_id=student_id)
    except AssignmentSubmission.DoesNotExist:
        submission = None
    
    if request.method == 'POST':
        submission_text = request.POST.get('submission_text', '')
        
        if submission:
            submission.submission_text = submission_text
            submission.is_submitted = True
            if 'submission_file' in request.FILES:
                submission.submission_file = request.FILES['submission_file']
            submission.save()
        else:
            submission = AssignmentSubmission.objects.create(
                assignment=assignment,
                student=student,
                submission_text=submission_text,
                is_submitted=True
            )
            if 'submission_file' in request.FILES:
                submission.submission_file = request.FILES['submission_file']
                submission.save()
        
        return redirect('student_assignments', student_id=student_id)
    
    context = {
        'student': student,
        'assignment': assignment,
        'submission': submission,
    }
    return render(request, 'info/submit_assignment.html', context)


# Study Material Views for Students
@login_required()
def student_study_materials(request, student_id):
    if not request.user.is_student:
        return redirect('index')
    
    student = get_object_or_404(Student, USN=student_id)
    materials = StudyMaterial.objects.filter(class_id=student.class_id, is_active=True).order_by('-created_at')
    
    context = {
        'student': student,
        'materials': materials,
    }
    return render(request, 'info/student_study_materials.html', context)


# API Views
@login_required()
def get_courses_for_class(request, class_id):
    """API endpoint to get courses for a specific class"""
    try:
        class_obj = get_object_or_404(Class, id=class_id)
        # Get courses through the Assign table (teacher-class-course relationships)
        assignments = Assign.objects.filter(class_id=class_obj).select_related('course')
        courses = []
        for assignment in assignments:
            courses.append({
                'id': assignment.course.id,
                'name': assignment.course.name,
                'shortname': assignment.course.shortname
            })
        return JsonResponse({
            'courses': courses
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)