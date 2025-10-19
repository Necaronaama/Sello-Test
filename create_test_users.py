import os
import sys
from flask import Flask

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db, User

app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'
] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Crear usuario auditor
    auditor_user = User.query.filter_by(email='auditor@selloqr.net').first()
    if not auditor_user:
        auditor_user = User(email='auditor@selloqr.net', role='auditor')
        auditor_user.set_password('auditor123')
        db.session.add(auditor_user)
        print("Usuario auditor creado: auditor@selloqr.net / auditor123")

    # Crear usuario público (en este contexto, un usuario sin rol específico que solo ve lo público)
    public_user = User.query.filter_by(email='publico@selloqr.net').first()
    if not public_user:
        public_user = User(email='publico@selloqr.net', role='public') # Asignar un rol 'public' o 'user'
        public_user.set_password('publico123')
        db.session.add(public_user)
        print("Usuario público creado: publico@selloqr.net / publico123")

    db.session.commit()
    print("Usuarios de prueba creados/verificados.")


