"""
Rotas para itens de personagem
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Character, Item

items_bp = Blueprint('items', __name__)

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

def _safe_float(value, default=None):
    """Converte um valor para float de forma segura"""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

@items_bp.route('/<int:character_id>/items', methods=['GET'])
@jwt_required()
def list_items(character_id):
    """Lista todos os itens de um personagem"""
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
        
        items = Item.query.filter_by(character_id=character_id).all()
        
        return jsonify({
            'message': 'items',
            'data': [item.to_dict() for item in items]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'error_retrieving_items', 'error': str(e)}), 500

@items_bp.route('/<int:character_id>/items/<int:item_id>', methods=['GET'])
@jwt_required()
def show_item(character_id, item_id):
    """Mostra um item específico"""
    try:
        user_id = get_jwt_identity()
        character = Character.query.filter_by(
            id=character_id,
            user_id=user_id
        ).first()
        
        if not character:
            return jsonify({'message': 'character_not_found'}), 404
        
        item = Item.query.filter_by(
            id=item_id,
            character_id=character_id
        ).first()
        
        if not item:
            return jsonify({'message': 'item_not_found'}), 404
        
        return jsonify({
            'message': 'item',
            'data': item.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'error_retrieving_item', 'error': str(e)}), 500

@items_bp.route('/<int:character_id>/items', methods=['POST'])
@jwt_required()
def create_item(character_id):
    """Cria um novo item"""
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
        
        item = Item(
            character_id=character_id,
            name=data['name'].strip(),
            category=data.get('category', 'equipamento').strip(),
            weight=_safe_float(data.get('weight'), 0.0),
            description=data.get('description', '').strip() if data.get('description') else None,
            quantity=_safe_int(data.get('quantity'), 1)
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'message': 'item_created',
            'data': item.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'error_creating_item', 'error': str(e)}), 500

@items_bp.route('/<int:character_id>/items/<int:item_id>', methods=['PATCH'])
@jwt_required()
def update_item(character_id, item_id):
    """Atualiza um item"""
    try:
        user_id = get_jwt_identity()
        character = Character.query.filter_by(
            id=character_id,
            user_id=user_id
        ).first()
        
        if not character:
            return jsonify({'message': 'character_not_found'}), 404
        
        item = Item.query.filter_by(
            id=item_id,
            character_id=character_id
        ).first()
        
        if not item:
            return jsonify({'message': 'item_not_found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'invalid_data'}), 400
        
        if 'name' in data:
            item.name = data['name'].strip()
        if 'category' in data:
            item.category = data['category'].strip()
        if 'weight' in data:
            item.weight = _safe_float(data['weight'], 0.0)
        if 'description' in data:
            item.description = data['description'].strip() if data['description'] else None
        if 'quantity' in data:
            item.quantity = _safe_int(data['quantity'], 1)
        
        db.session.commit()
        
        return jsonify({
            'message': 'item_updated',
            'data': item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'error_updating_item', 'error': str(e)}), 500

@items_bp.route('/<int:character_id>/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(character_id, item_id):
    """Deleta um item"""
    try:
        user_id = get_jwt_identity()
        character = Character.query.filter_by(
            id=character_id,
            user_id=user_id
        ).first()
        
        if not character:
            return jsonify({'message': 'character_not_found'}), 404
        
        item = Item.query.filter_by(
            id=item_id,
            character_id=character_id
        ).first()
        
        if not item:
            return jsonify({'message': 'item_not_found'}), 404
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'message': 'item_deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'error_deleting_item', 'error': str(e)}), 500

