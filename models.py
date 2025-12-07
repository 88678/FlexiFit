# 定義所有「資料表」
from datetime import datetime, timezone

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

    


class BodyPart(db.Model):
    __tablename__ = 'BodyParts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False) # 部位名稱 

    # 關係???
    exercisex = db.relationship('Exersise', backref='body_part', lazy=True) 

    def __repr__(self):
        return f'<BodyPart {self.name}>'

from app import db # 這行一定要放在最下面！等 app.py 建立好 db 再 import
