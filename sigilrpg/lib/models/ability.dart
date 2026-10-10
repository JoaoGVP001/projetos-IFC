class Ability {
  final String id;
  final String name;
  final String description;
  final int costPE; // custo em Pontos de Esforço (se aplicável)

  const Ability({
    required this.id,
    required this.name,
    required this.description,
    this.costPE = 0,
  });
}
