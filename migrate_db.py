import sqlite3

def run_migration():
    db_path = "instance/attendance.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Add new columns (ignore if already exists)
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN department VARCHAR(100)")
        except sqlite3.OperationalError:
            pass # Column exists
            
        try:
            cursor.execute("ALTER TABLE subjects ADD COLUMN department VARCHAR(100)")
        except sqlite3.OperationalError:
            pass
            
        try:
            cursor.execute("ALTER TABLE timetable ADD COLUMN department VARCHAR(100)")
        except sqlite3.OperationalError:
            pass

        # Update subjects
        # Step 1: For Master programs, department = course
        masters = "('MCA', 'MBA', 'BBA', 'BCA')"
        cursor.execute(f"UPDATE subjects SET department = course WHERE course IN {masters}")
        
        # Step 2: For others (which are currently department names scraped, like 'AGRIL'), department = course, course = 'BTech'
        cursor.execute(f"UPDATE subjects SET department = course, course = 'BTech' WHERE course NOT IN {masters} AND department IS NULL")
        
        # Now do the same for timetable
        cursor.execute(f"UPDATE timetable SET department = course WHERE course IN {masters}")
        cursor.execute(f"UPDATE timetable SET department = course, course = 'BTech' WHERE course NOT IN {masters} AND department IS NULL")
        
        # For students, currently there are no students with missing departments yet if we haven't seeded them, so leaving as NULL is fine for now

        conn.commit()
        print("Database migration completed successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Error migrating: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
