"""
Rotas de autenticação
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import check_password_hash
from models import db, User
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Autentica um usuário e retorna um token JWT"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'invalid_credentials'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        # Validação básica
        if not email or not password:
            return jsonify({'message': 'invalid_credentials'}), 400
        
        # Validação de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'message': 'invalid_credentials'}), 400
        
        # Buscar usuário
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'message': 'invalid_credentials'}), 401
        
        # Criar token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'token_generated',
            'data': {
                'token': access_token
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'could_not_create_token'}), 500

@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    """Retorna informações do usuário autenticado"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'message': 'user_not_found'}), 404
        
        return jsonify({
            'message': 'authenticated_user',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'error_retrieving_user'}), 500

@auth_bp.route('/', methods=['PATCH'])
@jwt_required()
def refresh_token():
    """Atualiza o token JWT"""
    try:
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=str(current_user_id))
        
        return jsonify({
            'message': 'token_refreshed',
            'data': {
                'token': new_token
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'error_refreshing_token'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registra um novo usuário"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'invalid_data', 'error': 'No JSON data provided'}), 400
        
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        # Validação básica
        if not name or not email or not password:
            return jsonify({'message': 'missing_fields', 'error': 'Name, email and password are required'}), 400
        
        # Validação de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'message': 'invalid_email', 'error': 'Invalid email format'}), 400
        
        # Verificar se o email já existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': 'email_already_exists', 'error': 'Email already registered'}), 409
        
        # Criar novo usuário
        user = User(
            name=name,
            email=email
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Criar token para o novo usuário
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'user_created',
            'data': {
                'user': user.to_dict(),
                'token': access_token
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao registrar usuário: {str(e)}")
        return jsonify({'message': 'error_creating_user', 'error': str(e)}), 500

@auth_bp.route('/', methods=['DELETE'])
@jwt_required()
def invalidate_token():
    """Invalida o token JWT atual"""
    try:
        # Em uma implementação mais robusta, você adicionaria o token a uma blacklist
        # Por simplicidade, apenas retornamos sucesso
        return jsonify({'message': 'token_invalidated'}), 200
        
    except Exception as e:
        return jsonify({'message': 'error_invalidating_token'}), 500
