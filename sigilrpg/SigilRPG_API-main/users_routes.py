from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@jwt_required()
def list_users():
    """Lista usuários registrados (apenas admin). Regra simples: usuário id=1 é admin."""
    try:
        user_id = get_jwt_identity()
        # Regra de admin simples: id == 1
        if str(user_id) != '1':
            return jsonify({'message': 'forbidden'}), 403

        users = User.query.order_by(User.id.asc()).all()
        return jsonify({
            'message': 'users_list',
            'data': [u.to_dict() for u in users]
        }), 200
    except Exception as e:
        return jsonify({'message': 'error_retrieving_users', 'error': str(e)}), 500


