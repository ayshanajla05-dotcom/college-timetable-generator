from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


# ------------------------
# Department
# ------------------------

class Department(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return self.name


# ------------------------
# Faculty
# ------------------------

class Faculty(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    faculty_name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100))

    phone = db.Column(db.String(20))

    max_hours = db.Column(db.Integer)

    department_id = db.Column(
        db.Integer,
        db.ForeignKey('department.id')
    )

    department = db.relationship('Department')
    def __repr__(self):
        return self.faculty_name


# ------------------------
# Subject
# ------------------------

class Subject(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    subject_code = db.Column(db.String(20), unique=True, nullable=False)

    subject_name = db.Column(db.String(100), nullable=False)

    semester = db.Column(db.Integer, nullable=False)

    hours_per_week = db.Column(db.Integer, nullable=False)

    subject_type = db.Column(db.String(20), nullable=False)   # Theory / Lab

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("department.id"),
        nullable=False
    )

    faculty_id = db.Column(
        db.Integer,
        db.ForeignKey("faculty.id"),
        nullable=False
    )

    department = db.relationship("Department")

    faculty = db.relationship("Faculty")

# ------------------------
# Room
# ------------------------

class Room(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    room_number = db.Column(db.String(20), unique=True, nullable=False)

    room_type = db.Column(db.String(20), nullable=False)   # Classroom / Lab

    capacity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return self.room_number


# ------------------------
# Section
# ------------------------

class Section(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    section_name = db.Column(db.String(20), nullable=False)

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("department.id")
    )

    semester = db.Column(db.Integer)

    strength = db.Column(db.Integer)

    department = db.relationship("Department")

    def __repr__(self):
        return self.section_name


# ------------------------
# Timetable
# ------------------------

class Timetable(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    day_order = db.Column(db.String(10))

    period = db.Column(db.Integer)

    section_id = db.Column(
        db.Integer,
        db.ForeignKey("section.id")
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subject.id")
    )

    faculty_id = db.Column(
        db.Integer,
        db.ForeignKey("faculty.id")
    )

    room_id = db.Column(
        db.Integer,
        db.ForeignKey("room.id")
    )

    section = db.relationship("Section")
    subject = db.relationship("Subject")
    faculty = db.relationship("Faculty")
    room = db.relationship("Room")

class Admin(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True)

    password = db.Column(db.String(100))