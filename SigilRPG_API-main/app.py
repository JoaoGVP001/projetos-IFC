"""
RESTful API para RPG básico - Flask
Convertido de Laravel/Lumen para Flask
"""

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import random

# Importar modelos primeiro
from models import db, User, Character, Fight

# Inicializar Flask app
app = Flask(__name__)

# Configurações
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///rpg.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Desabilitar redirecionamento automático de trailing slash
app.url_map.strict_slashes = False

# Inicializar extensões
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app, origins=['*'], methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'], allow_headers=['Content-Type', 'Authorization'])

# Importar rotas
from routes import auth_bp
from characters_routes import characters_bp
from user_character_routes import user_character_bp
from fights_routes import fights_bp

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(characters_bp, url_prefix='/api/characters')
app.register_blueprint(user_character_bp, url_prefix='/api/me')
app.register_blueprint(fights_bp, url_prefix='/api/me/fights')

@app.route('/')
def index():
    return jsonify({
        'message': 'RESTful API para RPG básico',
        'version': '1.0',
        'framework': 'Flask'
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8000)
