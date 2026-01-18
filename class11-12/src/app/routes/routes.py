from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.models import Student, Attendance, db, Class, Course, User
from app.decorators import admin_required, teacher_required, student_required, admin_or_teacher_required
from datetime import datetime, date

bp = Blueprint("main", __name__)


@bp.route("/health")
def health():
    return {"status": "healthy", "service": "student-attendance-system"}, 200


@bp.route("/")
@login_required
def dashboard():
    # Role-based dashboard routing
    if current_user.is_admin():
        # Admin dashboard - show all courses, users, stats
        total_courses = Course.query.count()
        total_teachers = User.query.filter_by(role='teacher').count()
        total_students_users = User.query.filter_by(role='student').count()
        total_classes = Class.query.count()

        return render_template(
            "admin_dashboard.html",
            total_courses=total_courses,
            total_teachers=total_teachers,
            total_students=total_students_users,
            total_classes=total_classes,
        )

    elif current_user.is_teacher():
        # Teacher dashboard - show their courses and classes
        my_courses = current_user.teaching_courses
        return render_template(
            "teacher_dashboard.html",
            courses=my_courses,
        )

    else:  # Student
        # Student dashboard - show enrolled courses and classes
        my_courses = current_user.enrolled_courses
        return render_template(
            "student_dashboard.html",
            courses=my_courses,
        )


@bp.route("/students")
@login_required
def students():
    students = Student.query.all()
    for student in students:
        total_days = Attendance.query.filter_by(student_id=student.id).count()
        if total_days > 0:
            present_days = Attendance.query.filter_by(
                student_id=student.id, status="Present"
            ).count()
            student.attendance_rate = round(present_days / total_days * 100, 1)
        else:
            student.attendance_rate = 0
    return render_template("students.html", students=students)


@bp.route("/attendance")
@login_required
def attendance():
    selected_date = request.args.get("date", date.today().isoformat())
    students = Student.query.all()

    for student in students:
        student.today_attendance = Attendance.query.filter_by(
            student_id=student.id, date=selected_date
        ).first()

    return render_template(
        "attendance.html", students=students, selected_date=selected_date
    )


@bp.route("/add_student", methods=["POST"])
@login_required
def add_student():
    name = request.form.get("name")
    if name:
        student = Student(name=name)
        db.session.add(student)
        db.session.commit()
        flash("Student added successfully", "success")
    return redirect(url_for("main.students"))


@bp.route("/mark_attendance", methods=["POST"])
@login_required
def mark_attendance():
    try:
        attendance_date = request.form.get("date", date.today().isoformat())
        students = Student.query.all()

        for student in students:
            status = request.form.get(f"status_{student.id}")
            if status:
                # Update existing or create new attendance record
                attendance = Attendance.query.filter_by(
                    student_id=student.id, date=attendance_date
                ).first()

                if attendance:
                    attendance.status = status
                else:
                    attendance = Attendance(
                        student_id=student.id, date=attendance_date, status=status
                    )
                    db.session.add(attendance)

        db.session.commit()
        flash("Attendance marked successfully", "success")
        return redirect(url_for("main.attendance", date=attendance_date))
    except Exception as e:
        flash("Error marking attendance", "error")
        return redirect(url_for("main.attendance"))


@bp.route("/edit_student/<int:id>", methods=["POST"])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    data = request.get_json()
    student.name = data["name"]
    db.session.commit()
    return "", 204


@bp.route("/delete_student/<int:id>", methods=["POST"])
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return "", 204


@bp.route("/classes")
@login_required
def classes():
    classes = Class.query.order_by(Class.date.desc()).all()
    return render_template("classes.html", classes=classes)


