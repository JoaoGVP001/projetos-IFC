import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/constants/app_routes.dart';
import 'package:sigilrpg/controllers/character_draft_controller.dart';
import 'package:sigilrpg/controllers/characters_controller.dart';

class CharacterCreateDetailsView extends StatefulWidget {
  const CharacterCreateDetailsView({super.key});

  @override
  State<CharacterCreateDetailsView> createState() =>
      _CharacterCreateDetailsViewState();
}

class _CharacterCreateDetailsViewState
    extends State<CharacterCreateDetailsView> {
  final _formKey = GlobalKey<FormState>();
  final _genderCtrl = TextEditingController();
  final _ageCtrl = TextEditingController();
  final _appearanceCtrl = TextEditingController();
  final _personalityCtrl = TextEditingController();
  final _backgroundCtrl = TextEditingController();
  final _objectiveCtrl = TextEditingController();
  bool _submitting = false;

  @override
  void dispose() {
    _genderCtrl.dispose();
    _ageCtrl.dispose();
    _appearanceCtrl.dispose();
    _personalityCtrl.dispose();
    _backgroundCtrl.dispose();
    _objectiveCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final draft = context.watch<CharacterDraftController>();
    _genderCtrl.text = draft.gender ?? '';
    _ageCtrl.text = draft.age?.toString() ?? '';
    _appearanceCtrl.text = draft.appearance ?? '';
    _personalityCtrl.text = draft.personality ?? '';
    _backgroundCtrl.text = draft.background ?? '';
    _objectiveCtrl.text = draft.objective ?? '';

    return Scaffold(
      appBar: AppBar(title: const Text('Criar Personagem · Detalhes')),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surfaceVariant,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text('Finalize a descrição do agente.'),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _genderCtrl,
                        decoration: const InputDecoration(labelText: 'Gênero'),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: TextFormField(
                        controller: _ageCtrl,
                        decoration: const InputDecoration(labelText: 'Idade'),
                        keyboardType: TextInputType.number,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _appearanceCtrl,
                  decoration: const InputDecoration(labelText: 'Aparência'),
                  maxLines: 3,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _personalityCtrl,
                  decoration: const InputDecoration(labelText: 'Personalidade'),
                  maxLines: 3,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _backgroundCtrl,
                  decoration: const InputDecoration(labelText: 'Histórico'),
                  maxLines: 4,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _objectiveCtrl,
                  decoration: const InputDecoration(labelText: 'Objetivo'),
                  maxLines: 3,
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
          child: Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: _submitting ? null : () => Navigator.pop(context),
                  child: const Text('Voltar'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton(
                  onPressed: _submitting
                      ? null
                      : () async {
                          draft.setDetails(
                            newGender: _genderCtrl.text,
                            newAge: _ageCtrl.text.trim().isEmpty
                                ? null
                                : int.tryParse(_ageCtrl.text.trim()),
                            newAppearance: _appearanceCtrl.text,
                            newPersonality: _personalityCtrl.text,
                            newBackground: _backgroundCtrl.text,
                            newObjective: _objectiveCtrl.text,
                          );
                          setState(() => _submitting = true);
                          try {
                            await draft.submit();
                            if (!context.mounted) return;
                            // Atualizar lista de personagens
                            try {
                              await context.read<CharactersController>().load();
                            } catch (_) {
                              // Ignorar erro ao recarregar lista
                            }
                            
                            if (!context.mounted) return;
                            
                            // Fechar todas as telas do wizard e voltar para a lista de personagens
                            Navigator.of(context).popUntil((route) => 
                              route.isFirst || route.settings.name == AppRoutes.characters
                            );
                            
                            // Se não chegou na lista, navegar para ela
                            if (context.mounted && Navigator.canPop(context)) {
                              Navigator.pushReplacementNamed(context, AppRoutes.characters);
                            } else if (context.mounted) {
                              Navigator.popUntil(context, (route) => route.isFirst);
                              Navigator.pushNamed(context, AppRoutes.characters);
                            }
                          } catch (e) {
                            if (!context.mounted) return;
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text('Erro ao criar personagem: $e'),
                              ),
                            );
                          } finally {
                            if (mounted) setState(() => _submitting = false);
                          }
                        },
                  child: _submitting
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Criar Personagem'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
