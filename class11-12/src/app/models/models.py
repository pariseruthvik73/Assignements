from app import db, login_manager
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from bcrypt import hashpw, checkpw, gensalt
from flask_login import UserMixin


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# Association tables for many-to-many relationships
teacher_courses = db.Table('teacher_courses',
    db.Column('teacher_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

student_courses = db.Table('student_courses',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, teacher, student

    # Relationships for teachers and students
    teaching_courses = db.relationship('Course', secondary=teacher_courses, back_populates='teachers')
    enrolled_courses = db.relationship('Course', secondary=student_courses, back_populates='students')

    def set_password(self, password):
        self.password_hash = hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")

    def check_password(self, password):
        return checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))

    def is_admin(self):
        return self.role == 'admin'

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    attendance = db.relationship("Attendance", backref="student", lazy=True)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(
        db.Date, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    status = db.Column(db.String(10), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)


class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(50), nullable=False)
    session_link = db.Column(db.String(500))
    code_link = db.Column(db.String(500))
    recording_link = db.Column(db.String(500))
    resource_link = db.Column(db.String(500))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=True)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Relationships
    classes = db.relationship("Class", backref="course", lazy=True)
    teachers = db.relationship('User', secondary=teacher_courses, back_populates='teaching_courses')
    students = db.relationship('User', secondary=student_courses, back_populates='enrolled_courses')
