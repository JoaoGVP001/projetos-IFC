import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/constants/app_colors.dart';
import 'package:sigilrpg/controllers/characters_controller.dart';
import 'package:sigilrpg/models/character.dart';
import 'package:sigilrpg/models/character_class.dart';
import 'package:sigilrpg/models/character_origin.dart';
import 'package:sigilrpg/services/characters_service.dart';

class CharacterEditView extends StatefulWidget {
  final Character character;
  const CharacterEditView({super.key, required this.character});

  @override
  State<CharacterEditView> createState() => _CharacterEditViewState();
}

class _CharacterEditViewState extends State<CharacterEditView> {
  final _service = CharactersService();
  final _formKey = GlobalKey<FormState>();
  bool _saving = false;

  // Controllers
  late TextEditingController _nameCtrl;
  late TextEditingController _playerNameCtrl;
  late TextEditingController _ageCtrl;
  late TextEditingController _avatarUrlCtrl;
  late TextEditingController _genderCtrl;
  late TextEditingController _appearanceCtrl;
  late TextEditingController _personalityCtrl;
  late TextEditingController _backgroundCtrl;
  late TextEditingController _objectiveCtrl;
  late TextEditingController _agiCtrl;
  late TextEditingController _intCtrl;
  late TextEditingController _vigCtrl;
  late TextEditingController _preCtrl;
  late TextEditingController _forCtrl;

  // Values
  int _nex = 5;
  int _agilidade = 1;
  int _intelecto = 1;
  int _vigor = 1;
  int _presenca = 1;
  int _forca = 1;
  String _skilledIn = 'Combat';
  String? _origin;
  String? _characterClass;

  final List<String> _skilledInOptions = [
    'Combat',
    'Tiroteio',
    'Pontaria',
    'Acrobacia',
    'Adestramento',
    'Artes',
    'Atletismo',
    'Atualidades',
    'Ciências',
    'Crime',
    'Diplomacia',
    'Enganação',
    'Fortitude',
    'Furtividade',
    'Iniciativa',
    'Intimidação',
    'Intuição',
    'Investigação',
    'Luta',
    'Medicina',
    'Ocultismo',
    'Percepção',
    'Pilotagem',
    'Pontaria',
    'Profissão',
    'Reflexos',
    'Religião',
    'Sobrevivência',
    'Tática',
    'Tecnologia',
    'Vontade',
  ];

