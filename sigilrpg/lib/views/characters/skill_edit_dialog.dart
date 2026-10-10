import 'package:flutter/material.dart';
import 'package:sigilrpg/models/skill.dart';

class SkillEditDialog extends StatefulWidget {
  final Skill? skill;
  const SkillEditDialog({super.key, this.skill});

  @override
  State<SkillEditDialog> createState() => _SkillEditDialogState();
}

class _SkillEditDialogState extends State<SkillEditDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameController;
  late final TextEditingController _descriptionController;
  late String _attribute;
  late int _bonusDice;
  late int _training;
  late int _others;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.skill?.name ?? '');
    _descriptionController = TextEditingController(text: widget.skill?.description ?? '');
    _attribute = widget.skill?.attribute ?? 'AGI';
    _bonusDice = widget.skill?.bonusDice ?? 0;
    _training = widget.skill?.training ?? 0;
    _others = widget.skill?.others ?? 0;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  void _save() {
    if (!_formKey.currentState!.validate()) return;
    
    final skill = Skill(
      id: widget.skill?.id ?? '',
      characterId: widget.skill?.characterId ?? '',
      name: _nameController.text.trim(),
      attribute: _attribute,
      bonusDice: _bonusDice,
      training: _training,
      others: _others,
      description: _descriptionController.text.trim().isEmpty 
          ? null 
          : _descriptionController.text.trim(),
    );
    
    Navigator.pop(context, skill);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.skill == null ? 'Adicionar Habilidade' : 'Editar Habilidade'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Nome da Habilidade',
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
              DropdownButtonFormField<String>(
                value: _attribute,
                decoration: const InputDecoration(
                  labelText: 'Atributo',
                  border: OutlineInputBorder(),
                ),
                items: ['AGI', 'INT', 'VIG', 'PRE', 'FOR']
                    .map((attr) => DropdownMenuItem(value: attr, child: Text(attr)))
                    .toList(),
                onChanged: (value) {
                  if (value != null) setState(() => _attribute = value);
                },
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      initialValue: _bonusDice.toString(),
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Dados Bônus',
                        border: OutlineInputBorder(),
                      ),
                      onChanged: (value) {
                        _bonusDice = int.tryParse(value) ?? 0;
                      },
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextFormField(
                      initialValue: _training.toString(),
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Treino',
                        border: OutlineInputBorder(),
                      ),
                      onChanged: (value) {
                        _training = int.tryParse(value) ?? 0;
                      },
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextFormField(
                      initialValue: _others.toString(),
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Outros',
                        border: OutlineInputBorder(),
                      ),
                      onChanged: (value) {
                        _others = int.tryParse(value) ?? 0;
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

