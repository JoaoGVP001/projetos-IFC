"""
Script para popular o banco de dados com dados iniciais
"""

from app import app, db
from models import User, Character, Fight
from werkzeug.security import generate_password_hash

def create_sample_data():
    """Cria dados de exemplo para testar a API"""
    
    with app.app_context():
        # Limpar dados existentes
        db.drop_all()
        db.create_all()
        
        # Criar usuários de exemplo
        users_data = [
            {
                'name': 'João Silva',
                'email': 'joao@example.com',
                'password': '123456'
            },
            {
                'name': 'Maria Santos',
                'email': 'maria@example.com',
                'password': '123456'
            },
            {
                'name': 'Pedro Oliveira',
                'email': 'pedro@example.com',
                'password': '123456'
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                name=user_data['name'],
                email=user_data['email']
            )
            user.set_password(user_data['password'])
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        
        # Criar personagens de exemplo (alguns com usuários, outros sem)
        characters_data = [
            {
                'name': 'Aragorn',
                'age': 35,
                'skilled_in': 'Espada e Arco',
                'user_id': users[0].id
            },
            {
                'name': 'Legolas',
                'age': 2000,
                'skilled_in': 'Arco e Flechas',
                'user_id': users[1].id
            },
            {
                'name': 'Gandalf',
                'age': 2000,
                'skilled_in': 'Magia e Sabedoria',
                'user_id': None
            },
            {
                'name': 'Gimli',
                'age': 150,
                'skilled_in': 'Machado de Guerra',
                'user_id': None
            },
            {
                'name': 'Frodo',
                'age': 50,
                'skilled_in': 'Coragem e Determinação',
                'user_id': None
            }
        ]
        
        characters = []
        for char_data in characters_data:
            character = Character(
                name=char_data['name'],
                age=char_data['age'],
                skilled_in=char_data['skilled_in'],
                user_id=char_data['user_id']
            )
            characters.append(character)
            db.session.add(character)
        
        db.session.commit()
        
        # Criar algumas lutas de exemplo
        fights_data = [
            {
                'character_id': characters[0].id,  # Aragorn
                'opponent_id': characters[2].id,  # Gandalf
                'status': 'won',
                'experience': 75
            },
            {
                'character_id': characters[0].id,  # Aragorn
                'opponent_id': characters[3].id,  # Gimli
                'status': 'draw',
                'experience': 35
            },
            {
                'character_id': characters[1].id,  # Legolas
                'opponent_id': characters[4].id,  # Frodo
                'status': 'won',
                'experience': 60
            }
        ]
        
        for fight_data in fights_data:
            fight = Fight(
                character_id=fight_data['character_id'],
                opponent_id=fight_data['opponent_id'],
                status=fight_data['status'],
                experience=fight_data['experience']
            )
            db.session.add(fight)
        
        db.session.commit()
        
        print("Dados de exemplo criados com sucesso!")
        print(f"Criados {len(users)} usuários")
        print(f"Criados {len(characters)} personagens")
        print(f"Criadas {len(fights_data)} lutas")

if __name__ == '__main__':
    create_sample_data()


