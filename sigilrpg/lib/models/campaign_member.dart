import 'package:sigilrpg/models/character.dart';

class CampaignMember {
  final String id;
  final String campaignId;
  final String characterId;
  final String? role;
  final bool isActive;
  final String? notes;
  final DateTime? joinedAt;
  final Character? character;

  const CampaignMember({
    required this.id,
    required this.campaignId,
    required this.characterId,
    this.role,
    this.isActive = true,
    this.notes,
    this.joinedAt,
    this.character,
  });

  factory CampaignMember.fromJson(Map<String, dynamic> json) {
    return CampaignMember(
      id: json['id'].toString(),
      campaignId: json['campaign_id'].toString(),
      characterId: json['character_id'].toString(),
      role: json['role'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      notes: json['notes'] as String?,
      joinedAt: json['joined_at'] != null
          ? DateTime.tryParse(json['joined_at'] as String)
          : null,
      character: json['character'] != null
          ? Character.fromJson(json['character'] as Map<String, dynamic>)
          : null,
    );
  }
}

