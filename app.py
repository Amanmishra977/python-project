from flask import Flask, redirect, url_for
from models import db, User
import os

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.teacher import teacher_bp
from routes.student import student_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-attendance-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(student_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

def setup_database():
    with app.app_context():
        db.create_all()
        # Seed an admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin', name='Super Admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: admin / admin123")

setup_database()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
