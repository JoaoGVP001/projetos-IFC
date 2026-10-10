import 'package:flutter/material.dart';
import 'package:sigilrpg/models/skill.dart';
import 'package:sigilrpg/services/skills_service.dart';
import 'package:sigilrpg/views/characters/skill_edit_dialog.dart';

class CharacterSkillsTab extends StatefulWidget {
  final String characterId;
  const CharacterSkillsTab({super.key, required this.characterId});

  @override
  State<CharacterSkillsTab> createState() => _CharacterSkillsTabState();
}

class _CharacterSkillsTabState extends State<CharacterSkillsTab> {
  final _service = SkillsService();
  bool _loading = true;
  List<Skill> _skills = [];

  @override
  void initState() {
    super.initState();
    _loadSkills();
  }

  Future<void> _loadSkills() async {
    setState(() => _loading = true);
    try {
      final skills = await _service.getSkills(widget.characterId);
      if (mounted) {
        setState(() {
          _skills = skills;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _loading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro ao carregar habilidades: $e')),
        );
      }
    }
  }

  Future<void> _addSkill() async {
    final result = await showDialog<Skill>(
      context: context,
      builder: (context) => const SkillEditDialog(),
    );
    if (result != null) {
      try {
        await _service.createSkill(widget.characterId, result);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Habilidade criada com sucesso')),
          );
          _loadSkills();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Erro ao criar habilidade: $e')),
          );
        }
      }
    }
  }

  Future<void> _editSkill(Skill skill) async {
    final result = await showDialog<Skill>(
      context: context,
      builder: (context) => SkillEditDialog(skill: skill),
    );
    if (result != null) {
      try {
        await _service.updateSkill(widget.characterId, skill.id, result.toJson());
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Habilidade atualizada com sucesso')),
          );
          _loadSkills();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Erro ao atualizar habilidade: $e')),
          );
        }
      }
    }
  }

  Future<void> _deleteSkill(Skill skill) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Deletar Habilidade'),
        content: Text('Tem certeza que deseja deletar "${skill.name}"?'),
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
        await _service.deleteSkill(widget.characterId, skill.id);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Habilidade deletada com sucesso')),
          );
          _loadSkills();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Erro ao deletar habilidade: $e')),
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
          : _skills.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.sports_martial_arts, size: 64, color: Colors.grey),
                      const SizedBox(height: 16),
                      Text(
                        'Nenhuma habilidade',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      const Text('Adicione habilidades ao seu personagem'),
                      const SizedBox(height: 24),
                      ElevatedButton.icon(
                        onPressed: _addSkill,
                        icon: const Icon(Icons.add),
                        label: const Text('Adicionar Habilidade'),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadSkills,
                  child: Column(
                    children: [
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Habilidades (${_skills.length})',
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                            ElevatedButton.icon(
                              onPressed: _addSkill,
                              icon: const Icon(Icons.add),
                              label: const Text('Adicionar'),
                            ),
                          ],
                        ),
                      ),
                      Expanded(
                        child: ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          itemCount: _skills.length,
                          itemBuilder: (context, index) {
                            final skill = _skills[index];
                            return Card(
                              margin: const EdgeInsets.only(bottom: 12),
                              child: ListTile(
                                title: Text(skill.name),
                                subtitle: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text('Atributo: ${skill.attribute}'),
                                    if (skill.description != null && skill.description!.isNotEmpty)
                                      Text(
                                        skill.description!,
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    const SizedBox(height: 4),
                                    Row(
                                      children: [
                                        if (skill.bonusDice > 0)
                                          Chip(
                                            label: Text('Dados: +${skill.bonusDice}'),
                                            padding: EdgeInsets.zero,
                                          ),
                                        if (skill.training > 0)
                                          Chip(
                                            label: Text('Treino: ${skill.training}'),
                                            padding: EdgeInsets.zero,
                                          ),
                                        if (skill.others != 0)
                                          Chip(
                                            label: Text('Outros: ${skill.others > 0 ? '+' : ''}${skill.others}'),
                                            padding: EdgeInsets.zero,
                                          ),
                                      ],
                                    ),
                                  ],
                                ),
                                trailing: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    IconButton(
                                      icon: const Icon(Icons.edit),
                                      onPressed: () => _editSkill(skill),
                                    ),
                                    IconButton(
                                      icon: const Icon(Icons.delete),
                                      color: Colors.red,
                                      onPressed: () => _deleteSkill(skill),
                                    ),
                                  ],
                                ),
                                isThreeLine: true,
                              ),
                            );
                          },
                        ),
                      ),
                    ],
                  ),
                ),
      floatingActionButton: _skills.isNotEmpty
          ? FloatingActionButton(
              onPressed: _addSkill,
              child: const Icon(Icons.add),
            )
          : null,
    );
  }
}

