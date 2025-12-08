# 定義所有「資料表」
from datetime import datetime, timezone
from app import db


# 1. 使用者
class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.String(10))           # M / F / Other
    birth_year = db.Column(db.Integer)
    join_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    measurements = db.relationship('BodyMeasurement', backref='user', lazy=True)
    sessions = db.relationship('WorkoutSession', backref='user', lazy=True)
    exercises = db.relationship('Exercise', backref='creator', lazy=True)
    personal_records = db.relationship('PersonalRecord', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


# 2. 身體測量（改名 BodyMeasurement 比較標準）
class BodyMeasurement(db.Model):
    __tablename__ = 'BodyMeasurements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    measure_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    body_fat_percent = db.Column(db.Float)

    # 計算 BMI 的屬性（不用存進資料庫，只在 Python 計算）
    @property
    def bmi(self):
        if self.height_cm and self.weight_kg and self.height_cm > 0:
            return round(self.weight_kg / ((self.height_cm / 100) ** 2), 1)
        return None


# 3. 部位
class BodyPart(db.Model):
    __tablename__ = 'BodyParts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

    exercises = db.relationship('Exercise', backref='body_part', lazy=True)


# 4. 動作庫
class Exercise(db.Model):
    __tablename__ = 'Exercises'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    body_part_id = db.Column(db.Integer, db.ForeignKey('BodyParts.id'), nullable=False)
    youtube_url = db.Column(db.String(200))
    is_custom = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('Users.id'))  # NULL = 系統預設動作
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # 複合唯一索引：同一個人不能建立兩個同名動作
    __table_args__ = (db.UniqueConstraint('name', 'created_by', name='uix_name_creator'),)


# 5. 訓練模板
class WorkoutTemplate(db.Model):
    __tablename__ = 'WorkoutTemplates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    total_days = db.Column(db.Integer, nullable=False, default=1)


# 6. 模板每天安排
class TemplateDay(db.Model):
    __tablename__ = 'TemplateDays'
    template_id = db.Column(db.Integer, db.ForeignKey('WorkoutTemplates.id'), primary_key=True)
    day_number = db.Column(db.Integer, primary_key=True)
    focus = db.Column(db.String(50))  # 可選：例如 "推" / "拉" / "腿日"


# 7. 模板每天的動作設定
class TemplateExercise(db.Model):
    __tablename__ = 'TemplateExercises'
    template_id = db.Column(db.Integer, db.ForeignKey('WorkoutTemplates.id'), primary_key=True)
    day_number = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('Exercises.id'), primary_key=True)
    set_order = db.Column(db.Integer, nullable=False)   # 第幾順位
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.String(20), nullable=False)     # 用字串支援 "8-12" 這種寫法
    rest_seconds = db.Column(db.Integer, default=120)
    suggested_weight_kg = db.Column(db.Float)

    # 複合外鍵
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['template_id', 'day_number'],
            ['TemplateDays.template_id', 'TemplateDays.day_number']
        ),
    )


# 8. 實際訓練紀錄
class WorkoutSession(db.Model):
    __tablename__ = 'WorkoutSessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('WorkoutTemplates.id'))
    day_number = db.Column(db.Integer)   # 如果沒用模板，就手動填
    start_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    end_time = db.Column(db.DateTime)
    notes = db.Column(db.Text)


# 9. 每組實際記錄（最重要！觸發器會用這張）
class SetLog(db.Model):
    __tablename__ = 'SetLogs'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('WorkoutSessions.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('Exercises.id'), nullable=False)
    set_number = db.Column(db.SmallInteger, nullable=False)
    reps_actual = db.Column(db.SmallInteger)
    weight_kg = db.Column(db.Numeric(6, 2))   # 999.99 kg 夠用
    rpe = db.Column(db.Numeric(3, 1))         # 6.0 ~ 10.0
    status = db.Column(db.String(10), default='completed')  # completed / skipped / failed

    # 檢查 constraint（你問的！）
    __table_args__ = (
        db.CheckConstraint(status.in_(['completed', 'skipped', 'failed']), name='ck_status'),
        db.CheckConstraint(rpe >= 1, name='ck_rpe_min'),
        db.CheckConstraint(rpe <= 10, name='ck_rpe_max'),
    )


# 10. 個人紀錄（Trigger 會自動更新這張）
class PersonalRecord(db.Model):
    __tablename__ = 'PersonalRecords'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('Exercises.id'), nullable=False)
    pr_type = db.Column(db.String(20), nullable=False)  # 'max_weight', 'max_reps', 'max_volume'
    value = db.Column(db.Numeric(10, 2))  # 通用值欄位，如重量、次數或容量
    updated_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint(pr_type.in_(['max_weight', 'max_reps', 'max_volume']), name='ck_pr_type'),
        db.UniqueConstraint('user_id', 'exercise_id', 'pr_type', name='uix_user_exercise_type'),  # 每類型唯一
    )