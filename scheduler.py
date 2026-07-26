import random
from models import db, Subject, Faculty, Room, Section, Timetable
from conflict_report import clear_conflicts, add_conflict

DAY_ORDERS = [
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI"
]

PERIODS = [1, 2, 3, 4, 5, 6]

def generate_timetable():
    clear_conflicts()
    Timetable.query.delete()
    db.session.commit()

    sections = Section.query.all()

    for section in sections:

        subjects = Subject.query.filter_by(
            department_id=section.department_id,
            semester=section.semester
        ).all()

        random.shuffle(subjects)

        for subject in subjects:

            remaining_hours = subject.hours_per_week

            # ---------- LAB ----------
            if subject.subject_type.lower() == "lab":

                while remaining_hours >= 3:

                    assigned = False

                    random_days = DAY_ORDERS[:]
                    random.shuffle(random_days)

                    for day in random_days:

                        # consecutive periods
                        for start in [1, 2, 3, 4]:

                            if assign_lab(
                                section,
                                subject,
                                day,
                                start
                            ):

                                remaining_hours -= 3
                                assigned = True
                                break

                        if assigned:
                            break

                    if not assigned:

                        add_conflict(
                            "Scheduling Failed",
                            section.section_name,
                            subject.subject_name,
                            "No available day order and period found."
                        )

                        break
            # ---------- THEORY ----------
            else:

                while remaining_hours > 0:

                    assigned = False

                    random_days = DAY_ORDERS[:]
                    random.shuffle(random_days)

                    for day in random_days:

                        random_periods = PERIODS[:]
                        random.shuffle(random_periods)

                        for period in random_periods:

                            if assign_theory(
                                section,
                                subject,
                                day,
                                period
                            ):

                                remaining_hours -= 1
                                assigned = True
                                break

                        if assigned:
                            break

                    if not assigned:

                        add_conflict(
                            "Scheduling Failed",
                            section.section_name,
                            subject.subject_name,
                            "No available day order and period found."
                        )

                        break

    db.session.commit()

def faculty_busy(faculty_id, day, period):

    return Timetable.query.filter_by(
        faculty_id=faculty_id,
        day_order=day,
        period=period
    ).first() is not None

def room_busy(room_id, day, period):

    return Timetable.query.filter_by(
        room_id=room_id,
        day_order=day,
        period=period
    ).first() is not None

def section_busy(section_id, day, period):

    return Timetable.query.filter_by(
        section_id=section_id,
        day_order=day,
        period=period
    ).first() is not None

def assign_theory(section, subject, day, period):

    room = Room.query.filter_by(
        room_type="Classroom"
    ).first()

    if room is None:
        return False

    if faculty_busy(subject.faculty_id, day, period):

        add_conflict(
            "Faculty Conflict",
            section.section_name,
            subject.subject_name,
            f"Faculty is already assigned on Day Order {day}, Period {period}."
        )

        return False

    if room_busy(room.id, day, period):

        add_conflict(
            "Room Conflict",
            section.section_name,
            subject.subject_name,
            f"{room.room_number} is already occupied on Day Order {day}, Period {period}."
        )

        return False

    if section_busy(section.id, day, period):

        add_conflict(
            "Section Conflict",
            section.section_name,
            subject.subject_name,
            f"Section already has a class on Day {day}, Period {period}."
        )

        return False

    db.session.add(
        Timetable(
            day_order=day,
            period=period,
            section_id=section.id,
            subject_id=subject.id,
            faculty_id=subject.faculty_id,
            room_id=room.id
        )
    )

    return True

def assign_lab(section, subject, day, start):

    room = Room.query.filter_by(
        room_type="Lab"
    ).first()

    if room is None:
        return False

    for p in range(start, start + 3):

        if faculty_busy(subject.faculty_id, day, p):

            add_conflict(
                "Faculty Conflict",
                section.section_name,
                subject.subject_name,
                f"Faculty is busy on Day {day}, Period {p}."
            )

            return False

        if room_busy(room.id, day, p):

            add_conflict(
                "Room Conflict",
                section.section_name,
                subject.subject_name,
                f"Lab {room.room_number} is occupied on Day {day}, Period {p}."
            )

            return False

        if section_busy(section.id, day, p):

            add_conflict(
                "Section Conflict",
                section.section_name,
                subject.subject_name,
                f"Section already has a class on Day {day}, Period {p}."
            )

            return False

    for p in range(start, start + 3):

        db.session.add(
            Timetable(
                day_order=day,
                period=p,
                section_id=section.id,
                subject_id=subject.id,
                faculty_id=subject.faculty_id,
                room_id=room.id
            )
        )

    return True

