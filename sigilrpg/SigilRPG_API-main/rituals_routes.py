"""
Rotas para rituais de personagem
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Character, Ritual

rituals_bp = Blueprint('rituals', __name__)

def _safe_int(value, default=None):
    """Converte um valor para int de forma segura"""
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

@rituals_bp.route('/<int:character_id>/rituals', methods=['GET'])
@jwt_required()
def list_rituals(character_id):
    """Lista todos os rituais de um personagem"""
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
            return jsonify({'message': 'character_not_found'}), 404
        
        rituals = Ritual.query.filter_by(character_id=character_id).all()
        
        return jsonify({
            'message': 'rituals',
            'data': [ritual.to_dict() for ritual in rituals]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'error_retrieving_rituals', 'error': str(e)}), 500

@rituals_bp.route('/<int:character_id>/rituals/<int:ritual_id>', methods=['GET'])
@jwt_required()
def show_ritual(character_id, ritual_id):
    """Mostra um ritual específico"""
    try:
        user_id = get_jwt_identity()
        character = Character.query.filter_by(
            id=character_id,
            user_id=user_id
        ).first()
        
        if not character:
            return jsonify({'message': 'character_not_found'}), 404
        
        ritual = Ritual.query.filter_by(
            id=ritual_id,
            character_id=character_id
        ).first()
        
        if not ritual:
            return jsonify({'message': 'ritual_not_found'}), 404
        
        return jsonify({
            'message': 'ritual',
            'data': ritual.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'error_retrieving_ritual', 'error': str(e)}), 500

@rituals_bp.route('/<int:character_id>/rituals', methods=['POST'])
@jwt_required()
def create_ritual(character_id):
    """Cria um novo ritual"""
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
            return jsonify({'message': 'character_not_found'}), 404
        
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'message': 'invalid_data'}), 400
        
        ritual = Ritual(
            character_id=character_id,
            name=data['name'].strip(),
            circle=_safe_int(data.get('circle'), 1),
            cost=_safe_int(data.get('cost'), 0),
            execution_time=data.get('execution_time', '').strip() if data.get('execution_time') else None,
            range=data.get('range', '').strip() if data.get('range') else None,
            duration=data.get('duration', '').strip() if data.get('duration') else None,
            resistance_test=data.get('resistance_test', '').strip() if data.get('resistance_test') else None,
            description=data.get('description', '').strip() if data.get('description') else None,
            effect=data.get('effect', '').strip() if data.get('effect') else None
        )
        
        db.session.add(ritual)
        db.session.commit()
        
        return jsonify({
            'message': 'ritual_created',
            'data': ritual.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'error_creating_ritual', 'error': str(e)}), 500

@rituals_bp.route('/<int:character_id>/rituals/<int:ritual_id>', methods=['PATCH'])
@jwt_required()
def update_ritual(character_id, ritual_id):
    """Atualiza um ritual"""
    try:
        user_id = get_jwt_identity()
        character = Character.query.filter_by(
            id=character_id,
            user_id=user_id
        ).first()
        
        if not character:
            return jsonify({'message': 'character_not_found'}), 404
        
        ritual = Ritual.query.filter_by(
            id=ritual_id,
            character_id=character_id
        ).first()
        
        if not ritual:
            return jsonify({'message': 'ritual_not_found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'invalid_data'}), 400
        
        if 'name' in data:
            ritual.name = data['name'].strip()
        if 'circle' in data:
            ritual.circle = _safe_int(data['circle'], 1)
        if 'cost' in data:
            ritual.cost = _safe_int(data['cost'], 0)
        if 'execution_time' in data:
            ritual.execution_time = data['execution_time'].strip() if data['execution_time'] else None
        if 'range' in data:
            ritual.range = data['range'].strip() if data['range'] else None
        if 'duration' in data:
            ritual.duration = data['duration'].strip() if data['duration'] else None
        if 'resistance_test' in data:
            ritual.resistance_test = data['resistance_test'].strip() if data['resistance_test'] else None
        if 'description' in data:
            ritual.description = data['description'].strip() if data['description'] else None
        if 'effect' in data:
            ritual.effect = data['effect'].strip() if data['effect'] else None
        
        db.session.commit()
        
        return jsonify({
            'message': 'ritual_updated',
            'data': ritual.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'error_updating_ritual', 'error': str(e)}), 500

@rituals_bp.route('/<int:character_id>/rituals/<int:ritual_id>', methods=['DELETE'])
@jwt_required()
def delete_ritual(character_id, ritual_id):
    """Deleta um ritual"""
    try:
        user_id = get_jwt_identity()
        character = Character.query.filter_by(
            id=character_id,
            user_id=user_id
        ).first()
        
        if not character:
            return jsonify({'message': 'character_not_found'}), 404
        
        ritual = Ritual.query.filter_by(
            id=ritual_id,
            character_id=character_id
        ).first()
        
        if not ritual:
            return jsonify({'message': 'ritual_not_found'}), 404
        
        db.session.delete(ritual)
        db.session.commit()
        
        return jsonify({'message': 'ritual_deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'error_deleting_ritual', 'error': str(e)}), 500

