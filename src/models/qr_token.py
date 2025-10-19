from datetime import datetime, timedelta
from src.models.user import db
import secrets

class QrToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Nullable para tokens de marca
    brand_name = db.Column(db.String(100), nullable=True)  # Nuevo campo para marca
    token_type = db.Column(db.String(50), default='user')  # 'user' o 'brand'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=True)  # Expiración personalizable

    user = db.relationship('User', backref='qr_tokens')

    def is_valid(self):
        """Verificar si el token es válido"""
        if self.used:
            return False
        
        # Si tiene fecha de expiración específica, usarla
        if self.expires_at:
            return datetime.utcnow() < self.expires_at
        
        # Si no tiene fecha de expiración específica, se considera válido indefinidamente (o hasta que se marque como usado)
        return True

    def mark_as_used(self):
        """Marcar token como usado"""
        self.used = True
        db.session.commit()

    @classmethod
    def create_brand_token(cls, brand_name, expires_hours=24):
        """Crear un token para acceso a marca específica"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
        qr_token = cls(
            token=token,
            brand_name=brand_name,
            token_type='brand',
            expires_at=expires_at
        )
        
        db.session.add(qr_token)
        db.session.commit()
        
        return qr_token

    @classmethod
    def create_user_token(cls, user_id, expires_minutes=5):
        """Crear un token para usuario específico"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
        
        qr_token = cls(
            token=token,
            user_id=user_id,
            token_type='user',
            expires_at=expires_at
        )
        
        db.session.add(qr_token)
        db.session.commit()
        
        return qr_token

    def __repr__(self):
        return f'<QrToken {self.token} ({self.token_type})>'
