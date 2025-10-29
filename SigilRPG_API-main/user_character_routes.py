"""
Rotas para personagem do usuário
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Character
import re

user_character_bp = Blueprint('user_character', __name__)

@user_character_bp.route('/', methods=['POST'])
@jwt_required()
def create_user_character():
    """Cria um personagem para o usuário autenticado"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'user_not_found'}), 404
        
        # Verificar se o usuário já tem um personagem
        existing_character = Character.query.filter_by(user_id=user_id).first()
        if existing_character:
            return jsonify({
                'message': 'user_already_has_character',
                'error_detail': 'Usuário já possui um personagem'
            }), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'invalid_data'}), 400
        
        # Validação dos dados
        name = data.get('name')
        age = data.get('age')
        skilled_in = data.get('skilled_in')
        
        errors = {}
        
        if not name or len(name.strip()) == 0:
            errors['name'] = ['Nome é obrigatório']
        elif len(name) > 255:
            errors['name'] = ['Nome deve ter no máximo 255 caracteres']
        
        if not age:
            errors['age'] = ['Idade é obrigatória']
        elif not isinstance(age, int) or age < 1 or age > 200:
            errors['age'] = ['Idade deve ser um número entre 1 e 200']
        
        if not skilled_in or len(skilled_in.strip()) == 0:
            errors['skilled_in'] = ['Habilidade é obrigatória']
        elif len(skilled_in) > 255:
            errors['skilled_in'] = ['Habilidade deve ter no máximo 255 caracteres']
        
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Criar personagem
        character = Character(
            name=name.strip(),
            age=age,
            skilled_in=skilled_in.strip(),
            user_id=user_id
        )
        
        db.session.add(character)
        db.session.commit()
        
        return jsonify({
            'message': 'character_created',
            'data': character.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'error_creating_character'}), 500

@user_character_bp.route('/', methods=['GET'])
@jwt_required()
def show_user_character():
    """Mostra o personagem do usuário autenticado"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'user_not_found'}), 404
        
        character = Character.query.filter_by(user_id=user_id).first()
        
        if not character:
            return jsonify({
                'message': 'character_not_exist',
                'error_detail': 'Nenhum personagem existe para este usuário, primeiro crie um personagem'
            }), 400
        
        return jsonify({
            'message': 'character',
            'data': character.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'error_retrieving_character'}), 500
