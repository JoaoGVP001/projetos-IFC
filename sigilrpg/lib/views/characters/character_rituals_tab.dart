import 'package:flutter/material.dart';
import 'package:sigilrpg/models/ritual.dart';
import 'package:sigilrpg/services/rituals_service.dart';

class CharacterRitualsTab extends StatefulWidget {
  final String characterId;
  const CharacterRitualsTab({super.key, required this.characterId});

  @override
  State<CharacterRitualsTab> createState() => _CharacterRitualsTabState();
}

class _CharacterRitualsTabState extends State<CharacterRitualsTab> {
  final _service = RitualsService();
  bool _loading = true;
  List<Ritual> _rituals = [];

  @override
  void initState() {
    super.initState();
    _loadRituals();
  }

  Future<void> _loadRituals() async {
    setState(() => _loading = true);
    try {
      final rituals = await _service.getRituals(widget.characterId);
      if (mounted) {
        setState(() {
          _rituals = rituals;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _loading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro ao carregar rituais: $e')),
        );
      }
    }
  }

  Future<void> _addRitual() async {
    final result = await showDialog<Ritual>(
      context: context,
      builder: (context) => _RitualEditDialog(),
    );
    if (result != null) {
      try {
        await _service.createRitual(widget.characterId, result);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Ritual criado com sucesso')),
          );
          _loadRituals();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Erro ao criar ritual: $e')),
          );
        }
      }
    }
  }

  Future<void> _editRitual(Ritual ritual) async {
    final result = await showDialog<Ritual>(
      context: context,
      builder: (context) => _RitualEditDialog(ritual: ritual),
    );
    if (result != null) {
      try {
        await _service.updateRitual(widget.characterId, ritual.id, result.toJson());
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Ritual atualizado com sucesso')),
          );
          _loadRituals();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Erro ao atualizar ritual: $e')),
          );
        }
      }
    }
  }

  Future<void> _deleteRitual(Ritual ritual) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Deletar Ritual'),
        content: Text('Tem certeza que deseja deletar "${ritual.name}"?'),
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

    if (confirmed == true) {
      try {
        await _service.deleteRitual(widget.characterId, ritual.id);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Ritual deletado com sucesso')),
          );
          _loadRituals();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Erro ao deletar ritual: $e')),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _rituals.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.auto_awesome, size: 64, color: Colors.grey),
                      const SizedBox(height: 16),
                      Text(
                        'Nenhum ritual',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      const Text('Adicione rituais ao seu personagem'),
                      const SizedBox(height: 24),
                      ElevatedButton.icon(
                        onPressed: _addRitual,
                        icon: const Icon(Icons.add),
                        label: const Text('Adicionar Ritual'),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadRituals,
                  child: Column(
                    children: [
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Rituais (${_rituals.length})',
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                            ElevatedButton.icon(
                              onPressed: _addRitual,
                              icon: const Icon(Icons.add),
                              label: const Text('Adicionar'),
                            ),
                          ],
                        ),
                      ),
                      Expanded(
                        child: ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          itemCount: _rituals.length,
                          itemBuilder: (context, index) {
                            final ritual = _rituals[index];
                            return Card(
                              margin: const EdgeInsets.only(bottom: 12),
                              child: ExpansionTile(
                                title: Text(ritual.name),
                                subtitle: Text('Círculo ${ritual.circle} • Custo: ${ritual.cost} PE'),
                                trailing: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    IconButton(
                                      icon: const Icon(Icons.edit),
                                      onPressed: () => _editRitual(ritual),
                                    ),
                                    IconButton(
                                      icon: const Icon(Icons.delete),
                                      color: Colors.red,
                                      onPressed: () => _deleteRitual(ritual),
                                    ),
                                  ],
                                ),
                                children: [
                                  Padding(
                                    padding: const EdgeInsets.all(16),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        if (ritual.description != null && ritual.description!.isNotEmpty)
                                          Padding(
                                            padding: const EdgeInsets.only(bottom: 8),
                                            child: Text(
                                              ritual.description!,
                                              style: Theme.of(context).textTheme.bodyMedium,
                                            ),
                                          ),
                                        if (ritual.effect != null && ritual.effect!.isNotEmpty)
                                          Padding(
                                            padding: const EdgeInsets.only(bottom: 8),
                                            child: Text(
                                              'Efeito: ${ritual.effect!}',
                                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                                    fontWeight: FontWeight.bold,
                                                  ),
                                            ),
                                          ),
                                        Wrap(
                                          spacing: 8,
                                          runSpacing: 8,
                                          children: [
                                            if (ritual.executionTime != null)
                                              Chip(
                                                label: Text('Tempo: ${ritual.executionTime}'),
                                                padding: EdgeInsets.zero,
                                              ),
                                            if (ritual.range != null)
                                              Chip(
                                                label: Text('Alcance: ${ritual.range}'),
                                                padding: EdgeInsets.zero,
                                              ),
                                            if (ritual.duration != null)
                                              Chip(
                                                label: Text('Duração: ${ritual.duration}'),
                                                padding: EdgeInsets.zero,
                                              ),
                                            if (ritual.resistanceTest != null)
                                              Chip(
                                                label: Text('Teste: ${ritual.resistanceTest}'),
                                                padding: EdgeInsets.zero,
                                              ),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            );
                          },
                        ),
                      ),
                    ],
                  ),
                ),
      floatingActionButton: _rituals.isNotEmpty
          ? FloatingActionButton(
              onPressed: _addRitual,
              child: const Icon(Icons.add),
            )
          : null,
    );
  }
}

