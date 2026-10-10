import 'package:sigilrpg/models/character.dart';

class TeamMember {
  final String id;
  final String partyId;
  final String characterId;
  final String? role;
  final DateTime? joinedAt;
  final Character? character;

  const TeamMember({
    required this.id,
    required this.partyId,
    required this.characterId,
    this.role,
    this.joinedAt,
    this.character,
  });

  factory TeamMember.fromJson(Map<String, dynamic> json) {
    return TeamMember(
      id: json['id'].toString(),
      partyId: json['party_id'].toString(),
      characterId: json['character_id'].toString(),
      role: json['role'] as String?,
      joinedAt: json['joined_at'] != null
          ? DateTime.tryParse(json['joined_at'] as String)
          : null,
      character: json['character'] != null
          ? Character.fromJson(json['character'] as Map<String, dynamic>)
          : null,
    );
  }
}

class Team {
  final String id;
  final String campaignId;
  final String name;
  final String? description;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  final List<TeamMember> members;
  final String? campaignName;

  const Team({
    required this.id,
    required this.campaignId,
    required this.name,
    this.description,
    this.createdAt,
    this.updatedAt,
    this.members = const [],
    this.campaignName,
  });

  factory Team.fromJson(Map<String, dynamic> json, {String? campaignName}) {
    final membersJson = json['members'] as List<dynamic>?;
    return Team(
      id: json['id'].toString(),
      campaignId: json['campaign_id'].toString(),
      name: json['name'] as String? ?? '',
      description: json['description'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String)
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.tryParse(json['updated_at'] as String)
          : null,
      members: membersJson == null
          ? const []
          : membersJson
              .map((e) => TeamMember.fromJson(e as Map<String, dynamic>))
              .toList(),
      campaignName: campaignName,
    );
  }

  Team copyWith({List<TeamMember>? members}) {
    return Team(
      id: id,
      campaignId: campaignId,
      name: name,
      description: description,
      createdAt: createdAt,
      updatedAt: updatedAt,
      members: members ?? this.members,
      campaignName: campaignName,
    );
  }
}
