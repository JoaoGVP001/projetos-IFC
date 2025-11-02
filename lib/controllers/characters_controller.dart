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
    // Carregar todos os personagens do usuário autenticado
    try {
      final charactersList = await _service.getUserCharacters();
      _characters
        ..clear()
        ..addAll(charactersList);
      notifyListeners();
    } catch (e) {
      // Se não houver personagens ou erro, apenas limpar lista
      _characters.clear();
      notifyListeners();
      // Não relançar o erro para não quebrar o login
    }
  }

  void add(Character c) {
    _characters.add(c);
    notifyListeners();
  }

  void removeById(String id) {
    _characters.removeWhere((c) => c.id == id);
    notifyListeners();
  }

  void updateById(String id, Character updated) {
    final index = _characters.indexWhere((c) => c.id == id);
    if (index != -1) {
      _characters[index] = updated;
      notifyListeners();
    }
  }
}
