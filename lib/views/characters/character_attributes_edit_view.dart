import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/models/character.dart';
import 'package:sigilrpg/services/characters_service.dart';
import 'package:sigilrpg/controllers/characters_controller.dart';

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

  late final TextEditingController _agiController;
  late final TextEditingController _intController;
  late final TextEditingController _vigController;
  late final TextEditingController _preController;
  late final TextEditingController _forController;

  @override
  void initState() {
    super.initState();
    _agiController = TextEditingController(text: _agi.toString());
    _intController = TextEditingController(text: _int.toString());
    _vigController = TextEditingController(text: _vig.toString());
    _preController = TextEditingController(text: _pre.toString());
    _forController = TextEditingController(text: _for.toString());
    _load();
  }

  @override
  void dispose() {
    _agiController.dispose();
    _intController.dispose();
    _vigController.dispose();
    _preController.dispose();
    _forController.dispose();
    super.dispose();
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
        _agiController.text = _agi.toString();
        _intController.text = _int.toString();
        _vigController.text = _vig.toString();
        _preController.text = _pre.toString();
        _forController.text = _for.toString();
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
          : SingleChildScrollView(
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
                  DropdownButtonFormField<int>(
                    value: _nex,
                    decoration: const InputDecoration(
                      labelText: 'NEX (%)',
                      border: OutlineInputBorder(),
                    ),
                    items: [
                      // Valores de 5 em 5 até 95
                      ...List.generate(19, (index) {
                        final value = 5 + (index * 5);
                        return DropdownMenuItem<int>(
                          value: value,
                          child: Text('$value%'),
                        );
                      }),
                      // Valores especiais: 99 e 100
                      const DropdownMenuItem<int>(value: 99, child: Text('99%')),
                      const DropdownMenuItem<int>(value: 100, child: Text('100%')),
                    ],
                    onChanged: (v) {
                      if (v != null) setState(() => _nex = v);
                    },
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'Atributos',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 8),
                  _attrRow('AGI', _agiController, (v) => setState(() => _agi = v)),
                  _attrRow('INT', _intController, (v) => setState(() => _int = v)),
                  _attrRow('VIG', _vigController, (v) => setState(() => _vig = v)),
                  _attrRow('PRE', _preController, (v) => setState(() => _pre = v)),
                  _attrRow('FOR', _forController, (v) => setState(() => _for = v)),
                  const SizedBox(height: 24),
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

  Widget _attrRow(String label, TextEditingController controller, ValueChanged<int> onChanged) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          SizedBox(width: 48, child: Text(label, style: const TextStyle(fontWeight: FontWeight.w500))),
          Expanded(
            child: TextField(
              controller: controller,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'Valor',
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 16),
              ),
              onChanged: (text) {
                final parsed = int.tryParse(text);
                if (parsed != null && parsed >= 0) {
                  onChanged(parsed);
                }
              },
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      // Ler valores dos controllers para garantir que salvamos o que o usuário digitou
      final agi = int.tryParse(_agiController.text) ?? _agi;
      final intel = int.tryParse(_intController.text) ?? _int;
      final vig = int.tryParse(_vigController.text) ?? _vig;
      final pre = int.tryParse(_preController.text) ?? _pre;
      final forca = int.tryParse(_forController.text) ?? _for;
      
      // Tentar atualizar como personagem do usuário primeiro
      Character updated;
      try {
        updated = await _service.updateUserCharacter(widget.characterId, {
          'nex': _nex,
          'agilidade': agi >= 0 ? agi : _agi,
          'intelecto': intel >= 0 ? intel : _int,
          'vigor': vig >= 0 ? vig : _vig,
          'presenca': pre >= 0 ? pre : _pre,
          'forca': forca >= 0 ? forca : _for,
        });
      } catch (e) {
        // Se falhar, tentar endpoint de personagens do sistema
        updated = await _service.updateCharacter(widget.characterId, {
          'nex': _nex,
          'agilidade': agi >= 0 ? agi : _agi,
          'intelecto': intel >= 0 ? intel : _int,
          'vigor': vig >= 0 ? vig : _vig,
          'presenca': pre >= 0 ? pre : _pre,
          'forca': forca >= 0 ? forca : _for,
        });
      }
      if (!mounted) return;
      
      // Atualizar o controller para que a lista seja atualizada
      try {
        context.read<CharactersController>().updateById(widget.characterId, updated);
      } catch (e) {
        // Se não conseguir acessar o controller, não é problema crítico
      }
      
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
