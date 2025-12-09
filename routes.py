from flask import Blueprint, request, jsonify
from app import db
from models import (
    User, Exercise, WorkoutSession, SetLog, 
    PersonalRecord, BodyPart
)
from datetime import datetime, timezone
from sqlalchemy import func

api_bp = Blueprint('api', __name__)


# ========== 1. 取得所有動作 ==========
@api_bp.route('/exercises', methods=['GET'])
def get_exercises():
    """取得所有動作（含部位名稱）"""
    exercises = db.session.query(
        Exercise.id,
        Exercise.name,
        BodyPart.name.label('body_part')
    ).join(BodyPart).all()
    
    return jsonify([{
        'id': ex.id,
        'name': ex.name,
        'body_part': ex.body_part
    } for ex in exercises])


# ========== 2. 開始訓練 ==========
@api_bp.route('/start-session', methods=['POST'])
def start_session():
    """開始一次訓練"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': '缺少 user_id'}), 400
    
    # 檢查使用者是否存在
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '使用者不存在'}), 404
    
    # 建立新訓練
    session = WorkoutSession(
        user_id=user_id,
        start_time=datetime.now(timezone.utc)
    )
    db.session.add(session)
    db.session.commit()
    
    return jsonify({
        'session_id': session.id,
        'message': '訓練已開始！'
    })


# ========== 3. 記錄單組 ==========
@api_bp.route('/add-set', methods=['POST'])
def add_set():
    """記錄一組訓練"""
    data = request.json
    
    # 驗證必填欄位
    required = ['session_id', 'exercise_id', 'set_number']
    if not all(k in data for k in required):
        return jsonify({'error': '缺少必填欄位'}), 400
    
    # 建立記錄
    set_log = SetLog(
        session_id=data['session_id'],
        exercise_id=data['exercise_id'],
        set_number=data['set_number'],
        weight_kg=data.get('weight_kg'),
        reps_actual=data.get('reps_actual'),
        rpe=data.get('rpe', 8.0),
        status='completed'
    )
    db.session.add(set_log)
    db.session.commit()
    
    # 手動更新 PR（因為 SQLAlchemy 不支援觸發器）
    update_personal_records(set_log)
    
    return jsonify({
        'message': '✅ 記錄成功！',
        'set_id': set_log.id
    })


# ========== 4. 查詢個人紀錄 ==========
@api_bp.route('/pr/<int:user_id>', methods=['GET'])
def get_personal_records(user_id):
    """查詢使用者所有 PR"""
    prs = db.session.query(
        Exercise.name.label('exercise'),
        PersonalRecord.pr_type,
        PersonalRecord.value,
        PersonalRecord.updated_date
    ).join(Exercise).filter(
        PersonalRecord.user_id == user_id
    ).order_by(PersonalRecord.updated_date.desc()).all()
    
    return jsonify([{
        'exercise': pr.exercise,
        'type': pr.pr_type,
        'value': float(pr.value),
        'date': pr.updated_date.isoformat()
    } for pr in prs])


# ========== 5. 查詢訓練歷史 ==========
@api_bp.route('/history/<int:user_id>', methods=['GET'])
def get_history(user_id):
    """查詢使用者所有訓練記錄"""
    sessions = db.session.query(
        WorkoutSession.id,
        WorkoutSession.start_time,
        WorkoutSession.end_time,
        func.count(SetLog.id).label('total_sets')
    ).outerjoin(SetLog).filter(
        WorkoutSession.user_id == user_id
    ).group_by(WorkoutSession.id).order_by(
        WorkoutSession.start_time.desc()
    ).limit(20).all()
    
    return jsonify([{
        'session_id': s.id,
        'date': s.start_time.strftime('%Y-%m-%d %H:%M'),
        'total_sets': s.total_sets
    } for s in sessions])


# ========== 輔助函數：更新 PR ==========
def update_personal_records(set_log):
    """根據 SetLog 自動更新 PersonalRecord"""
    if not set_log.weight_kg or not set_log.reps_actual:
        return  # 沒有有效數據就不更新
    
    # 取得 user_id
    session = WorkoutSession.query.get(set_log.session_id)
    user_id = session.user_id
    exercise_id = set_log.exercise_id
    
    # 計算容量（Volume = 重量 × 次數）
    volume = float(set_log.weight_kg) * set_log.reps_actual
    
    # === 1. 更新最大重量 ===
    max_weight_pr = PersonalRecord.query.filter_by(
        user_id=user_id,
        exercise_id=exercise_id,
        pr_type='max_weight'
    ).first()
    
    if not max_weight_pr or float(set_log.weight_kg) > float(max_weight_pr.value):
        if max_weight_pr:
            max_weight_pr.value = set_log.weight_kg
            max_weight_pr.updated_date = datetime.now(timezone.utc)
        else:
            max_weight_pr = PersonalRecord(
                user_id=user_id,
                exercise_id=exercise_id,
                pr_type='max_weight',
                value=set_log.weight_kg
            )
            db.session.add(max_weight_pr)
    
    # === 2. 更新最大次數 ===
    max_reps_pr = PersonalRecord.query.filter_by(
        user_id=user_id,
        exercise_id=exercise_id,
        pr_type='max_reps'
    ).first()
    
    if not max_reps_pr or set_log.reps_actual > int(max_reps_pr.value):
        if max_reps_pr:
            max_reps_pr.value = set_log.reps_actual
            max_reps_pr.updated_date = datetime.now(timezone.utc)
        else:
            max_reps_pr = PersonalRecord(
                user_id=user_id,
                exercise_id=exercise_id,
                pr_type='max_reps',
                value=set_log.reps_actual
            )
            db.session.add(max_reps_pr)
    
    # === 3. 更新最大容量 ===
    max_volume_pr = PersonalRecord.query.filter_by(
        user_id=user_id,
        exercise_id=exercise_id,
        pr_type='max_volume'
    ).first()
    
    if not max_volume_pr or volume > float(max_volume_pr.value):
        if max_volume_pr:
            max_volume_pr.value = volume
            max_volume_pr.updated_date = datetime.now(timezone.utc)
        else:
            max_volume_pr = PersonalRecord(
                user_id=user_id,
                exercise_id=exercise_id,
                pr_type='max_volume',
                value=volume
            )
            db.session.add(max_volume_pr)
    
    db.session.commit()