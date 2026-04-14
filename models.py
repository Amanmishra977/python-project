from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False) # Admin username, Teacher ID, Student Reg No
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'teacher', 'student'
    name = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course = db.Column(db.String(50), nullable=False) # Btech, Dipolma, MCA, MBA, BBA, BCA
    department = db.Column(db.String(100), nullable=True)
    semester = db.Column(db.Integer, nullable=False)
    parent_email = db.Column(db.String(150), nullable=False)
    fee_fine = db.Column(db.Integer, default=0)
    absent_days = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref=db.backref('student_profile', uselist=False))

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department = db.Column(db.String(100), nullable=True)

    user = db.relationship('User', backref=db.backref('teacher_profile', uselist=False))

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    semester = db.Column(db.Integer, nullable=False)
    subject_name = db.Column(db.String(150), nullable=False)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date, nullable=False)
    time_slot = db.Column(db.String(50), nullable=False) # e.g. "08:30-09:30"
    status = db.Column(db.String(20), nullable=False) # "Present" or "Absent"

    student = db.relationship('Student', backref='attendance_records')
    teacher = db.relationship('Teacher', backref='taken_attendance_records')
    subject = db.relationship('Subject', backref='attendance_records')

class Timetable(db.Model):
    __tablename__ = 'timetable'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    course = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    semester = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False) # e.g. "Monday"
    time_slot = db.Column(db.String(50), nullable=False) # e.g. "08:30-09:30"

    teacher = db.relationship('Teacher', backref='timetables')
    subject = db.relationship('Subject')
