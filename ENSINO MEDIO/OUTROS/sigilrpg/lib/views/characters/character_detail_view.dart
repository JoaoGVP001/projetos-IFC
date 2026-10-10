import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/constants/app_colors.dart';
import 'package:sigilrpg/constants/app_routes.dart';
import 'package:sigilrpg/controllers/characters_controller.dart';
import 'package:sigilrpg/models/character.dart';
import 'package:sigilrpg/services/characters_service.dart';
import 'package:sigilrpg/views/characters/character_edit_view.dart';
import 'package:sigilrpg/views/characters/character_skills_tab.dart';
import 'package:sigilrpg/views/characters/character_rituals_tab.dart';
import 'package:sigilrpg/views/characters/character_items_tab.dart';
import 'package:sigilrpg/views/characters/character_description_tab.dart';
import 'package:sigilrpg/widgets/attribute_circle.dart';
import 'package:sigilrpg/utils/combat.dart';

class CharacterDetailView extends StatefulWidget {
  final Character character;
  const CharacterDetailView({super.key, required this.character});

  @override
  State<CharacterDetailView> createState() => _CharacterDetailViewState();
}

class _CharacterDetailViewState extends State<CharacterDetailView> {
  late Character _character;
  final _service = CharactersService();
  bool _hasInitialized = false;
  DateTime? _lastReload;

  @override
  void initState() {
    super.initState();
    _character = widget.character;
    _hasInitialized = true;
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Recarregar personagem quando voltar para esta tela (evitar recarregar muito rápido)
    final now = DateTime.now();
    if (_hasInitialized && 
        ModalRoute.of(context)?.isCurrent == true &&
        (_lastReload == null || now.difference(_lastReload!).inSeconds > 1)) {
      _lastReload = now;
      _reloadCharacter();
    }
  }

  Future<void> _reloadCharacter() async {
    try {
      final updated = await _service.fetchCharacter(_character.id);
      if (mounted) {
        setState(() {
          _character = updated;
        });
      }
    } catch (e) {
      // Se falhar, manter os dados atuais
    }
  }

  Future<void> _editNex() async {
    final currentNex = _character.nex;
    final result = await showDialog<int>(
      context: context,
      builder: (context) => _NexEditDialog(currentNex: currentNex),
    );

    if (result != null && result != currentNex) {
      try {
        Character updated;
        try {
          updated = await _service.updateUserCharacter(_character.id, {
            'nex': result,
          });
        } catch (e) {
          updated = await _service.updateCharacter(_character.id, {
            'nex': result,
          });
        }
        setState(() {
          _character = updated;
        });
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('NEX atualizado')),
        );
      } catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro ao atualizar NEX: $e')),
        );
      }
    }
  }

  Future<void> _updateCombatStat(String statName, int newValue) async {
    try {
      Character updated;
      try {
        updated = await _service.updateUserCharacter(_character.id, {
          statName: newValue,
        });
      } catch (e) {
        updated = await _service.updateCharacter(_character.id, {
          statName: newValue,
        });
      }
      setState(() {
        _character = updated;
      });
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Valor atualizado')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao atualizar: $e')),
      );
    }
  }

  Future<void> _editAttribute(String attrName, int currentValue) async {
    final result = await showDialog<int>(
      context: context,
      builder: (context) => _AttributeEditDialog(
        attrName: attrName,
        currentValue: currentValue,
      ),
    );

    if (result != null && result != currentValue) {
      try {
        final updateMap = <String, dynamic>{};
        switch (attrName) {
          case 'AGI':
            updateMap['agilidade'] = result;
            break;
          case 'INT':
            updateMap['intelecto'] = result;
            break;
          case 'VIG':
            updateMap['vigor'] = result;
            break;
          case 'PRE':
            updateMap['presenca'] = result;
            break;
          case 'FOR':
            updateMap['forca'] = result;
            break;
        }

        Character updated;
        try {
          updated = await _service.updateUserCharacter(_character.id, updateMap);
        } catch (e) {
          updated = await _service.updateCharacter(_character.id, updateMap);
        }
        setState(() {
          _character = updated;
        });
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Atributo atualizado')),
        );
      } catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro ao atualizar atributo: $e')),
        );
      }
    }
  }

  Future<void> _confirmDelete() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Deletar Personagem'),
        content: Text('Tem certeza que deseja deletar ${_character.name}? Esta ação não pode ser desfeita.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Deletar'),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      try {
        try {
          await _service.deleteUserCharacter(_character.id);
        } catch (e) {
          // Se falhar, pode tentar endpoint de sistema
          throw e;
        }

        // Remover da lista
        if (mounted) {
          context.read<CharactersController>().removeById(_character.id);
        }

        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Personagem deletado com sucesso')),
        );

        // Voltar para lista de personagens
        Navigator.of(context).popUntil((route) => 
          route.isFirst || route.settings.name == AppRoutes.characters
        );

        if (mounted && Navigator.canPop(context)) {
          Navigator.pushReplacementNamed(context, AppRoutes.characters);
        } else if (mounted) {
          Navigator.popUntil(context, (route) => route.isFirst);
          Navigator.pushNamed(context, AppRoutes.characters);
        }
      } catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro ao deletar personagem: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 5,
      child: Scaffold(
        appBar: AppBar(
          title: Text(_character.name),
          actions: [
            IconButton(
              icon: const Icon(Icons.edit),
              tooltip: 'Editar Personagem Completo',
              onPressed: () async {
                final result = await Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => CharacterEditView(character: _character),
                  ),
                );
                if (result != null && result is Character) {
                  setState(() {
                    _character = result;
                  });
                }
              },
            ),
            IconButton(
              icon: const Icon(Icons.delete),
              tooltip: 'Deletar Personagem',
              onPressed: _confirmDelete,
            ),
          ],
          bottom: const TabBar(
            isScrollable: true,
            tabs: [
              Tab(text: 'Combate'),
              Tab(text: 'Habilidades'),
              Tab(text: 'Rituais'),
              Tab(text: 'Inventário'),
              Tab(text: 'Descrição'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _CombatTab(
              character: _character,
              onEditNex: _editNex,
              onEditAttribute: _editAttribute,
              onUpdateCombatStat: _updateCombatStat,
            ),
            CharacterSkillsTab(characterId: _character.id),
            CharacterRitualsTab(characterId: _character.id),
            CharacterItemsTab(characterId: _character.id),
            CharacterDescriptionTab(character: _character),
          ],
        ),
      ),
    );
  }
}

