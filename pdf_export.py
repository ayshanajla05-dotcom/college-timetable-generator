from io import BytesIO
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from models import Timetable


def export_pdf():

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph("<b>College Timetable</b>", styles["Title"])
    elements.append(title)

    data = [
        [
            "Section",
            "Day Order",
            "Period",
            "Subject",
            "Faculty",
            "Room"
        ]
    ]

    timetable = Timetable.query.order_by(
        Timetable.section_id,
        Timetable.day_order,
        Timetable.period
    ).all()

    for row in timetable:

        data.append([
            row.section.section_name,
            row.day_order,
            row.period,
            row.subject.subject_name,
            row.faculty.faculty_name,
            row.room.room_number
        ])

    table = Table(data)

    table.setStyle(TableStyle([

        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),

        ('GRID', (0,0), (-1,-1), 1, colors.black),

        ('BACKGROUND', (0,1), (-1,-1), colors.beige),

        ('ALIGN', (0,0), (-1,-1), 'CENTER'),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

        ('BOTTOMPADDING', (0,0), (-1,0), 10)

    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="College_Timetable.pdf",
        mimetype="application/pdf"
    )