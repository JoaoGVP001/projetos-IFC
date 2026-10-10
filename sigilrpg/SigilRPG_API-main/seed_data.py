"""
Script para popular o banco de dados com dados iniciais
"""

from app import app, db
from models import (
    User,
    Character,
    Fight,
    Campaign,
    CampaignCharacter,
    Party,
    PartyMember,
)
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
        
        # Criar campanhas de exemplo
        campaigns_data = [
            {
                'name': 'Defensores de Sigil',
                'description': 'Campanha oficial da Ordem para proteger Sigil das ameaças paranormais.',
                'master_name': 'João Silva',
                'system': 'Sigil RPG',
                'max_players': 5,
                'is_active': True,
                'is_public': True,
                'setting': 'Sigil City',
                'rules': 'Regulamento interno da Ordem.',
                'notes': 'Sessões semanais às quintas.',
            },
            {
                'name': 'Sombras do Passado',
                'description': 'Campanha investigativa com foco em mistérios e horror psicológico.',
                'master_name': 'Maria Santos',
                'system': 'Sigil RPG',
                'max_players': 4,
                'is_active': False,
                'is_public': False,
                'setting': 'Interior do Brasil, década de 90',
                'rules': 'Adaptação narrativa com checkpoints reduzidos.',
                'notes': 'Retorno previsto para o próximo trimestre.',
            },
        ]

        campaigns = []
        for campaign_data in campaigns_data:
            campaign = Campaign(**campaign_data)
            campaigns.append(campaign)
            db.session.add(campaign)

        db.session.commit()

        # Vincular personagens às campanhas
        campaign_memberships = [
            {
                'campaign': campaigns[0],
                'character': characters[0],  # Aragorn
                'role': 'Líder tático',
            },
            {
                'campaign': campaigns[0],
                'character': characters[1],  # Legolas
                'role': 'Especialista em reconhecimento',
            },
            {
                'campaign': campaigns[0],
                'character': characters[2],  # Gandalf
                'role': 'Consultor arcano',
            },
            {
                'campaign': campaigns[1],
                'character': characters[3],  # Gimli
                'role': 'Contato da Ordem',
            },
            {
                'campaign': campaigns[1],
                'character': characters[4],  # Frodo
                'role': 'Investigador de campo',
            },
        ]

        for membership_data in campaign_memberships:
            membership = CampaignCharacter(
                campaign_id=membership_data['campaign'].id,
                character_id=membership_data['character'].id,
                role=membership_data.get('role'),
            )
            db.session.add(membership)

        db.session.commit()

        # Criar equipes (parties) para as campanhas
        parties = []
        party_specs = [
            {
                'campaign': campaigns[0],
                'name': 'Força de Resposta Alfa',
                'description': 'Equipe principal de incursão.',
                'members': [
                    {'character': characters[0], 'role': 'Comandante'},
                    {'character': characters[1], 'role': 'Atirador de elite'},
                ],
            },
            {
                'campaign': campaigns[0],
                'name': 'Suporte Arcano',
                'description': 'Equipe dedicada a suporte mágico.',
                'members': [
                    {'character': characters[2], 'role': 'Mago de campo'},
                ],
            },
        ]

        for party_spec in party_specs:
            party = Party(
                campaign_id=party_spec['campaign'].id,
                name=party_spec['name'],
                description=party_spec.get('description'),
            )
            db.session.add(party)
            db.session.flush()  # Garantir ID para membros
            parties.append(party)

            for member_info in party_spec.get('members', []):
                party_member = PartyMember(
                    party_id=party.id,
                    character_id=member_info['character'].id,
                    role=member_info.get('role'),
                )
                db.session.add(party_member)

        db.session.commit()

        print("Dados de exemplo criados com sucesso!")
        print(f"Criados {len(users)} usuários")
        print(f"Criados {len(characters)} personagens")
        print(f"Criadas {len(fights_data)} lutas")
        print(f"Criadas {len(campaigns)} campanhas")
        print(f"Criados {len(campaign_memberships)} vínculos de campanha")
        print(f"Criadas {len(parties)} equipes")

if __name__ == '__main__':
    create_sample_data()


