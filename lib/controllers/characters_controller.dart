import 'package:flutter/foundation.dart';
import 'package:sigilrpg/models/character.dart';
import 'package:sigilrpg/services/characters_service.dart';

class CharactersController extends ChangeNotifier {
  CharactersController({CharactersService? service})
    : _service = service ?? CharactersService();

  final CharactersService _service;
  final List<Character> _characters = <Character>[];

  List<Character> get characters => List.unmodifiable(_characters);

  Future<void> load() async {
    // Carregar personagem do usuário autenticado
    final me = await _service.getUserCharacter();
    _characters
      ..clear()
      ..add(me);
    notifyListeners();
  }

  void add(Character c) {
    _characters.add(c);
    notifyListeners();
  }

  void removeById(String id) {
    _characters.removeWhere((c) => c.id == id);
    notifyListeners();
  }
}
