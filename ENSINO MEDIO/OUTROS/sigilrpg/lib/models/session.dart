class Session {
  final String id;
  final String title;
  final DateTime date;
  final String? notes;

  const Session({
    required this.id,
    required this.title,
    required this.date,
    this.notes,
  });
}
