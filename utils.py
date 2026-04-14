import pandas as pd
import os
from models import db, Student, Attendance

import smtplib
from email.mime.text import MIMEText

def send_parent_email(parent_email, student_name, date, subject_name):
    """
    Live Email functionality mapping. Attempt to connect out via secure SMTP.
    """
    sender = os.environ.get('SMTP_EMAIL', 'principalgiftautonomous@gmail.com')
    password = os.environ.get('SMTP_PASSWORD', 'principal123')
    
    msg = MIMEText(f"Dear Parent,\n\nWe are writing to officially inform you that your ward, {student_name}, was marked ABSENT for the subject '{subject_name}' on {date}.\n\nAccording to new institute regulations, a precise academic fine of ₹50 has been levied against their profile.\n\nPlease ensure they attend classes regularly to prevent further penalties.\n\nRegards,\nGIFT University Attendance Protocol")
    msg['Subject'] = f"Absence Alert - {student_name}"
    msg['From'] = sender
    msg['To'] = parent_email
    
    try:
        # Standard connection array. Default to Gmail configurations.
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print(f"SUCCESS: Email dispatched linearly to {parent_email} via SMTP array.")
    except Exception as e:
        print(f"SMTP UNAVAILABLE: Environment variables not configured locally. [Mock log generated instead] -> TO: {parent_email} FOR: {student_name}")


def process_attendance_fines(student_id):
    student = Student.query.get(student_id)
    if not student:
        return

    # Fetch total classes and attended classes
    total_classes = Attendance.query.filter_by(student_id=student_id).count()
    attended_classes = Attendance.query.filter_by(student_id=student_id, status='Present').count()
    absent_classes = total_classes - attended_classes

    # Ensure attendance_percentage is calculated
    attendance_percentage = (attended_classes / total_classes * 100) if total_classes > 0 else 100

    # Business Rule NEW: Pure synchronizing fine (₹50 every absent block)
    # The system will forcefully recalibrate the exact fine amount based strictly on current total absence metrics.
    student.absent_days = absent_classes
    student.fee_fine = absent_classes * 50

    db.session.commit()

def export_attendance_to_excel():
    """
    Exports the current state of Attendance to an Excel file using pandas.
    """
    records = Attendance.query.all()
    data = []
    for r in records:
        data.append({
            "Attendance ID": r.id,
            "Date": r.date,
            "Time Slot": r.time_slot,
            "Student Name": r.student.user.name,
            "Registration No": r.student.user.username,
            "Course": r.student.course,
            "Semester": r.student.semester,
            "Subject": r.subject.subject_name,
            "Teacher Name": r.teacher.user.name,
            "Status": r.status
        })
    df = pd.DataFrame(data)
    
    export_path = os.path.join(os.path.dirname(__file__), "attendance_export.xlsx")
    df.to_excel(export_path, index=False)
    return export_path

def sync_external_timetable():
    """
    Attempts to connect to https://mytimetable.gift.edu.in/ to scrape Teacher and Class schedules.
    Currently returns an error indicating the host cannot be reached from the server infrastructure.
    """
    import urllib.request
    
    url = "https://mytimetable.gift.edu.in/"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=5).read()
        return True, "Successfully reached timetable link."
    except Exception as e:
        return False, f"Could not sync with {url}. Error: {str(e)}"
