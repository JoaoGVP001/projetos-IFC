"""
Modelos SQLAlchemy para a API RPG
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Criar instância do SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    remember_token = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos - Permite múltiplos personagens
    characters = db.relationship('Character', backref='user', lazy=True)
    
    def set_password(self, password):
        """Define a senha do usuário"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Converte o usuário para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Character(db.Model):
    __tablename__ = 'characters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    player_name = db.Column(db.String(255), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    skilled_in = db.Column(db.String(255), nullable=False)
    character_class = db.Column(db.String(255), nullable=True)
    nex = db.Column(db.Integer, default=0)
    avatar_url = db.Column(db.String(500), nullable=True)
    
    # Atributos do personagem
    agilidade = db.Column(db.Integer, default=1)
    intelecto = db.Column(db.Integer, default=1)
    vigor = db.Column(db.Integer, default=1)
    presenca = db.Column(db.Integer, default=1)
    forca = db.Column(db.Integer, default=1)
    
    # Detalhes do personagem
    gender = db.Column(db.String(50), nullable=True)
    appearance = db.Column(db.Text, nullable=True)
    personality = db.Column(db.Text, nullable=True)
    background = db.Column(db.Text, nullable=True)
    objective = db.Column(db.Text, nullable=True)
    origin = db.Column(db.String(255), nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    fights = db.relationship('Fight', backref='character', lazy=True, foreign_keys='Fight.character_id')
    skills = db.relationship('Skill', backref='character', lazy=True, cascade='all, delete-orphan')
    rituals = db.relationship('Ritual', backref='character', lazy=True, cascade='all, delete-orphan')
    items = db.relationship('Item', backref='character', lazy=True, cascade='all, delete-orphan')
    campaign_memberships = db.relationship(
        'CampaignCharacter',
        back_populates='character',
        lazy=True,
        cascade='all, delete-orphan'
    )
    party_memberships = db.relationship(
        'PartyMember',
        back_populates='character',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    def to_dict(self, include_relationships=False):
        """Converte o personagem para dicionário"""
        data = {
            'id': self.id,
            'name': self.name,
            'player_name': self.player_name,
            'age': self.age,
            'skilled_in': self.skilled_in,
            'character_class': self.character_class,
            'nex': self.nex,
            'avatar_url': self.avatar_url,
            'agilidade': self.agilidade,
            'intelecto': self.intelecto,
            'vigor': self.vigor,
            'presenca': self.presenca,
            'forca': self.forca,
            'gender': self.gender,
            'appearance': self.appearance,
            'personality': self.personality,
            'background': self.background,
            'objective': self.objective,
            'origin': self.origin,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_relationships:
            data['campaigns'] = [
                membership.to_dict(include_campaign=True, include_character=False)
                for membership in self.campaign_memberships
            ]
            data['parties'] = [
                membership.to_dict(include_party=True, include_character=False)
                for membership in self.party_memberships
            ]

        return data

class Fight(db.Model):
    __tablename__ = 'fights'
    
    id = db.Column(db.Integer, primary_key=True)
    opponent_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    status = db.Column(db.Enum('won', 'lost', 'draw', name='fight_status'), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    opponent = db.relationship('Character', foreign_keys=[opponent_id], backref='opponent_fights')
    
    def to_dict(self):
        """Converte a luta para dicionário"""
        return {
            'id': self.id,
            'opponent_id': self.opponent_id,
            'character_id': self.character_id,
            'status': self.status,
            'experience': self.experience,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    attribute = db.Column(db.String(10), nullable=False)  # AGI, INT, VIG, PRE, FOR
    bonus_dice = db.Column(db.Integer, default=0)
    training = db.Column(db.Integer, default=0)
    others = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Converte a habilidade para dicionário"""
        return {
            'id': self.id,
            'character_id': self.character_id,
            'name': self.name,
            'attribute': self.attribute,
            'bonus_dice': self.bonus_dice,
            'training': self.training,
            'others': self.others,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Ritual(db.Model):
    __tablename__ = 'rituals'
    
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    circle = db.Column(db.Integer, nullable=False)  # Círculo do ritual (1-10)
    cost = db.Column(db.Integer, nullable=False)  # Custo em PE
    execution_time = db.Column(db.String(255), nullable=True)  # Tempo de execução
    range = db.Column(db.String(255), nullable=True)  # Alcance
    duration = db.Column(db.String(255), nullable=True)  # Duração
    resistance_test = db.Column(db.String(255), nullable=True)  # Teste de resistência
    description = db.Column(db.Text, nullable=True)
    effect = db.Column(db.Text, nullable=True)  # Efeito do ritual
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Converte o ritual para dicionário"""
        return {
            'id': self.id,
            'character_id': self.character_id,
            'name': self.name,
            'circle': self.circle,
            'cost': self.cost,
            'execution_time': self.execution_time,
            'range': self.range,
            'duration': self.duration,
            'resistance_test': self.resistance_test,
            'description': self.description,
            'effect': self.effect,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)  # arma, equipamento, consumível, etc.
    weight = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Converte o item para dicionário"""
        return {
            'id': self.id,
            'character_id': self.character_id,
            'name': self.name,
            'category': self.category,
            'weight': self.weight,
            'description': self.description,
            'quantity': self.quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default='')
    system = db.Column(db.String(255), default='Sigil RPG')
    max_players = db.Column(db.Integer, default=6)
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=False)
    setting = db.Column(db.Text, default='')
    rules = db.Column(db.Text, default='')
    notes = db.Column(db.Text, default='')
    master_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    memberships = db.relationship(
        'CampaignCharacter',
        back_populates='campaign',
        lazy=True,
        cascade='all, delete-orphan'
    )
    parties = db.relationship(
        'Party',
        backref='campaign',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self, include_members=False, include_parties=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'system': self.system or 'Sigil RPG',
            'max_players': self.max_players,
            'is_active': bool(self.is_active),
            'is_public': bool(self.is_public),
            'setting': self.setting or '',
            'rules': self.rules or '',
            'notes': self.notes or '',
            'master_name': self.master_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_members:
            data['members'] = [
                membership.to_dict(include_character=True)
                for membership in self.memberships
            ]

        if include_parties:
            data['parties'] = [
                party.to_dict(include_members=True)
                for party in self.parties
            ]

        return data


class CampaignCharacter(db.Model):
    __tablename__ = 'campaign_characters'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    role = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    campaign = db.relationship('Campaign', back_populates='memberships')
    character = db.relationship('Character', back_populates='campaign_memberships')

    __table_args__ = (
        db.UniqueConstraint('campaign_id', 'character_id', name='uq_campaign_character'),
    )

    def to_dict(
        self,
        include_campaign=False,
        include_character=False,
        include_parties=False
    ):
        data = {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'character_id': self.character_id,
            'role': self.role,
            'is_active': bool(self.is_active),
            'notes': self.notes,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }

        if include_campaign and self.campaign:
            data['campaign'] = self.campaign.to_dict()

        if include_character and self.character:
            data['character'] = self.character.to_dict(include_relationships=include_parties)

        return data


class Party(db.Model):
    __tablename__ = 'parties'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    members = db.relationship(
        'PartyMember',
        back_populates='party',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self, include_members=False):
        data = {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_members:
            data['members'] = [
                member.to_dict(include_character=True)
                for member in self.members
            ]

        return data


class PartyMember(db.Model):
    __tablename__ = 'party_members'

    id = db.Column(db.Integer, primary_key=True)
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    role = db.Column(db.String(100), nullable=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    party = db.relationship('Party', back_populates='members')
    character = db.relationship('Character', back_populates='party_memberships')

    __table_args__ = (
        db.UniqueConstraint('party_id', 'character_id', name='uq_party_character'),
    )

    def to_dict(
        self,
        include_party=False,
        include_character=False,
        include_campaign=False
    ):
        data = {
            'id': self.id,
            'party_id': self.party_id,
            'character_id': self.character_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }

        if include_party and self.party:
            data['party'] = self.party.to_dict(include_members=False)

        if include_character and self.character:
            data['character'] = self.character.to_dict(include_relationships=include_campaign)

        if include_campaign and self.party and self.party.campaign:
            data['campaign'] = self.party.campaign.to_dict()

        return data