@bp.route("/add_class", methods=["GET", "POST"])
@login_required
def add_class():
    if request.method == "POST":
        try:
            new_class = Class(
                date=datetime.strptime(request.form["date"], "%Y-%m-%d").date(),
                time=request.form["time"],
                session_link=request.form["session_link"],
                code_link=request.form["code_link"],
                recording_link=request.form["recording_link"],
                resource_link=request.form["resource_link"],
                remarks=request.form["remarks"],
                created_by=current_user.id,
            )
            db.session.add(new_class)
            db.session.commit()
            flash("Class added successfully!", "success")
            return redirect(url_for("main.classes"))
        except Exception as e:
            flash("Error adding class.", "error")
            return redirect(url_for("main.add_class"))
    return render_template("add_class.html")


@bp.route("/delete_class/<int:id>", methods=["POST"])
@login_required
def delete_class(id):
    class_obj = Class.query.get_or_404(id)
    db.session.delete(class_obj)
    db.session.commit()
    return "", 204


@bp.route("/edit_class/<int:id>", methods=["GET", "POST"])
@login_required
def edit_class(id):
    class_obj = Class.query.get_or_404(id)

    if request.method == "POST":
        try:
            class_obj.date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
            class_obj.time = request.form["time"]
            class_obj.session_link = request.form["session_link"]
            class_obj.code_link = request.form["code_link"]
            class_obj.recording_link = request.form["recording_link"]
            class_obj.resource_link = request.form["resource_link"]
            class_obj.remarks = request.form["remarks"]

            db.session.commit()
            flash("Class updated successfully!", "success")
            return redirect(url_for("main.classes"))
        except Exception as e:
            flash("Error updating class.", "error")

    return render_template("edit_class.html", class_obj=class_obj)


@bp.route("/courses")
@login_required
def courses():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template("courses.html", courses=courses)


@bp.route("/add_course", methods=["GET", "POST"])
@login_required
@admin_required
def add_course():
    if request.method == "POST":
        try:
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")

            new_course = Course(
                name=request.form["name"],
                description=request.form.get("description", ""),
                start_date=datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None,
                end_date=datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None,
                status=request.form.get("status", "Active"),
                created_by=current_user.id,
            )
            db.session.add(new_course)
            db.session.flush()  # Get the course ID

            # Assign teachers
            teacher_ids = request.form.getlist("teachers")
            if teacher_ids:
                teachers = User.query.filter(User.id.in_(teacher_ids), User.role == 'teacher').all()
                new_course.teachers.extend(teachers)

            # Assign students
            student_ids = request.form.getlist("students")
            if student_ids:
                students = User.query.filter(User.id.in_(student_ids), User.role == 'student').all()
                new_course.students.extend(students)

            db.session.commit()
            flash("Course added successfully!", "success")
            return redirect(url_for("main.courses"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding course: {str(e)}", "error")
            return redirect(url_for("main.add_course"))

    # Get all teachers and students for the form
    teachers = User.query.filter_by(role='teacher').all()
    students = User.query.filter_by(role='student').all()
    return render_template("add_course.html", teachers=teachers, students=students)


@bp.route("/edit_course/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_course(id):
    course = Course.query.get_or_404(id)

    if request.method == "POST":
        try:
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")

            course.name = request.form["name"]
            course.description = request.form.get("description", "")
            course.start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
            course.end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
            course.status = request.form.get("status", "Active")

            # Update teachers
            teacher_ids = request.form.getlist("teachers")
            course.teachers = []
            if teacher_ids:
                teachers = User.query.filter(User.id.in_(teacher_ids), User.role == 'teacher').all()
                course.teachers = teachers

            # Update students
            student_ids = request.form.getlist("students")
            course.students = []
            if student_ids:
                students = User.query.filter(User.id.in_(student_ids), User.role == 'student').all()
                course.students = students

            db.session.commit()
            flash("Course updated successfully!", "success")
            return redirect(url_for("main.courses"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating course: {str(e)}", "error")

    # Get all teachers and students for the form
    teachers = User.query.filter_by(role='teacher').all()
    students = User.query.filter_by(role='student').all()
    return render_template("edit_course.html", course=course, teachers=teachers, students=students)


@bp.route("/delete_course/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return "", 204
