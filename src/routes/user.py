from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import User, db
from src.utils.email import EmailService
import secrets
from datetime import datetime, timedelta
import re

user_bp = Blueprint('user', __name__)
email_service = EmailService()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 8

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} es requerido'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        full_name = data['full_name'].strip()
        phone = data.get('phone', '').strip()
        
        # Validaciones
        if len(username) < 3:
            return jsonify({'error': 'El nombre de usuario debe tener al menos 3 caracteres'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Email inválido'}), 400
        
        if not validate_password(password):
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'El nombre de usuario ya está en uso'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'El email ya está registrado'}), 400
        
        # Generar token de verificación
        verification_token = secrets.token_urlsafe(32)
        
        # Crear nuevo usuario
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            phone=phone,
            verification_token=verification_token,
            is_verified=False,
            is_premium=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Enviar email de verificación
        email_sent = email_service.send_verification_email(
            user_email=email,
            user_name=full_name,
            verification_token=verification_token
        )
        
        if email_sent:
            return jsonify({
                'message': 'Usuario registrado exitosamente. Revisa tu email para verificar tu cuenta.',
                'user_id': user.id
            }), 201
        else:
            return jsonify({
                'message': 'Usuario registrado exitosamente, pero hubo un problema enviando el email de verificación.',
                'user_id': user.id
            }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@user_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    try:
        token = request.args.get('token') if request.method == 'GET' else request.get_json().get('token')
        
        if not token:
            return jsonify({'error': 'Token de verificación requerido'}), 400
        
        # Buscar usuario por token
        user = User.query.filter_by(verification_token=token).first()
        
        if not user:
            return jsonify({'error': 'Token de verificación inválido'}), 400
        
        if user.is_verified:
            return jsonify({'message': 'La cuenta ya está verificada'}), 200
        
        # Verificar si el token ha expirado (24 horas)
        if user.created_at < datetime.utcnow() - timedelta(hours=24):
            return jsonify({'error': 'El token de verificación ha expirado'}), 400
        
        # Verificar la cuenta
        user.is_verified = True
        user.verification_token = None  # Limpiar el token
        db.session.commit()
        
        return jsonify({'message': 'Cuenta verificada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400
        
        # Buscar usuario por username o email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        if not user.is_verified:
            return jsonify({'error': 'Debes verificar tu email antes de iniciar sesión'}), 401
        
        # Crear sesión
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_premium'] = user.is_premium
        
        return jsonify({
            'message': 'Inicio de sesión exitoso',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'is_premium': user.is_premium,
                'is_verified': user.is_verified
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@user_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Sesión cerrada exitosamente'}), 200

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'is_premium': user.is_premium,
            'is_verified': user.is_verified,
            'created_at': user.created_at.isoformat(),
            'premium_expires_at': user.premium_expires_at.isoformat() if user.premium_expires_at else None
        }
    }), 200

@user_bp.route('/upgrade-premium', methods=['POST'])
def upgrade_premium():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        
        data = request.get_json()
        payment_reference = data.get('payment_reference', '').strip()
        
        if not payment_reference:
            return jsonify({'error': 'Referencia de pago requerida'}), 400
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        if user.is_premium:
            return jsonify({'error': 'El usuario ya es premium'}), 400
        
        # En un entorno real, aquí verificarías el pago con Bizum
        # Por ahora, simulamos que el pago es válido
        
        # Actualizar usuario a premium (válido por 1 año)
        user.is_premium = True
        user.premium_expires_at = datetime.utcnow() + timedelta(days=365)
        db.session.commit()
        
        # Actualizar sesión
        session['is_premium'] = True
        
        # Enviar email de confirmación
        email_service.send_premium_confirmation_email(
            user_email=user.email,
            user_name=user.full_name
        )
        
        return jsonify({
            'message': 'Upgrade a premium exitoso',
            'premium_expires_at': user.premium_expires_at.isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@user_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        if user.is_verified:
            return jsonify({'error': 'La cuenta ya está verificada'}), 400
        
        # Generar nuevo token
        user.verification_token = secrets.token_urlsafe(32)
        db.session.commit()
        
        # Enviar nuevo email
        email_sent = email_service.send_verification_email(
            user_email=user.email,
            user_name=user.full_name,
            verification_token=user.verification_token
        )
        
        if email_sent:
            return jsonify({'message': 'Email de verificación reenviado'}), 200
        else:
            return jsonify({'error': 'Error enviando email'}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@user_bp.route('/', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'is_verified': user.is_verified,
        'is_premium': user.is_premium,
        'created_at': user.created_at.isoformat()
    } for user in users]), 200

