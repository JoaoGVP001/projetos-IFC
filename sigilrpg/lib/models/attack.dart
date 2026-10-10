class Attack {
  final String id;
  final String name;
  final String damage; // ex: "1d8+2"
  final String critical; // ex: "19-20/x2"

  const Attack({
    required this.id,
    required this.name,
    required this.damage,
    required this.critical,
  });
}
