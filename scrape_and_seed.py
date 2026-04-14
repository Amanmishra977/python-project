import re
import requests
from bs4 import BeautifulSoup
from app import app
from models import db, Teacher, Subject, Timetable, User

def scrape_and_seed():
    headers = {'User-Agent': 'Mozilla/5.0'}
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    with app.app_context():
        # Clean up old dummy subjects and timetables
        dummy_subjects = Subject.query.filter(Subject.subject_name.like("General Subject%")).all()
        for ds in dummy_subjects:
            # Delete associated timetables
            Timetable.query.filter_by(subject_id=ds.id).delete()
            db.session.delete(ds)
        db.session.commit()
        print("Deleted old dummy dummy timetables and subjects.")

        teachers = Teacher.query.join(User).all()
        print(f"Found {len(teachers)} teachers in the database. Fetching their timetables...")
        
        added_subjects = {}
        timetable_count = 0

        for teacher in teachers:
            username = teacher.user.username
            if username.startswith("T") and username[1:].isdigit():
                link_id = username[1:]
                url = f"https://mytimetable.gift.edu.in/mytimetable.php?t=r&id={link_id}"
                
                try:
                    resp = requests.get(url, headers=headers, timeout=10)
                    if resp.status_code != 200:
                        continue
                        
                    soup = BeautifulSoup(resp.content, 'html.parser')
                    table = soup.find('table', {'id': 'tbl'})
                    if not table:
                        continue

                    tbody = table.find('tbody')
                    if not tbody:
                        continue
                        
                    rows = tbody.find_all('tr')
                    for row in rows:
                        th = row.find('th')
                        if not th:
                            continue
                        time_slot = th.get_text(strip=True)
                        
                        tds = row.find_all('td')
                        for day_idx, td in enumerate(tds):
                            if day_idx >= len(days_of_week):
                                break
                            
                            day = days_of_week[day_idx]
                            
                            # Replace <br> with | for easy splitting
                            for br in td.find_all('br'):
                                br.replace_with('|')
                                
                            text = td.get_text(strip=True)
                            if not text:
                                continue
                                
                            parts = [p.strip() for p in text.split('|') if p.strip()]
                            if len(parts) >= 2:
                                subject_part = parts[0]
                                course_sem_part = parts[1]
                                
                                # Parse semester and course e.g. "4TH Sem AGRIL"
                                sem_match = re.search(r'(\d+)\s*(?:TH|ST|ND|RD)?\s*Sem\s+(.*)', course_sem_part, re.IGNORECASE)
                                if sem_match:
                                    sem = int(sem_match.group(1))
                                    course = sem_match.group(2).strip()
                                else:
                                    sem = 1
                                    course = course_sem_part
                                    
                                subject_name = subject_part
                                
                                # Check if subject exists
                                subj_key = f"{subject_name}_{course}_{sem}"
                                subject = added_subjects.get(subj_key)
                                
                                if not subject:
                                    subject = Subject.query.filter_by(subject_name=subject_name, course=course, semester=sem).first()
                                    if not subject:
                                        subject = Subject(subject_name=subject_name, course=course, semester=sem)
                                        db.session.add(subject)
                                        db.session.flush() # get ID
                                    added_subjects[subj_key] = subject
                                
                                # Add timetable entry
                                # Check if already exists to prevent duplicates if script runs multiple times
                                existing_tt = Timetable.query.filter_by(
                                    teacher_id=teacher.id, 
                                    day_of_week=day, 
                                    time_slot=time_slot
                                ).first()
                                
                                if not existing_tt:
                                    tt = Timetable(
                                        teacher_id=teacher.id,
                                        subject_id=subject.id,
                                        course=course,
                                        semester=sem,
                                        day_of_week=day,
                                        time_slot=time_slot
                                    )
                                    db.session.add(tt)
                                    timetable_count += 1
                                    
                except Exception as e:
                    print(f"Failed to process {url}: {e}")
                    
        db.session.commit()
        print(f"Successfully scraped and assigned {len(added_subjects)} distinct subjects and {timetable_count} timetable entries.")

if __name__ == "__main__":
    scrape_and_seed()
