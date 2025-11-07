"""Rotas para gerenciamento de campanhas, personagens e equipes"""

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from models import (
    db,
    Campaign,
    Character,
    CampaignCharacter,
    Party,
    PartyMember,
)


campaigns_bp = Blueprint('campaigns', __name__)


def _parse_bool(value, default=None):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {'true', '1', 'yes', 'y', 'sim'}:
            return True
        if lowered in {'false', '0', 'no', 'n', 'nao', 'não'}:
            return False
    return default


def _campaign_not_found():
    return jsonify({'message': 'campaign_not_found'}), 404


def _character_not_found():
    return jsonify({'message': 'character_not_found'}), 404


@campaigns_bp.route('/', methods=['GET'])
def list_campaigns():
    """Lista todas as campanhas"""
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    return jsonify([campaign.to_dict() for campaign in campaigns]), 200


@campaigns_bp.route('/', methods=['POST'])
def create_campaign():
    """Cria uma nova campanha"""
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    master_name = (data.get('master_name') or '').strip()

    if not name:
        return jsonify({'message': 'name_required'}), 400

    if not master_name:
        return jsonify({'message': 'master_name_required'}), 400

    try:
        campaign = Campaign(
            name=name,
            description=data.get('description') or '',
            system=data.get('system') or 'Sigil RPG',
            max_players=int(data.get('max_players') or 6),
            is_active=_parse_bool(data.get('is_active'), True),
            is_public=_parse_bool(data.get('is_public'), False),
            setting=data.get('setting') or '',
            rules=data.get('rules') or '',
            notes=data.get('notes') or '',
            master_name=master_name,
        )

        db.session.add(campaign)
        db.session.commit()

        return jsonify(campaign.to_dict()), 201

    except Exception as exc:
        db.session.rollback()
        return jsonify({'message': 'error_creating_campaign', 'error': str(exc)}), 500


