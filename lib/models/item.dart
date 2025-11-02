class Item {
  final String id;
  final String characterId;
  final String name;
  final String category; // armas, equipamento, consumível, etc.
  final double weight;
  final String? description;
  final int quantity;

  const Item({
    required this.id,
    required this.characterId,
    required this.name,
    required this.category,
    this.weight = 0,
    this.description,
    this.quantity = 1,
  });

  factory Item.fromJson(Map<String, dynamic> json) {
    return Item(
      id: json['id'].toString(),
      characterId: json['character_id'].toString(),
      name: json['name'] as String? ?? '',
      category: json['category'] as String? ?? 'equipamento',
      weight: (json['weight'] as num?)?.toDouble() ?? 0.0,
      description: json['description'] as String?,
      quantity: (json['quantity'] as num?)?.toInt() ?? 1,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'category': category,
      'weight': weight,
      'quantity': quantity,
      if (description != null) 'description': description,
    };
  }
}