class _RitualEditDialog extends StatefulWidget {
  final Ritual? ritual;
  const _RitualEditDialog({this.ritual});

  @override
  State<_RitualEditDialog> createState() => _RitualEditDialogState();
}

class _RitualEditDialogState extends State<_RitualEditDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameController;
  late final TextEditingController _descriptionController;
  late final TextEditingController _effectController;
  late final TextEditingController _executionTimeController;
  late final TextEditingController _rangeController;
  late final TextEditingController _durationController;
  late final TextEditingController _resistanceTestController;
  late int _circle;
  late int _cost;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.ritual?.name ?? '');
    _descriptionController = TextEditingController(text: widget.ritual?.description ?? '');
    _effectController = TextEditingController(text: widget.ritual?.effect ?? '');
    _executionTimeController = TextEditingController(text: widget.ritual?.executionTime ?? '');
    _rangeController = TextEditingController(text: widget.ritual?.range ?? '');
    _durationController = TextEditingController(text: widget.ritual?.duration ?? '');
    _resistanceTestController = TextEditingController(text: widget.ritual?.resistanceTest ?? '');
    _circle = widget.ritual?.circle ?? 1;
    _cost = widget.ritual?.cost ?? 0;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _effectController.dispose();
    _executionTimeController.dispose();
    _rangeController.dispose();
    _durationController.dispose();
    _resistanceTestController.dispose();
    super.dispose();
  }

  void _save() {
    if (!_formKey.currentState!.validate()) return;
    
    final ritual = Ritual(
      id: widget.ritual?.id ?? '',
      characterId: widget.ritual?.characterId ?? '',
      name: _nameController.text.trim(),
      circle: _circle,
      cost: _cost,
      executionTime: _executionTimeController.text.trim().isEmpty 
          ? null 
          : _executionTimeController.text.trim(),
      range: _rangeController.text.trim().isEmpty 
          ? null 
          : _rangeController.text.trim(),
      duration: _durationController.text.trim().isEmpty 
          ? null 
          : _durationController.text.trim(),
      resistanceTest: _resistanceTestController.text.trim().isEmpty 
          ? null 
          : _resistanceTestController.text.trim(),
      description: _descriptionController.text.trim().isEmpty 
          ? null 
          : _descriptionController.text.trim(),
      effect: _effectController.text.trim().isEmpty 
          ? null 
          : _effectController.text.trim(),
    );
    
    Navigator.pop(context, ritual);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.ritual == null ? 'Adicionar Ritual' : 'Editar Ritual'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Nome do Ritual',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Nome é obrigatório';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<int>(
                      value: _circle,
                      decoration: const InputDecoration(
                        labelText: 'Círculo',
                        border: OutlineInputBorder(),
                      ),
                      items: List.generate(10, (index) => index + 1)
                          .map((circle) => DropdownMenuItem(
                                value: circle,
                                child: Text('Círculo $circle'),
                              ))
                          .toList(),
                      onChanged: (value) {
                        if (value != null) setState(() => _circle = value);
                      },
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextFormField(
                      initialValue: _cost.toString(),
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Custo (PE)',
                        border: OutlineInputBorder(),
                      ),
                      onChanged: (value) {
                        _cost = int.tryParse(value) ?? 0;
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Descrição (opcional)',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _effectController,
                decoration: const InputDecoration(
                  labelText: 'Efeito (opcional)',
                  border: OutlineInputBorder(),
                ),
                maxLines: 2,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _executionTimeController,
                decoration: const InputDecoration(
                  labelText: 'Tempo de Execução (opcional)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _rangeController,
                decoration: const InputDecoration(
                  labelText: 'Alcance (opcional)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _durationController,
                decoration: const InputDecoration(
                  labelText: 'Duração (opcional)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _resistanceTestController,
                decoration: const InputDecoration(
                  labelText: 'Teste de Resistência (opcional)',
                  border: OutlineInputBorder(),
                ),
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancelar'),
        ),
        ElevatedButton(
          onPressed: _save,
          child: const Text('Salvar'),
        ),
      ],
    );
  }
}

