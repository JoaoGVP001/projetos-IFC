import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/controllers/character_draft_controller.dart';
import 'package:sigilrpg/views/characters/character_create_wizard_routes.dart';

class CharacterCreateBasicsView extends StatefulWidget {
  const CharacterCreateBasicsView({super.key});

  @override
  State<CharacterCreateBasicsView> createState() =>
      _CharacterCreateBasicsViewState();
}

class _CharacterCreateBasicsViewState extends State<CharacterCreateBasicsView> {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _playerCtrl = TextEditingController();
  int _nex = 5;
  String? _avatarUrl;

  @override
  void dispose() {
    _nameCtrl.dispose();
    _playerCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final draft = context.watch<CharacterDraftController>();
    _nameCtrl.text = draft.name;
    _playerCtrl.text = draft.playerName;
    _nex = draft.nex;
    _avatarUrl = draft.avatarUrl;

    return Scaffold(
      appBar: AppBar(title: const Text('Criar Personagem · Básico')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _nameCtrl,
                decoration: const InputDecoration(
                  labelText: 'Nome do Personagem',
                ),
                validator: (v) =>
                    (v == null || v.trim().isEmpty) ? 'Informe o nome' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _playerCtrl,
                decoration: const InputDecoration(
                  labelText: 'Jogador Responsável',
                ),
                validator: (v) => (v == null || v.trim().isEmpty)
                    ? 'Informe o jogador'
                    : null,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  const Text('NEX:'),
                  Expanded(
                    child: Slider(
                      min: 5,
                      max: 50,
                      divisions: 9,
                      value: _nex.toDouble(),
                      label: '$_nex%',
                      onChanged: (v) => setState(() => _nex = v.round()),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              TextFormField(
                initialValue: _avatarUrl,
                decoration: const InputDecoration(
                  labelText: 'Avatar URL (opcional)',
                ),
                onChanged: (v) =>
                    _avatarUrl = v.trim().isEmpty ? null : v.trim(),
              ),
              const Spacer(),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        if (!(_formKey.currentState?.validate() ?? false))
                          return;
                        draft.setBasics(
                          newName: _nameCtrl.text,
                          newPlayerName: _playerCtrl.text,
                          newNex: _nex,
                          newAvatarUrl: _avatarUrl,
                        );
                        Navigator.pushNamed(
                          context,
                          CharacterCreateRoutes.origin,
                        );
                      },
                      child: const Text('Continuar'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