class _CombatTab extends StatelessWidget {
  final Character character;
  final VoidCallback onEditNex;
  final Function(String, int) onEditAttribute;
  final Function(String, int) onUpdateCombatStat;
  const _CombatTab({
    required this.character,
    required this.onEditNex,
    required this.onEditAttribute,
    required this.onUpdateCombatStat,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              AttributeCircle(
                label: 'AGI',
                value: character.attributes.agilidade,
                onTap: () => onEditAttribute('AGI', character.attributes.agilidade),
              ),
              AttributeCircle(
                label: 'INT',
                value: character.attributes.intelecto,
                onTap: () => onEditAttribute('INT', character.attributes.intelecto),
              ),
              AttributeCircle(
                label: 'VIG',
                value: character.attributes.vigor,
                onTap: () => onEditAttribute('VIG', character.attributes.vigor),
              ),
              AttributeCircle(
                label: 'PRE',
                value: character.attributes.presenca,
                onTap: () => onEditAttribute('PRE', character.attributes.presenca),
              ),
              AttributeCircle(
                label: 'FOR',
                value: character.attributes.forca,
                onTap: () => onEditAttribute('FOR', character.attributes.forca),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _EditableHealthBar(
                  label: 'PV',
                  character: character,
                  current: CombatCalculator.getCurrentPV(character),
                  max: CombatCalculator.calculateMaxPV(character),
                  color: AppColors.success,
                  onUpdate: (newValue) => onUpdateCombatStat('current_pv', newValue),
                ),
                const SizedBox(height: 12),
                _EditableHealthBar(
                  label: 'PE',
                  character: character,
                  current: CombatCalculator.getCurrentPE(character),
                  max: CombatCalculator.calculateMaxPE(character),
                  color: Colors.blueAccent,
                  onUpdate: (newValue) => onUpdateCombatStat('current_pe', newValue),
                ),
                const SizedBox(height: 12),
                _EditableHealthBar(
                  label: 'PS',
                  character: character,
                  current: CombatCalculator.getCurrentPS(character),
                  max: CombatCalculator.calculateMaxPS(character),
                  color: Colors.purpleAccent,
                  onUpdate: (newValue) => onUpdateCombatStat('current_ps', newValue),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                InkWell(
                  onTap: onEditNex,
                  borderRadius: BorderRadius.circular(8),
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
                    decoration: BoxDecoration(
                      border: Border.all(color: AppColors.seed.withOpacity(0.3)),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'NEX: ${character.nex}%',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: AppColors.seed,
                              ),
                        ),
                        Icon(Icons.edit, size: 18, color: AppColors.seed),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  'Defesa: ${CombatCalculator.calculateDefense(character)}',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                Text(
                  'Resistências: Física ${CombatCalculator.resistanceFisica(character)}, '
                  'Balística ${CombatCalculator.resistanceBalistica(character)}, '
                  'Mental ${CombatCalculator.resistanceMental(character)}',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _NexEditDialog extends StatefulWidget {
  final int currentNex;
  const _NexEditDialog({required this.currentNex});

  @override
  State<_NexEditDialog> createState() => _NexEditDialogState();
}

class _NexEditDialogState extends State<_NexEditDialog> {
  late int _nex;

  @override
  void initState() {
    super.initState();
    _nex = widget.currentNex;
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Editar NEX'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            '$_nex%',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppColors.seed,
                ),
          ),
          const SizedBox(height: 16),
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
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancelar'),
        ),
        TextButton(
          onPressed: () => Navigator.pop(context, _nex),
          child: const Text('Salvar'),
        ),
      ],
    );
  }
}

class _AttributeEditDialog extends StatefulWidget {
  final String attrName;
  final int currentValue;
  const _AttributeEditDialog({
    required this.attrName,
    required this.currentValue,
  });

