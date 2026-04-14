from app import app
from models import db, Subject, Student, User

def seed_test_students():
    with app.app_context():
        # Get all distinct (course, department, semester) combinations from subjects
        combinations = db.session.query(Subject.course, Subject.department, Subject.semester).distinct().all()
        
        reg_no = 2601432100
        default_pwd = "student123"
        
        students_added = 0
        
        for combo in combinations:
            course, department, semester = combo
            
            # For each combination, we want to add 10 students
            for i in range(10):
                username = str(reg_no)
                
                # Check if username already exists
                existing = User.query.filter_by(username=username).first()
                if not existing:
                    # Create User
                    user = User(
                        username=username,
                        role='student',
                        name=f"Test Student {username}"
                    )
                    user.set_password(default_pwd)
                    db.session.add(user)
                    db.session.flush() # get user ID
                    
                    # Create Student profile
                    student = Student(
                        user_id=user.id,
                        course=course,
                        department=department,
                        semester=semester,
                        parent_email=f"parent_{username}@example.com"
                    )
                    db.session.add(student)
                    students_added += 1
                
                reg_no += 1
                
        db.session.commit()
        print(f"Successfully generated {students_added} test students across {len(combinations)} active course/dept/sem combinations.")

if __name__ == "__main__":
    seed_test_students()
