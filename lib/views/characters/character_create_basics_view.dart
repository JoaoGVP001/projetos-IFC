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
  final _nexCtrl = TextEditingController();
  String? _avatarUrl;

  @override
  void initState() {
    super.initState();
    _nexCtrl.text = '5';
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _playerCtrl.dispose();
    _nexCtrl.dispose();
    super.dispose();
  }

  List<DropdownMenuItem<int>> _buildNexItems() {
    final List<int> nexValues = [];

    // Adiciona valores de 5 em 5 até 95
    for (int i = 5; i <= 95; i += 5) {
      nexValues.add(i);
    }

    // Adiciona valores especiais: 99 e 100
    nexValues.addAll([99, 100]);

    return nexValues.map((nex) {
      return DropdownMenuItem<int>(value: nex, child: Text('$nex%'));
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final draft = context.watch<CharacterDraftController>();
    _nameCtrl.text = draft.name;
    _playerCtrl.text = draft.playerName;
    _nexCtrl.text = draft.nex.toString();
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
              DropdownButtonFormField<int>(
                value: draft.nex,
                decoration: const InputDecoration(
                  labelText: 'NEX (%)',
                  suffixText: '%',
                ),
                items: _buildNexItems(),
                validator: (value) {
                  if (value == null) {
                    return 'Selecione o NEX';
                  }
                  return null;
                },
                onChanged: (value) {
                  if (value != null) {
                    setState(() {
                      _nexCtrl.text = value.toString();
                    });
                  }
                },
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
                          newNex: draft.nex,
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
