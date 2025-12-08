# 定義所有「資料表」
from datetime import datetime, timezone
from app import db 


class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.String(10))
    birth_year = db.Column(db.Integer)
    join_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # 與其他資料表關聯??
    measurements = db.relationship('Measurement', backref='user', lazy=True)
    sessions = db.relationship('WorkoutSession', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    
class Measurement(db.Model):
    __tablename__ = 'Measurements'
    measurement_id = db.Column(db.Interger, primary_key=True)
    user_id = db.Column(db.Interger, db.ForeignKey('Users.id'), nullable=False)
    measure_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    body_fat_percent = db.Column(db.Float)

    def __repr__(self):
        return f'<Measurement {self.measurement_id} for User {self.user_id}>'

class BodyPart(db.Model):
    __tablename__ = 'BodyParts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False) # 部位名稱 

    # 關係???
    exercisex = db.relationship('Exersise', backref='body_part', lazy=True) 

    def __repr__(self):
        return f'<BodyPart {self.name}>'

class Exercise(db.Model):
    __tablename__ = 'Exercises'
    exercise_id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(100), nullable=False)
    body_part_id = db.Column(db.Integer, db.ForeignKey('BodyParts.id'), nullable=False)
    youtube_url = db.Column(db.String(200))
    created_by = db.Column(db.Integer, db.ForeignKey('Users.id'))

    def __repr__(self):
        return f'<Exercise {self.exercise_name}>'

class WorkoutTemplate(db.Model):
    __tablename__ = 'WorkoutTemplates'
    template_id = db.Column(db.Integer, primary_key=True)
    template_name = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Interger, db.ForeignKey('Users.id'))
    total_days = db.Column(db.Interger, nullable=False)

    def __repr__(self):
        return f'<WorkoutTemplate {self.template_name}>'

class TemplateDay(db.Model):
    __tablename__ = 'TemplateDays'
    template_id = db.Column(db.Integer, db.ForeignKey('WorkoutTemplates.template_id'), primary_key=True)
    day_number = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f'<TemplateDay {self.template_id} ; Day {self.day_number}>'

class TemplateExercise(db.Model):
    __tablename__ = 'TemplateExercises'
    template_id = db.Column(db.Integer, db.ForeignKey('WorkoutTemplates.template_id'), primary_key=True)
    day_number = db.Column(db.Integer,db.ForeignKey('TemplateDays.day_number'), primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('Exercises.exercise_id'), primary_key=True)
    set_order = db.Column(db.Integer, nullamle=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    rest_seconds = db.Column(db.Integer)
    weight_kg = db.Column(db.Float)

    def __repr__(self):
        return f'<TemplateExercise {self.template_id} ; Day {self.day_number} ; Exercise {self.exercise_id}>'
    
class WorkoutSession(db.Model):
    __tablename__ = 'WorkoutSessions'
    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('WorkoutTemplates.template_id'))
    template_day_number = db.Column(db.Integer, db.ForeignKey('TemplateDays.day_number'))
    start_time = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<WorkoutSession {self.session_id} for User {self.user_id}>'

