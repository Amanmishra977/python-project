import sqlite3

def rearrange_table(conn, table_name, foreign_keys):
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {table_name} ORDER BY id")
    old_ids = [row[0] for row in cursor.fetchall()]

    # Shift IDs to a safe high namespace to avoid UNIQUE constraints during the update
    offset = 1000000
    for old_id in old_ids:
        safe_id = old_id + offset
        cursor.execute(f"UPDATE {table_name} SET id = ? WHERE id = ?", (safe_id, old_id))
        for child_table, fk_col in foreign_keys:
            cursor.execute(f"UPDATE {child_table} SET {fk_col} = ? WHERE {fk_col} = ?", (safe_id, old_id))

    # Shift back to contiguous values starting from 1
    new_id = 1
    for old_id in old_ids:
        safe_id = old_id + offset
        cursor.execute(f"UPDATE {table_name} SET id = ? WHERE id = ?", (new_id, safe_id))
        for child_table, fk_col in foreign_keys:
            cursor.execute(f"UPDATE {child_table} SET {fk_col} = ? WHERE {fk_col} = ?", (new_id, safe_id))
        new_id += 1

def run():
    conn = sqlite3.connect('instance/attendance.db')
    try:
        # We process each table and specify the children that reference its ID.
        
        # 1. users -> students.user_id, teachers.user_id
        rearrange_table(conn, 'users', [('students', 'user_id'), ('teachers', 'user_id')])
        
        # 2. teachers -> attendance.teacher_id, timetable.teacher_id
        rearrange_table(conn, 'teachers', [('attendance', 'teacher_id'), ('timetable', 'teacher_id')])
        
        # 3. students -> attendance.student_id
        rearrange_table(conn, 'students', [('attendance', 'student_id')])
        
        # 4. subjects -> attendance.subject_id, timetable.subject_id
        rearrange_table(conn, 'subjects', [('attendance', 'subject_id'), ('timetable', 'subject_id')])
        
        # 5. timetable -> none
        rearrange_table(conn, 'timetable', [])
        
        # 6. attendance -> none
        rearrange_table(conn, 'attendance', [])
        
        conn.commit()
        print("Successfully reorganized all database serials.")
    except Exception as e:
        conn.rollback()
        print(f"Error during reorganization: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    run()
