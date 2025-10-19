from flask import Blueprint, jsonify, request, session
from src.models.user import User, db
from src.models.qr_token import QrToken

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['user_role'] = user.role
        
        response_data = {
            'message': 'Login exitoso',
            'user': user.to_dict()
        }
        
        # Si el usuario tiene rol 'public', incluir su marca asociada
        if user.role == 'public' and user.brand_name:
            response_data['brand'] = user.brand_name
            response_data['redirect_to_brand'] = True
        
        return jsonify(response_data), 200
    else:
        return jsonify({'error': 'Credenciales inválidas'}), 401

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout exitoso'}), 200

@auth_bp.route('/auth/profile', methods=['GET'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'No autenticado'}), 401
    
    user = User.query.get(user_id)
    if not user:
        # Si no hay user_id pero hay qr_access, es un qr_guest
        if session.get("qr_access") and session.get("qr_brand"):
            return jsonify({
                "role": "qr_guest",
                "brand_name": session.get("qr_brand"),
                "access_type": "qr",
                "authenticated": True
            }), 200
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/auth/validate-qr-token', methods=['POST'])
def validate_qr_token():
    """Validar token QR y establecer sesión temporal"""
    data = request.json
    token = data.get('token')
    brand_name = data.get('brand')
    
    if not token:
        return jsonify({'error': 'Token requerido'}), 400
    
    # Buscar el token en la base de datos
    qr_token = QrToken.query.filter_by(token=token, token_type='brand').first()
    
    if not qr_token:
        return jsonify({'error': 'Token inválido'}), 401
    
    if not qr_token.is_valid():
        return jsonify({'error': 'Token expirado o ya usado'}), 401
    
    # Verificar que el token corresponde a la marca solicitada
    if qr_token.brand_name != brand_name:
        return jsonify({'error': 'Token no válido para esta marca'}), 401
    
    # Establecer sesión temporal para acceso a la marca
    session['qr_access'] = True
    session['qr_brand'] = brand_name
    session['qr_token_id'] = qr_token.id
    session['user_role'] = 'qr_guest'  # Rol especial para acceso por QR
    
    # Opcional: marcar token como usado si se desea uso único
    # qr_token.mark_as_used()
    
    return jsonify({
        'message': 'Acceso autorizado por QR',
        'brand': brand_name,
        'access_type': 'qr_guest',
        'valid': True
    }), 200

@auth_bp.route('/auth/qr-profile', methods=['GET'])
def qr_profile():
    """Obtener perfil para sesión QR"""
    if not session.get('qr_access'):
        return jsonify({'error': 'No autenticado por QR'}), 401
    
    return jsonify({
        'role': 'qr_guest',
        'brand_name': session.get('qr_brand'),
        'access_type': 'qr',
        'authenticated': True
    }), 200

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'auditor')
    
    if not email or not password:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'El email ya está registrado'}), 400
    
    user = User(email=email, role=role)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Usuario registrado exitosamente',
        'user': user.to_dict()
    }), 201
