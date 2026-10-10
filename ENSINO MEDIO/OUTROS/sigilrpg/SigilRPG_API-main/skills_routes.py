"""
Rotas para habilidades de personagem
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Character, Skill

skills_bp = Blueprint('skills', __name__)

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

@skills_bp.route('/<int:character_id>/skills', methods=['GET'])
@jwt_required()
def list_skills(character_id):
    """Lista todas as habilidades de um personagem"""
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
        
        skills = Skill.query.filter_by(character_id=character_id).all()
        
        return jsonify({
            'message': 'skills',
            'data': [skill.to_dict() for skill in skills]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'error_retrieving_skills', 'error': str(e)}), 500

@skills_bp.route('/<int:character_id>/skills/<int:skill_id>', methods=['GET'])
@jwt_required()
def show_skill(character_id, skill_id):
    """Mostra uma habilidade específica"""
    try:
        user_id = get_jwt_identity()
        character = Character.query.filter_by(
            id=character_id,
            user_id=user_id
        ).first()
        
        if not character:
            return jsonify({'message': 'character_not_found'}), 404
        
        skill = Skill.query.filter_by(
            id=skill_id,
            character_id=character_id
        ).first()
        
        if not skill:
            return jsonify({'message': 'skill_not_found'}), 404
        
        return jsonify({
            'message': 'skill',
            'data': skill.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'error_retrieving_skill', 'error': str(e)}), 500

@skills_bp.route('/<int:character_id>/skills', methods=['POST'])
@jwt_required()
def create_skill(character_id):
    """Cria uma nova habilidade"""
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
        
        skill = Skill(
            character_id=character_id,
            name=data['name'].strip(),
            attribute=data.get('attribute', 'AGI'),
            bonus_dice=_safe_int(data.get('bonus_dice'), 0),
            training=_safe_int(data.get('training'), 0),
            others=_safe_int(data.get('others'), 0),
            description=data.get('description', '').strip() if data.get('description') else None
        )
        
        db.session.add(skill)
        db.session.commit()
        
        return jsonify({
            'message': 'skill_created',
            'data': skill.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'error_creating_skill', 'error': str(e)}), 500

@skills_bp.route('/<int:character_id>/skills/<int:skill_id>', methods=['PATCH'])
@jwt_required()
def update_skill(character_id, skill_id):
    """Atualiza uma habilidade"""
    try:
        user_id = get_jwt_identity()
        character = Character.query.filter_by(
            id=character_id,
            user_id=user_id
        ).first()
        
        if not character:
            return jsonify({'message': 'character_not_found'}), 404
        
        skill = Skill.query.filter_by(
            id=skill_id,
            character_id=character_id
        ).first()
        
        if not skill:
            return jsonify({'message': 'skill_not_found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'invalid_data'}), 400
        
        if 'name' in data:
            skill.name = data['name'].strip()
        if 'attribute' in data:
            skill.attribute = data['attribute']
        if 'bonus_dice' in data:
            skill.bonus_dice = _safe_int(data['bonus_dice'], 0)
        if 'training' in data:
            skill.training = _safe_int(data['training'], 0)
        if 'others' in data:
            skill.others = _safe_int(data['others'], 0)
        if 'description' in data:
            skill.description = data['description'].strip() if data['description'] else None
        
        db.session.commit()
        
        return jsonify({
            'message': 'skill_updated',
            'data': skill.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'error_updating_skill', 'error': str(e)}), 500

@skills_bp.route('/<int:character_id>/skills/<int:skill_id>', methods=['DELETE'])
@jwt_required()
def delete_skill(character_id, skill_id):
    """Deleta uma habilidade"""
    try:
        user_id = get_jwt_identity()
        character = Character.query.filter_by(
            id=character_id,
            user_id=user_id
        ).first()
        
        if not character:
            return jsonify({'message': 'character_not_found'}), 404
        
        skill = Skill.query.filter_by(
            id=skill_id,
            character_id=character_id
        ).first()
        
        if not skill:
            return jsonify({'message': 'skill_not_found'}), 404
        
        db.session.delete(skill)
        db.session.commit()
        
        return jsonify({'message': 'skill_deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'error_deleting_skill', 'error': str(e)}), 500

