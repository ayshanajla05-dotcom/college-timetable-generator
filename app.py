from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from config import Config
from models import db,Admin,Department, Subject, Faculty, Room, Section, Timetable
from scheduler import generate_timetable
from pdf_export import export_pdf
from excel_export import generate_excel

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(
            username=username,
            password=password
        ).first()

        if admin:
            login_user(admin)
            return redirect(url_for("dashboard"))

        flash("Invalid Username or Password")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(

        "dashboard.html",

        department_count=Department.query.count(),

        faculty_count=Faculty.query.count(),

        subject_count=Subject.query.count(),

        room_count=Room.query.count(),

        section_count=Section.query.count()

    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


with app.app_context():

    db.create_all()

    if not Admin.query.first():

        admin = Admin(
            username="admin",
            password="admin123"
        )

        db.session.add(admin)
        db.session.commit()

@app.route("/departments")
@login_required
def departments():

    search = request.args.get("search", "")

    if search:
        departments = Department.query.filter(
            Department.name.contains(search)
        ).all()
    else:
        departments = Department.query.all()

    return render_template(
        "departments.html",
        departments=departments
    )


@app.route("/add_department", methods=["GET", "POST"])
@login_required
def add_department():

    if request.method == "POST":

        name = request.form["name"]

        department = Department(name=name)

        db.session.add(department)
        db.session.commit()

        flash("Department Added Successfully")

        return redirect(url_for("departments"))

    return render_template("add_department.html")


@app.route("/edit_department/<int:id>", methods=["GET", "POST"])
@login_required
def edit_department(id):

    department = Department.query.get_or_404(id)

    if request.method == "POST":

        department.name = request.form["name"]

        db.session.commit()

        flash("Department Updated")

        return redirect(url_for("departments"))

    return render_template(
        "edit_department.html",
        department=department
    )


@app.route("/delete_department/<int:id>")
@login_required
def delete_department(id):

    department = Department.query.get_or_404(id)

    db.session.delete(department)

    db.session.commit()

    flash("Department Deleted")

    return redirect(url_for("departments"))

@app.route("/faculty")
@login_required
def faculty():

    search = request.args.get("search", "")

    if search:
        faculties = Faculty.query.filter(
            Faculty.faculty_name.contains(search)
        ).all()
    else:
        faculties = Faculty.query.all()

    return render_template(
        "faculty.html",
        faculties=faculties
    )


@app.route("/add_faculty", methods=["GET", "POST"])
@login_required
def add_faculty():

    departments = Department.query.all()

    if request.method == "POST":

        faculty = Faculty(
            faculty_name=request.form["faculty_name"],
            email=request.form["email"],
            phone=request.form["phone"],
            max_hours=request.form["max_hours"],
            department_id=request.form["department_id"]
        )

        db.session.add(faculty)
        db.session.commit()

        flash("Faculty Added Successfully")

        return redirect(url_for("faculty"))

    return render_template(
        "add_faculty.html",
        departments=departments
    )


@app.route("/edit_faculty/<int:id>", methods=["GET", "POST"])
@login_required
def edit_faculty(id):

    faculty = Faculty.query.get_or_404(id)
    departments = Department.query.all()

    if request.method == "POST":

        faculty.faculty_name = request.form["faculty_name"]
        faculty.email = request.form["email"]
        faculty.phone = request.form["phone"]
        faculty.max_hours = request.form["max_hours"]
        faculty.department_id = request.form["department_id"]

        db.session.commit()

        flash("Faculty Updated Successfully")

        return redirect(url_for("faculty"))

    return render_template(
        "edit_faculty.html",
        faculty=faculty,
        departments=departments
    )


@app.route("/delete_faculty/<int:id>")
@login_required
def delete_faculty(id):

    faculty = Faculty.query.get_or_404(id)

    db.session.delete(faculty)

    db.session.commit()

    flash("Faculty Deleted Successfully")

    return redirect(url_for("faculty"))

@app.route("/subjects")
@login_required
def subjects():

    search = request.args.get("search", "")

    if search:
        subjects = Subject.query.filter(
            Subject.subject_name.contains(search)
        ).all()
    else:
        subjects = Subject.query.all()

    return render_template(
        "subjects.html",
        subjects=subjects
    )


@app.route("/add_subject", methods=["GET", "POST"])
@login_required
def add_subject():

    departments = Department.query.all()
    faculties = Faculty.query.all()

    if request.method == "POST":

        subject = Subject(

            subject_code=request.form["subject_code"],

            subject_name=request.form["subject_name"],

            semester=request.form["semester"],

            hours_per_week=request.form["hours_per_week"],

            subject_type=request.form["subject_type"],

            department_id=request.form["department_id"],

            faculty_id=request.form["faculty_id"]

        )

        db.session.add(subject)

        db.session.commit()

        flash("Subject Added Successfully")

        return redirect(url_for("subjects"))

    return render_template(
        "add_subject.html",
        departments=departments,
        faculties=faculties
    )

@app.route("/rooms")
@login_required
def rooms():

    rooms = Room.query.all()

    return render_template(
        "rooms.html",
        rooms=rooms
    )


@app.route("/add_room", methods=["GET","POST"])
@login_required
def add_room():

    if request.method=="POST":

        room = Room(

            room_number=request.form["room_number"],

            room_type=request.form["room_type"],

            capacity=request.form["capacity"]

        )

        db.session.add(room)
        db.session.commit()

        flash("Room Added Successfully")

        return redirect(url_for("rooms"))

    return render_template("add_room.html")

@app.route("/sections")
@login_required
def sections():

    sections = Section.query.all()

    return render_template(
        "sections.html",
        sections=sections
    )


@app.route("/add_section", methods=["GET","POST"])
@login_required
def add_section():

    departments = Department.query.all()

    if request.method=="POST":

        section = Section(

            section_name=request.form["section_name"],

            department_id=request.form["department_id"],

            semester=request.form["semester"],

            strength=request.form["strength"]

        )

        db.session.add(section)

        db.session.commit()

        flash("Section Added Successfully")

        return redirect(url_for("sections"))

    return render_template(
        "add_section.html",
        departments=departments
    )

@app.route("/generate")
@login_required
def generate():

    generate_timetable()

    flash("Timetable Generated Successfully!")

    return redirect(url_for("timetable"))

@app.route("/timetable")
@login_required
def timetable():

    timetable_rows = Timetable.query.all()

    days = ["I", "II", "III", "IV", "V", "VI"]

    periods = [1,2,3,4,5,6]

    timetable = {}

    for row in timetable_rows:

        section = row.section.section_name

        if section not in timetable:

            timetable[section] = {}

            for day in days:

                timetable[section][day] = {}

                for p in periods:

                    timetable[section][day][p] = None

        timetable[section][row.day_order][row.period] = {

            "subject": row.subject.subject_name,

            "faculty": row.faculty.faculty_name,

            "room": row.room.room_number

        }

    return render_template(

        "timetable.html",

        timetable=timetable,

        days=days,

        periods=periods

    )

@app.route("/export_pdf")
@login_required
def pdf():

    return export_pdf()

@app.route("/export_excel")
@login_required
def export_excel():
    return generate_excel()

if __name__ == "__main__":
    app.run(debug=True)