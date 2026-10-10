"""
Rotas para lutas
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Character, Fight
import random

fights_bp = Blueprint('fights', __name__)

@fights_bp.route('/', methods=['GET'])
@jwt_required()
def list_user_fights():
    """Lista as lutas do personagem do usuário autenticado"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'user_not_found'}), 404
        
        character = Character.query.filter_by(user_id=user_id).first()
        
        if not character:
            return jsonify({
                'message': 'character_not_exist',
                'error_detail': 'Luta pertence a personagens, então primeiro crie um personagem'
            }), 400
        
        fights = Fight.query.filter_by(character_id=character.id).all()
        
        return jsonify({
            'message': 'fights_list',
            'data': [fight.to_dict() for fight in fights]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'error_retrieving_fights'}), 500

@fights_bp.route('/', methods=['POST'])
@jwt_required()
def create_fight():
    """Cria uma nova luta para o personagem do usuário"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'user_not_found'}), 404
        
        character = Character.query.filter_by(user_id=user_id).first()
        
        if not character:
            return jsonify({
                'message': 'character_not_exist',
                'error_detail': 'Luta pertence a personagens, então primeiro crie um personagem'
            }), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'invalid_data'}), 400
        
        opponent_id = data.get('opponent_id')
        
        if not opponent_id:
            return jsonify({'message': 'opponent_id_required'}), 400
        
        # Buscar oponente
        opponent = Character.query.get(opponent_id)
        
        if not opponent:
            return jsonify({'message': 'opponent_not_found'}), 404
        
        # Validar se não está lutando contra si mesmo
        if opponent.id == character.id:
            return jsonify({'message': 'cannot_fight_yourself'}), 400
        
        # Simular resultado da luta
        # Em um jogo real, isso seria baseado em estatísticas dos personagens
        fight_outcomes = ['won', 'lost', 'draw']
        status = random.choice(fight_outcomes)
        
        # Calcular experiência baseada no resultado
        if status == 'won':
            experience = random.randint(50, 100)
        elif status == 'lost':
            experience = random.randint(10, 30)
        else:  # draw
            experience = random.randint(20, 40)
        
        # Criar luta
        fight = Fight(
            character_id=character.id,
            opponent_id=opponent.id,
            status=status,
            experience=experience
        )
        
        db.session.add(fight)
        db.session.commit()
        
        return jsonify({
            'message': 'fight_completed',
            'data': fight.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'error_creating_fight'}), 500
