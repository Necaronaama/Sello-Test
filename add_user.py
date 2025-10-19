import os
import sys
from flask import Flask

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db, User

app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'
] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def add_user(email, password, role='auditor'):
    """
    Agregar un nuevo usuario al sistema
    
    Args:
        email (str): Correo electrónico del usuario
        password (str): Contraseña del usuario
        role (str): Rol del usuario ('admin', 'auditor', 'public')
    """
    with app.app_context():
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"Error: El usuario {email} ya existe en el sistema.")
            return False
        
        # Crear nuevo usuario
        new_user = User(email=email, role=role)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            print(f"Usuario creado exitosamente:")
            print(f"  Email: {email}")
            print(f"  Rol: {role}")
            print(f"  Contraseña: {password}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear usuario: {str(e)}")
            return False

def list_users():
    """Listar todos los usuarios del sistema"""
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No hay usuarios en el sistema.")
            return
        
        print("Usuarios en el sistema:")
        print("-" * 50)
        for user in users:
            print(f"Email: {user.email}")
            print(f"Rol: {user.role}")
            print(f"Creado: {user.created_at}")
            print("-" * 50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  Agregar usuario: python add_user.py add <email> <password> <role>")
        print("  Listar usuarios: python add_user.py list")
        print("")
        print("Roles disponibles: admin, auditor, public")
        print("")
        print("Ejemplos:")
        print("  python add_user.py add nuevo@usuario.com mipassword123 auditor")
        print("  python add_user.py list")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_users()
    elif command == "add":
        if len(sys.argv) < 4:
            print("Error: Faltan argumentos para agregar usuario")
            print("Uso: python add_user.py add <email> <password> <role>")
            sys.exit(1)
        
        email = sys.argv[2]
        password = sys.argv[3]
        role = sys.argv[4] if len(sys.argv) > 4 else 'auditor'
        
        # Validar rol
        if role not in ['admin', 'auditor', 'public']:
            print("Error: Rol inválido. Use: admin, auditor, o public")
            sys.exit(1)
        
        add_user(email, password, role)
    else:
        print(f"Comando desconocido: {command}")
        print("Comandos disponibles: add, list")
        sys.exit(1)

