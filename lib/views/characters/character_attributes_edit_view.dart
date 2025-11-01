import 'package:flutter/material.dart';
import 'package:sigilrpg/models/character.dart';
import 'package:sigilrpg/services/characters_service.dart';

class CharacterAttributesEditView extends StatefulWidget {
  const CharacterAttributesEditView({super.key, required this.characterId});
  final String characterId;

  @override
  State<CharacterAttributesEditView> createState() =>
      _CharacterAttributesEditViewState();
}

class _CharacterAttributesEditViewState
    extends State<CharacterAttributesEditView> {
  final _service = CharactersService();
  bool _loading = true;
  bool _saving = false;

  int _agi = 1, _int = 1, _vig = 1, _pre = 1, _for = 1;
  int _nex = 5;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final c = await _service.fetchCharacter(widget.characterId);
      setState(() {
        _agi = c.attributes.agilidade;
        _int = c.attributes.intelecto;
        _vig = c.attributes.vigor;
        _pre = c.attributes.presenca;
        _for = c.attributes.forca;
        _nex = c.nex;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _loading = false);
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Erro ao carregar: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Editar NEX e Atributos')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'NEX (Nível de Exposição)',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: Slider(
                          min: 5,
                          max: 99,
                          divisions: 94,
                          label: '$_nex%',
                          value: _nex.toDouble(),
                          onChanged: (v) => setState(() => _nex = v.round()),
                        ),
                      ),
                      SizedBox(
                        width: 60,
                        child: Text('$_nex%', textAlign: TextAlign.end),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'Atributos',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 8),
                  _attrRow('AGI', _agi, (v) => setState(() => _agi = v)),
                  _attrRow('INT', _int, (v) => setState(() => _int = v)),
                  _attrRow('VIG', _vig, (v) => setState(() => _vig = v)),
                  _attrRow('PRE', _pre, (v) => setState(() => _pre = v)),
                  _attrRow('FOR', _for, (v) => setState(() => _for = v)),
                  const Spacer(),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: _saving
                              ? null
                              : () => Navigator.pop(context),
                          child: const Text('Cancelar'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: _saving ? null : _save,
                          child: _saving
                              ? const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                  ),
                                )
                              : const Text('Salvar'),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
    );
  }

  Widget _attrRow(String label, int value, ValueChanged<int> onChanged) {
    return Row(
      children: [
        SizedBox(width: 48, child: Text(label)),
        Expanded(
          child: Slider(
            min: 0,
            max: 3,
            divisions: 3,
            label: '$value',
            value: value.toDouble(),
            onChanged: (v) => onChanged(v.round()),
          ),
        ),
        SizedBox(width: 32, child: Text('$value', textAlign: TextAlign.end)),
      ],
    );
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      // Tentar atualizar como personagem do usuário primeiro
      Character updated;
      try {
        updated = await _service.updateUserCharacter(widget.characterId, {
          'nex': _nex,
          'agilidade': _agi,
          'intelecto': _int,
          'vigor': _vig,
          'presenca': _pre,
          'forca': _for,
        });
      } catch (e) {
        // Se falhar, tentar endpoint de personagens do sistema
        updated = await _service.updateCharacter(widget.characterId, {
          'nex': _nex,
          'agilidade': _agi,
          'intelecto': _int,
          'vigor': _vig,
          'presenca': _pre,
          'forca': _for,
        });
      }
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Atributos e NEX atualizados.')));
      Navigator.pop(context, updated);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Erro ao salvar: $e')));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }
}
