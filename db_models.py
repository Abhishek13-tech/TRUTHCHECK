from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    auth_method = db.Column(db.String(20), nullable=False, default="email")  # 'email', 'google', 'phone'
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(25), unique=True, nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User's analysis records
    checks = db.relationship("CheckHistory", backref="user", lazy=True, cascade="all, delete-orphan")

    def get_display_name(self):
        if self.full_name:
            return self.full_name
        if self.email:
            return self.email.split("@")[0].capitalize()
        if self.phone:
            return f"User ({self.phone[-4:]})"
        return "TruthCheck User"

    def get_identifier(self):
        if self.email:
            return self.email
        if self.phone:
            return self.phone
        return "Anonymous User"

class CheckHistory(db.Model):
    __tablename__ = "check_history"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    check_type = db.Column(db.String(20), nullable=False)  # 'image' or 'text'
    input_preview = db.Column(db.String(255), nullable=True)
    source_type = db.Column(db.String(50), nullable=True)  # 'direct_text', 'image_ocr', 'image_check'
    verdict = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Integer, default=50)
    image_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
