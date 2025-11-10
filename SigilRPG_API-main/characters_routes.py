"""
Rotas para personagens do sistema
"""

from flask import Blueprint, request, jsonify
from models import db, Character

characters_bp = Blueprint('characters', __name__)

@characters_bp.route('/', methods=['GET'])
def list_characters():
    """Lista todos os personagens do sistema"""
    try:
        characters = Character.query.all()
        
        return jsonify([character.to_dict() for character in characters]), 200
        
    except Exception as e:
        return jsonify({'message': 'error_retrieving_characters'}), 500

@characters_bp.route('/', methods=['POST'])
def create_character():
    """Cria um novo personagem"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'invalid_data', 'error': 'No JSON data provided'}), 400
        
        # Campos obrigatórios
        if not data.get('name'):
            return jsonify({'message': 'name_required', 'error': 'Name field is required'}), 400
        
        # Criar personagem com valores padrão
        character = Character(
            name=data.get('name'),
            player_name=data.get('player_name'),
            age=data.get('age', 20),
            skilled_in=data.get('skilled_in', 'Combat'),
            character_class=data.get('character_class'),
            nex=data.get('nex', 0),
            avatar_url=data.get('avatar_url'),
            agilidade=data.get('agilidade', 1),
            intelecto=data.get('intelecto', 1),
            vigor=data.get('vigor', 1),
            presenca=data.get('presenca', 1),
            forca=data.get('forca', 1),
            gender=data.get('gender'),
            appearance=data.get('appearance'),
            personality=data.get('personality'),
            background=data.get('background'),
            objective=data.get('objective'),
            origin=data.get('origin'),
            user_id=data.get('user_id')
        )
        
        # Inicializar valores de combate com os máximos calculados
        character.initialize_combat_stats()
        
        db.session.add(character)
        db.session.commit()
        
        return jsonify(character.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar personagem: {str(e)}")  # Log do erro
        return jsonify({
            'message': 'error_creating_character', 
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@characters_bp.route('/<int:character_id>', methods=['GET'])
def show_character(character_id):
    """Mostra detalhes de um personagem específico"""
    try:
        character = Character.query.get(character_id)
        
        if not character:
            return jsonify({'message': 'character_not_found'}), 404
        
        return jsonify(character.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': 'error_retrieving_character'}), 500

@characters_bp.route('/<int:character_id>', methods=['PATCH'])
def update_character(character_id):
    """Atualiza um personagem existente"""
    try:
        character = Character.query.get(character_id)
        
        if not character:
            return jsonify({'message': 'character_not_found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'invalid_data'}), 400
        
        # Atualizar campos fornecidos
        if 'name' in data:
            character.name = data['name']
        if 'player_name' in data:
            character.player_name = data['player_name']
        if 'age' in data:
            character.age = data['age']
        if 'skilled_in' in data:
            character.skilled_in = data['skilled_in']
        if 'character_class' in data:
            character.character_class = data['character_class']
        if 'nex' in data:
            character.nex = data['nex']
        if 'avatar_url' in data:
            character.avatar_url = data['avatar_url']
        if 'agilidade' in data:
            character.agilidade = data['agilidade']
        if 'intelecto' in data:
            character.intelecto = data['intelecto']
        if 'vigor' in data:
            character.vigor = data['vigor']
        if 'presenca' in data:
            character.presenca = data['presenca']
        if 'forca' in data:
            character.forca = data['forca']
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
        if 'origin' in data:
            character.origin = data['origin']
        
        db.session.commit()
        
        return jsonify(character.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'error_updating_character'}), 500
