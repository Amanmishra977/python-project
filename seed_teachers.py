import re
from app import app
from models import db, User, Teacher, Subject, Timetable

def seed_database():
    content_file_path = "/Users/amanmishra/.gemini/antigravity/brain/96c9c05d-dfdb-407a-ad6a-bff64e5b5024/.system_generated/steps/5/content.md"
    
    with open(content_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to find all markdown links
    # e.g., [Dr. Ananya Mishra](https://mytimetable.gift.edu.in/mytimetable.php?t=r&id=17632)
    # or just normal URL matches
    pattern = r"\[(.*?)\]\s*\((.*?id=(\d+))\)"
    
    matches = re.findall(pattern, content)
    print(f"Found {len(matches)} teachers.")

    with app.app_context():
        added_count = 0
        for match in matches:
            name = match[0].strip()
            url_id = match[2].strip()
            teacher_username = f"T{url_id}"

            # Check if user already exists
            existing_user = User.query.filter_by(username=teacher_username).first()
            if existing_user:
                continue

            # Create User
            user = User(username=teacher_username, role='teacher', name=name)
            user.set_password('password123')
            db.session.add(user)
            db.session.flush() # to get user.id

            # Create Teacher
            teacher = Teacher(user_id=user.id, department="Engineering")
            db.session.add(teacher)
            db.session.flush() # to get teacher.id

            # Create an assignable dummy subject for this teacher to take attendance
            subject_name = f"General Subject ({name})"
            subject = Subject(course="BTech", semester=1, subject_name=subject_name)
            db.session.add(subject)
            db.session.flush() # to get subject.id
            
            # Assign Timetable so it shows up on their dashboard
            timetable = Timetable(
                teacher_id=teacher.id,
                subject_id=subject.id,
                course="BTech",
                semester=1,
                day_of_week="Monday",
                time_slot="10:00-11:00"
            )
            db.session.add(timetable)
            added_count += 1
            
        db.session.commit()
        print(f"Successfully added {added_count} new teachers and created their timetables.")

if __name__ == "__main__":
    seed_database()
