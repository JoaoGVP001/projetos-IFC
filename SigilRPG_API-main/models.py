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
    
    def to_dict(self):
        """Converte o personagem para dicionário"""
        return {
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