  @override
  void initState() {
    super.initState();
    final c = widget.character;
    _nameCtrl = TextEditingController(text: c.name);
    _playerNameCtrl = TextEditingController(text: c.playerName);
    _ageCtrl = TextEditingController(text: c.details.age?.toString() ?? '');
    _avatarUrlCtrl = TextEditingController(text: c.avatarUrl ?? '');
    _genderCtrl = TextEditingController(text: c.details.gender ?? '');
    _appearanceCtrl = TextEditingController(text: c.details.appearance ?? '');
    _personalityCtrl = TextEditingController(text: c.details.personality ?? '');
    _backgroundCtrl = TextEditingController(text: c.details.background ?? '');
    _objectiveCtrl = TextEditingController(text: c.details.objective ?? '');

    _nex = c.nex;
    _agilidade = c.attributes.agilidade;
    _intelecto = c.attributes.intelecto;
    _vigor = c.attributes.vigor;
    _presenca = c.attributes.presenca;
    _forca = c.attributes.forca;
    _skilledIn = c.skilledIn;
    _origin = c.origin.isEmpty ? null : c.origin;
    _characterClass = c.characterClass.isEmpty ? null : c.characterClass;

    _agiCtrl = TextEditingController(text: _agilidade.toString());
    _intCtrl = TextEditingController(text: _intelecto.toString());
    _vigCtrl = TextEditingController(text: _vigor.toString());
    _preCtrl = TextEditingController(text: _presenca.toString());
    _forCtrl = TextEditingController(text: _forca.toString());
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _playerNameCtrl.dispose();
    _ageCtrl.dispose();
    _avatarUrlCtrl.dispose();
    _genderCtrl.dispose();
    _appearanceCtrl.dispose();
    _personalityCtrl.dispose();
    _backgroundCtrl.dispose();
    _objectiveCtrl.dispose();
    _agiCtrl.dispose();
    _intCtrl.dispose();
    _vigCtrl.dispose();
    _preCtrl.dispose();
    _forCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _saving = true);
    try {
      final updates = <String, dynamic>{
        'name': _nameCtrl.text.trim(),
        'player_name': _playerNameCtrl.text.trim(),
        'age': int.tryParse(_ageCtrl.text.trim()) ?? 0,
        'nex': _nex,
        'avatar_url': _avatarUrlCtrl.text.trim().isEmpty ? null : _avatarUrlCtrl.text.trim(),
        'skilled_in': _skilledIn,
        'agilidade': _agilidade,
        'intelecto': _intelecto,
        'vigor': _vigor,
        'presenca': _presenca,
        'forca': _forca,
        'gender': _genderCtrl.text.trim().isEmpty ? null : _genderCtrl.text.trim(),
        'appearance': _appearanceCtrl.text.trim().isEmpty ? null : _appearanceCtrl.text.trim(),
        'personality': _personalityCtrl.text.trim().isEmpty ? null : _personalityCtrl.text.trim(),
        'background': _backgroundCtrl.text.trim().isEmpty ? null : _backgroundCtrl.text.trim(),
        'objective': _objectiveCtrl.text.trim().isEmpty ? null : _objectiveCtrl.text.trim(),
      };

      if (_origin != null) updates['origin'] = _origin;
      if (_characterClass != null) updates['character_class'] = _characterClass;

      Character updated;
      try {
        updated = await _service.updateUserCharacter(widget.character.id, updates);
      } catch (e) {
        updated = await _service.updateCharacter(widget.character.id, updates);
      }

      // Atualizar lista
      if (context.mounted) {
        await context.read<CharactersController>().load();
      }

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Personagem atualizado com sucesso!')),
      );
      Navigator.pop(context, updated);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao salvar: $e')),
      );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Editar Personagem'),
      ),
      body: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Informações Básicas
                    _buildSectionTitle('Informações Básicas'),
                    TextFormField(
                      controller: _nameCtrl,
                      decoration: const InputDecoration(labelText: 'Nome do Personagem *'),
                      validator: (v) => (v == null || v.trim().isEmpty) ? 'Campo obrigatório' : null,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _playerNameCtrl,
                      decoration: const InputDecoration(labelText: 'Jogador Responsável *'),
                      validator: (v) => (v == null || v.trim().isEmpty) ? 'Campo obrigatório' : null,
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: _ageCtrl,
                            decoration: const InputDecoration(labelText: 'Idade'),
                            keyboardType: TextInputType.number,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: DropdownButtonFormField<String>(
                            value: _skilledIn,
                            decoration: const InputDecoration(labelText: 'Especializado em'),
                            items: _skilledInOptions.map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
                            onChanged: (v) => setState(() => _skilledIn = v ?? 'Combat'),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _avatarUrlCtrl,
                      decoration: const InputDecoration(labelText: 'Avatar URL (opcional)'),
                    ),

                    const SizedBox(height: 24),
                    // Origem e Classe
                    _buildSectionTitle('Origem e Classe'),
                    DropdownButtonFormField<String?>(
                      value: _origin,
                      decoration: const InputDecoration(labelText: 'Origem'),
                      items: [
                        const DropdownMenuItem<String?>(value: null, child: Text('Nenhuma')),
                        ...CharacterOrigins.allOrigins.map((o) => DropdownMenuItem<String?>(value: o.name, child: Text(o.name))),
                      ],
                      onChanged: (v) => setState(() => _origin = v),
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String?>(
                      value: _characterClass,
                      decoration: const InputDecoration(labelText: 'Classe'),
                      items: [
                        const DropdownMenuItem<String?>(value: null, child: Text('Nenhuma')),
                        ...CharacterClasses.allClasses.map((c) => DropdownMenuItem<String?>(value: c.name, child: Text(c.name))),
                      ],
                      onChanged: (v) => setState(() => _characterClass = v),
                    ),

                    const SizedBox(height: 24),
                    // NEX
                    _buildSectionTitle('NEX (Nível de Exposição)'),
                    DropdownButtonFormField<int>(
                      value: _nex,
                      decoration: const InputDecoration(labelText: 'NEX (%)'),
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
                    // Atributos
                    _buildSectionTitle('Atributos'),
                    _attrRow('AGI', _agiCtrl, (v) {
                      setState(() {
                        _agilidade = v;
                        _agiCtrl.text = v.toString();
                      });
                    }),
                    _attrRow('INT', _intCtrl, (v) {
                      setState(() {
                        _intelecto = v;
                        _intCtrl.text = v.toString();
                      });
                    }),
                    _attrRow('VIG', _vigCtrl, (v) {
                      setState(() {
                        _vigor = v;
                        _vigCtrl.text = v.toString();
                      });
                    }),
                    _attrRow('PRE', _preCtrl, (v) {
                      setState(() {
                        _presenca = v;
                        _preCtrl.text = v.toString();
                      });
                    }),
                    _attrRow('FOR', _forCtrl, (v) {
                      setState(() {
                        _forca = v;
                        _forCtrl.text = v.toString();
                      });
                    }),

                    const SizedBox(height: 24),
                    // Detalhes
                    _buildSectionTitle('Detalhes do Personagem'),
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: _genderCtrl,
                            decoration: const InputDecoration(labelText: 'Gênero'),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _appearanceCtrl,
                      decoration: const InputDecoration(labelText: 'Aparência'),
                      maxLines: 3,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _personalityCtrl,
                      decoration: const InputDecoration(labelText: 'Personalidade'),
                      maxLines: 3,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _backgroundCtrl,
                      decoration: const InputDecoration(labelText: 'Histórico'),
                      maxLines: 4,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _objectiveCtrl,
                      decoration: const InputDecoration(labelText: 'Objetivo'),
                      maxLines: 3,
                    ),

                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: _saving ? null : () => Navigator.pop(context),
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
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Salvar'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12, top: 8),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.bold,
              color: AppColors.seed,
            ),
      ),
    );
  }

  Widget _attrRow(String label, TextEditingController controller, ValueChanged<int> onChanged) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          SizedBox(width: 60, child: Text(label, style: Theme.of(context).textTheme.titleMedium)),
          Expanded(
            child: TextFormField(
              controller: controller,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: label,
                border: const OutlineInputBorder(),
              ),
              onChanged: (v) {
                final num = int.tryParse(v);
                if (num != null && num >= 0) {
                  onChanged(num);
                }
              },
            ),
          ),
        ],
      ),
    );
  }
}

