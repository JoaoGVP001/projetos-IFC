"""
Rotas para personagem do usuário
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Character
import re

user_character_bp = Blueprint('user_character', __name__)

def _safe_int(value, default=None):
    """Converte um valor para int de forma segura, retornando default se falhar"""
    if value is None:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

@user_character_bp.route('/', methods=['POST'])
@jwt_required()
def create_user_character():
    """Cria um personagem para o usuário autenticado"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'user_not_found'}), 404
        
        # Permitir múltiplos personagens - remover restrição
        
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
        
        # Criar personagem com todos os campos opcionais
        character = Character(
            name=name.strip(),
            age=age,
            skilled_in=skilled_in.strip(),
            user_id=user_id,
            player_name=data.get('player_name'),
            origin=data.get('origin'),
            character_class=data.get('character_class'),
            nex=_safe_int(data.get('nex'), 5),  # Valor padrão de 5 se não fornecido
            avatar_url=data.get('avatar_url'),
            agilidade=_safe_int(data.get('agilidade'), 1),
            intelecto=_safe_int(data.get('intelecto'), 1),
            vigor=_safe_int(data.get('vigor'), 1),
            presenca=_safe_int(data.get('presenca'), 1),
            forca=_safe_int(data.get('forca'), 1),
            gender=data.get('gender'),
            appearance=data.get('appearance'),
            personality=data.get('personality'),
            background=data.get('background'),
            objective=data.get('objective')
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
def list_user_characters():
    """Lista todos os personagens do usuário autenticado"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'user_not_found'}), 404
        
        characters = Character.query.filter_by(user_id=user_id).all()
        
        # Sempre retornar lista, mesmo se vazia (para compatibilidade)
        return jsonify({
            'message': 'characters',
            'data': [char.to_dict() for char in characters]
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'error_retrieving_characters',
            'error': str(e)
        }), 500

@user_character_bp.route('/<int:character_id>', methods=['GET'])
@jwt_required()
def show_user_character(character_id):
    """Mostra um personagem específico do usuário autenticado"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'user_not_found'}), 404
        
        character = Character.query.filter_by(
            id=character_id,
            user_id=user_id
        ).first()
        
        if not character:
            return jsonify({
                'message': 'character_not_found',
                'error_detail': 'Personagem não encontrado ou não pertence a este usuário'
            }), 404
        
        return jsonify({
            'message': 'character',
            'data': character.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'error_retrieving_character'}), 500

@user_character_bp.route('/<int:character_id>', methods=['PATCH'])
@jwt_required()
def update_user_character(character_id):
    """Atualiza um personagem do usuário autenticado"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'user_not_found'}), 404
        
        character = Character.query.filter_by(
            id=character_id,
            user_id=user_id
        ).first()
        
        if not character:
            return jsonify({
                'message': 'character_not_found',
                'error_detail': 'Personagem não encontrado ou não pertence a este usuário'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'invalid_data'}), 400
        
        # Atualizar campos permitidos
        if 'name' in data:
            character.name = data['name'].strip()
        if 'player_name' in data:
            character.player_name = data['player_name']
        if 'age' in data:
            age = data['age']
            if isinstance(age, int) and 1 <= age <= 200:
                character.age = age
        if 'skilled_in' in data:
            character.skilled_in = data['skilled_in'].strip()
        if 'origin' in data:
            character.origin = data['origin']
        if 'character_class' in data:
            character.character_class = data['character_class']
        if 'nex' in data:
            nex = _safe_int(data['nex'])
            if nex is not None and 5 <= nex <= 100:
                character.nex = nex
        if 'avatar_url' in data:
            character.avatar_url = data['avatar_url']
        if 'agilidade' in data:
            agi = _safe_int(data['agilidade'])
            if agi is not None and agi >= 0:
                character.agilidade = agi
        if 'intelecto' in data:
            inte = _safe_int(data['intelecto'])
            if inte is not None and inte >= 0:
                character.intelecto = inte
        if 'vigor' in data:
            vig = _safe_int(data['vigor'])
            if vig is not None and vig >= 0:
                character.vigor = vig
        if 'presenca' in data:
            pre = _safe_int(data['presenca'])
            if pre is not None and pre >= 0:
                character.presenca = pre
        if 'forca' in data:
            forc = _safe_int(data['forca'])
            if forc is not None and forc >= 0:
                character.forca = forc
        if 'gender' in data:
            character.gender = data['gender']
        if 'appearance' in data:
            character.appearance = data['appearance']
        if 'personality' in data:
            character.personality = data['personality']
        if 'background' in data:
            character.background = data['background']
        if 'objective' in data:
            character.objective = data['objective']
        
        db.session.commit()
        
        return jsonify({
            'message': 'character_updated',
            'data': character.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'error_updating_character',
            'error': str(e)
        }), 500

@user_character_bp.route('/<int:character_id>', methods=['DELETE'])
@jwt_required()
def delete_user_character(character_id):
    """Deleta um personagem do usuário autenticado"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'user_not_found'}), 404
        
        character = Character.query.filter_by(
            id=character_id,
            user_id=user_id
        ).first()
        
        if not character:
            return jsonify({
                'message': 'character_not_found',
                'error_detail': 'Personagem não encontrado ou não pertence a este usuário'
            }), 404
        
        db.session.delete(character)
        db.session.commit()
        
        return jsonify({
            'message': 'character_deleted'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'error_deleting_character',
            'error': str(e)
        }), 500
