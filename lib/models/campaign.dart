class Campaign {
  final String id;
  final String name;
  final String description;
  final String system;
  final int maxPlayers;
  final bool isActive;
  final bool isPublic;
  final String setting;
  final String rules;
  final String notes;
  final String masterName;
  final DateTime createdAt;
  final DateTime? updatedAt;

  const Campaign({
    required this.id,
    required this.name,
    required this.description,
    this.system = 'Sigil RPG',
    this.maxPlayers = 6,
    this.isActive = true,
    this.isPublic = false,
    this.setting = '',
    this.rules = '',
    this.notes = '',
    required this.masterName,
    required this.createdAt,
    this.updatedAt,
  });

  Campaign copyWith({
    String? id,
    String? name,
    String? description,
    String? system,
    int? maxPlayers,
    bool? isActive,
    bool? isPublic,
    String? setting,
    String? rules,
    String? notes,
    String? masterName,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Campaign(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      system: system ?? this.system,
      maxPlayers: maxPlayers ?? this.maxPlayers,
      isActive: isActive ?? this.isActive,
      isPublic: isPublic ?? this.isPublic,
      setting: setting ?? this.setting,
      rules: rules ?? this.rules,
      notes: notes ?? this.notes,
      masterName: masterName ?? this.masterName,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'system': system,
      'max_players': maxPlayers,
      'is_active': isActive,
      'is_public': isPublic,
      'setting': setting,
      'rules': rules,
      'notes': notes,
      'master_name': masterName,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }

  factory Campaign.fromJson(Map<String, dynamic> json) {
    return Campaign(
      id: json['id'].toString(),
      name: json['name'] as String,
      description: json['description'] as String? ?? '',
      system: json['system'] as String? ?? 'Sigil RPG',
      maxPlayers: json['max_players'] as int? ?? 6,
      isActive: json['is_active'] as bool? ?? true,
      isPublic: json['is_public'] as bool? ?? false,
      setting: json['setting'] as String? ?? '',
      rules: json['rules'] as String? ?? '',
      notes: json['notes'] as String? ?? '',
      masterName: json['master_name'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
    );
  }
}