  @override
  State<_AttributeEditDialog> createState() => _AttributeEditDialogState();
}

class _AttributeEditDialogState extends State<_AttributeEditDialog> {
  late int _value;

  @override
  void initState() {
    super.initState();
    _value = widget.currentValue;
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Editar ${widget.attrName}'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            '$_value',
            style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 16),
          TextFormField(
            initialValue: _value.toString(),
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(
              labelText: 'Valor',
              border: OutlineInputBorder(),
            ),
            onChanged: (v) {
              final num = int.tryParse(v);
              if (num != null && num >= 0) {
                setState(() => _value = num);
              }
            },
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancelar'),
        ),
        TextButton(
          onPressed: () => Navigator.pop(context, _value),
          child: const Text('Salvar'),
        ),
      ],
    );
  }
}

// Widget editável para barras de vida
class _EditableHealthBar extends StatelessWidget {
  final String label;
  final Character character;
  final int current;
  final int max;
  final Color color;
  final Function(int) onUpdate;

  const _EditableHealthBar({
    required this.label,
    required this.character,
    required this.current,
    required this.max,
    required this.color,
    required this.onUpdate,
  });

  Future<void> _showEditDialog(BuildContext context) async {
    final result = await showDialog<int>(
      context: context,
      builder: (context) => _CombatStatEditDialog(
        label: label,
        currentValue: current,
        maxValue: max,
      ),
    );

    if (result != null && result != current) {
      onUpdate(result);
    }
  }

  @override
  Widget build(BuildContext context) {
    final double pct = max > 0 ? (current.clamp(0, max) / max) : 0;
    return InkWell(
      onTap: () => _showEditDialog(context),
      borderRadius: BorderRadius.circular(8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Text(label, style: Theme.of(context).textTheme.labelLarge),
                  const SizedBox(width: 8),
                  Icon(Icons.edit, size: 16, color: Colors.grey[600]),
                ],
              ),
              Text('$current / $max'),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: pct,
              minHeight: 10,
              backgroundColor: Colors.white10,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

// Dialog para editar valores de combate
class _CombatStatEditDialog extends StatefulWidget {
  final String label;
  final int currentValue;
  final int maxValue;

  const _CombatStatEditDialog({
    required this.label,
    required this.currentValue,
    required this.maxValue,
  });

  @override
  State<_CombatStatEditDialog> createState() => _CombatStatEditDialogState();
}

class _CombatStatEditDialogState extends State<_CombatStatEditDialog> {
  late int _value;
  final _controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    _value = widget.currentValue;
    _controller.text = _value.toString();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _adjustValue(int delta) {
    setState(() {
      _value = (_value + delta).clamp(0, widget.maxValue);
      _controller.text = _value.toString();
    });
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Editar ${widget.label}'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            'Máximo: ${widget.maxValue}',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                onPressed: () => _adjustValue(-5),
                icon: const Icon(Icons.remove_circle_outline),
                iconSize: 32,
              ),
              const SizedBox(width: 16),
              SizedBox(
                width: 80,
                child: TextField(
                  controller: _controller,
                  textAlign: TextAlign.center,
                  keyboardType: TextInputType.number,
                  style: Theme.of(context).textTheme.headlineMedium,
                  decoration: const InputDecoration(
                    border: OutlineInputBorder(),
                  ),
                  onChanged: (v) {
                    final num = int.tryParse(v);
                    if (num != null) {
                      setState(() {
                        _value = num.clamp(0, widget.maxValue);
                      });
                    }
                  },
                ),
              ),
              const SizedBox(width: 16),
              IconButton(
                onPressed: () => _adjustValue(5),
                icon: const Icon(Icons.add_circle_outline),
                iconSize: 32,
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              TextButton(
                onPressed: () => _adjustValue(-1),
                child: const Text('-1'),
              ),
              const SizedBox(width: 8),
              TextButton(
                onPressed: () => _adjustValue(1),
                child: const Text('+1'),
              ),
            ],
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancelar'),
        ),
        TextButton(
          onPressed: () => Navigator.pop(context, _value),
          child: const Text('Salvar'),
        ),
      ],
    );
  }
}