@campaigns_bp.route('/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Obtém os detalhes de uma campanha"""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _campaign_not_found()

    return jsonify(campaign.to_dict(include_members=True, include_parties=True)), 200


@campaigns_bp.route('/<int:campaign_id>', methods=['PATCH'])
def update_campaign(campaign_id):
    """Atualiza uma campanha existente"""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _campaign_not_found()

    data = request.get_json() or {}

    try:
        if 'name' in data and data['name']:
            campaign.name = data['name'].strip()
        if 'description' in data:
            campaign.description = data.get('description') or ''
        if 'system' in data:
            campaign.system = data.get('system') or 'Sigil RPG'
        if 'max_players' in data:
            try:
                campaign.max_players = int(data.get('max_players'))
            except (TypeError, ValueError):
                return jsonify({'message': 'invalid_max_players'}), 400
        if 'is_active' in data:
            campaign.is_active = _parse_bool(data.get('is_active'), campaign.is_active)
        if 'is_public' in data:
            campaign.is_public = _parse_bool(data.get('is_public'), campaign.is_public)
        if 'setting' in data:
            campaign.setting = data.get('setting') or ''
        if 'rules' in data:
            campaign.rules = data.get('rules') or ''
        if 'notes' in data:
            campaign.notes = data.get('notes') or ''
        if 'master_name' in data and data['master_name']:
            campaign.master_name = data['master_name'].strip()

        db.session.commit()

        return jsonify(campaign.to_dict(include_members=True, include_parties=True)), 200

    except Exception as exc:
        db.session.rollback()
        return jsonify({'message': 'error_updating_campaign', 'error': str(exc)}), 500


@campaigns_bp.route('/<int:campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    """Remove uma campanha"""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _campaign_not_found()

    try:
        db.session.delete(campaign)
        db.session.commit()
        return jsonify({'message': 'campaign_deleted'}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({'message': 'error_deleting_campaign', 'error': str(exc)}), 500


@campaigns_bp.route('/<int:campaign_id>/characters', methods=['GET'])
def list_campaign_characters(campaign_id):
    """Lista personagens vinculados a uma campanha"""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _campaign_not_found()

    memberships = (
        CampaignCharacter.query.filter_by(campaign_id=campaign_id)
        .order_by(CampaignCharacter.joined_at.asc())
        .all()
    )
    return (
        jsonify([
            membership.to_dict(include_character=True)
            for membership in memberships
        ]),
        200,
    )


@campaigns_bp.route('/<int:campaign_id>/characters', methods=['POST'])
def add_character_to_campaign(campaign_id):
    """Vincula um personagem a uma campanha"""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _campaign_not_found()

    data = request.get_json() or {}
    character_id = data.get('character_id')

    if not character_id:
        return jsonify({'message': 'character_id_required'}), 400

    character = Character.query.get(character_id)
    if not character:
        return _character_not_found()

    try:
        membership = CampaignCharacter(
            campaign_id=campaign.id,
            character_id=character.id,
            role=data.get('role'),
            is_active=_parse_bool(data.get('is_active'), True),
            notes=data.get('notes'),
        )

        db.session.add(membership)
        db.session.commit()

        return jsonify(membership.to_dict(include_character=True)), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'character_already_in_campaign'}), 409
    except Exception as exc:
        db.session.rollback()
        return jsonify({'message': 'error_linking_character', 'error': str(exc)}), 500


@campaigns_bp.route('/<int:campaign_id>/characters/<int:character_id>', methods=['PATCH'])
def update_campaign_character(campaign_id, character_id):
    """Atualiza dados do vínculo do personagem com a campanha"""
    membership = CampaignCharacter.query.filter_by(
        campaign_id=campaign_id,
        character_id=character_id,
    ).first()

    if not membership:
        return jsonify({'message': 'campaign_character_not_found'}), 404

    data = request.get_json() or {}

    try:
        if 'role' in data:
            membership.role = data.get('role')
        if 'is_active' in data:
            membership.is_active = _parse_bool(data.get('is_active'), membership.is_active)
        if 'notes' in data:
            membership.notes = data.get('notes')

        db.session.commit()

        return jsonify(membership.to_dict(include_character=True)), 200

    except Exception as exc:
        db.session.rollback()
        return jsonify({'message': 'error_updating_campaign_character', 'error': str(exc)}), 500


@campaigns_bp.route('/<int:campaign_id>/characters/<int:character_id>', methods=['DELETE'])
def remove_character_from_campaign(campaign_id, character_id):
    """Remove o vínculo de um personagem com a campanha"""
    membership = CampaignCharacter.query.filter_by(
        campaign_id=campaign_id,
        character_id=character_id,
    ).first()

    if not membership:
        return jsonify({'message': 'campaign_character_not_found'}), 404

    try:
        db.session.delete(membership)
        db.session.commit()
        return jsonify({'message': 'campaign_character_removed'}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({'message': 'error_removing_campaign_character', 'error': str(exc)}), 500


@campaigns_bp.route('/<int:campaign_id>/parties', methods=['GET'])
def list_parties(campaign_id):
    """Lista equipes de uma campanha"""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _campaign_not_found()

    parties = Party.query.filter_by(campaign_id=campaign_id).order_by(Party.created_at.asc()).all()
    return jsonify([party.to_dict(include_members=True) for party in parties]), 200


@campaigns_bp.route('/<int:campaign_id>/parties', methods=['POST'])
def create_party(campaign_id):
    """Cria uma nova equipe para a campanha"""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _campaign_not_found()

    data = request.get_json() or {}
    name = (data.get('name') or '').strip()

    if not name:
        return jsonify({'message': 'name_required'}), 400

    try:
        party = Party(
            campaign_id=campaign.id,
            name=name,
            description=data.get('description'),
        )

        db.session.add(party)
        db.session.commit()

        return jsonify(party.to_dict(include_members=True)), 201

    except Exception as exc:
        db.session.rollback()
        return jsonify({'message': 'error_creating_party', 'error': str(exc)}), 500


@campaigns_bp.route('/<int:campaign_id>/parties/<int:party_id>', methods=['PATCH'])
def update_party(campaign_id, party_id):
    """Atualiza dados de uma equipe"""
    party = Party.query.filter_by(id=party_id, campaign_id=campaign_id).first()
    if not party:
        return jsonify({'message': 'party_not_found'}), 404

    data = request.get_json() or {}

    try:
        if 'name' in data and data['name']:
            party.name = data['name'].strip()
        if 'description' in data:
            party.description = data.get('description')

        db.session.commit()

        return jsonify(party.to_dict(include_members=True)), 200

    except Exception as exc:
        db.session.rollback()
        return jsonify({'message': 'error_updating_party', 'error': str(exc)}), 500


@campaigns_bp.route('/<int:campaign_id>/parties/<int:party_id>', methods=['DELETE'])
def delete_party(campaign_id, party_id):
    """Remove uma equipe"""
    party = Party.query.filter_by(id=party_id, campaign_id=campaign_id).first()
    if not party:
        return jsonify({'message': 'party_not_found'}), 404

    try:
        db.session.delete(party)
        db.session.commit()
        return jsonify({'message': 'party_deleted'}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({'message': 'error_deleting_party', 'error': str(exc)}), 500


def _party_member_filter(campaign_id, party_id, character_id):
    return PartyMember.query.join(Party).filter(
        PartyMember.party_id == party_id,
        PartyMember.character_id == character_id,
        Party.campaign_id == campaign_id,
    )


@campaigns_bp.route('/<int:campaign_id>/parties/<int:party_id>/members', methods=['POST'])
def add_member_to_party(campaign_id, party_id):
    """Adiciona um personagem a uma equipe"""
    party = Party.query.filter_by(id=party_id, campaign_id=campaign_id).first()
    if not party:
        return jsonify({'message': 'party_not_found'}), 404

    data = request.get_json() or {}
    character_id = data.get('character_id')

    if not character_id:
        return jsonify({'message': 'character_id_required'}), 400

    character = Character.query.get(character_id)
    if not character:
        return _character_not_found()

    # Garantir que o personagem esteja vinculado à campanha
    membership = CampaignCharacter.query.filter_by(
        campaign_id=campaign_id,
        character_id=character_id,
    ).first()

    if not membership:
        return jsonify({'message': 'character_not_in_campaign'}), 409

    try:
        party_member = PartyMember(
            party_id=party.id,
            character_id=character.id,
            role=data.get('role'),
        )

        db.session.add(party_member)
        db.session.commit()

        return jsonify(party_member.to_dict(include_character=True)), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'character_already_in_party'}), 409
    except Exception as exc:
        db.session.rollback()
        return jsonify({'message': 'error_adding_party_member', 'error': str(exc)}), 500


@campaigns_bp.route('/<int:campaign_id>/parties/<int:party_id>/members/<int:character_id>', methods=['PATCH'])
def update_party_member(campaign_id, party_id, character_id):
    """Atualiza informações do membro da equipe"""
    party_member = _party_member_filter(campaign_id, party_id, character_id).first()

    if not party_member:
        return jsonify({'message': 'party_member_not_found'}), 404

    data = request.get_json() or {}

    try:
        if 'role' in data:
            party_member.role = data.get('role')

        db.session.commit()

        return jsonify(party_member.to_dict(include_character=True)), 200

    except Exception as exc:
        db.session.rollback()
        return jsonify({'message': 'error_updating_party_member', 'error': str(exc)}), 500


@campaigns_bp.route('/<int:campaign_id>/parties/<int:party_id>/members/<int:character_id>', methods=['DELETE'])
def remove_party_member(campaign_id, party_id, character_id):
    """Remove um personagem da equipe"""
    party_member = _party_member_filter(campaign_id, party_id, character_id).first()

    if not party_member:
        return jsonify({'message': 'party_member_not_found'}), 404

    try:
        db.session.delete(party_member)
        db.session.commit()
        return jsonify({'message': 'party_member_removed'}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({'message': 'error_removing_party_member', 'error': str(exc)}), 500

