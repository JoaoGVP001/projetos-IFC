import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/constants/app_colors.dart';
import 'package:sigilrpg/controllers/campaigns_controller.dart';
import 'package:sigilrpg/models/campaign.dart';

class CampaignCreateEditView extends StatefulWidget {
  final Campaign? campaign; // null para criar, não-null para editar

  const CampaignCreateEditView({super.key, this.campaign});

  @override
  State<CampaignCreateEditView> createState() => _CampaignCreateEditViewState();
}

class _CampaignCreateEditViewState extends State<CampaignCreateEditView> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _masterNameController = TextEditingController();
  final _settingController = TextEditingController();
  final _rulesController = TextEditingController();
  final _notesController = TextEditingController();

  String _system = 'Sigil RPG';
  int _maxPlayers = 6;
  bool _isActive = true;
  bool _isPublic = false;

  bool get _isEditing => widget.campaign != null;

  @override
  void initState() {
    super.initState();
    if (_isEditing) {
      _populateFields();
    }
  }

  void _populateFields() {
    final campaign = widget.campaign!;
    _nameController.text = campaign.name;
    _descriptionController.text = campaign.description;
    _masterNameController.text = campaign.masterName;
    _settingController.text = campaign.setting;
    _rulesController.text = campaign.rules;
    _notesController.text = campaign.notes;
    _system = campaign.system;
    _maxPlayers = campaign.maxPlayers;
    _isActive = campaign.isActive;
    _isPublic = campaign.isPublic;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _masterNameController.dispose();
    _settingController.dispose();
    _rulesController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? 'Editar Campanha' : 'Nova Campanha'),
        actions: [
          TextButton(onPressed: _saveCampaign, child: const Text('Salvar')),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Informações Básicas
            _buildSection(
              title: 'Informações Básicas',
              children: [
                TextFormField(
                  controller: _nameController,
                  decoration: const InputDecoration(
                    labelText: 'Nome da Campanha *',
                    hintText: 'Ex: Aventuras em Sigil',
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Nome é obrigatório';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _descriptionController,
                  decoration: const InputDecoration(
                    labelText: 'Descrição',
                    hintText: 'Descreva brevemente a campanha...',
                  ),
                  maxLines: 3,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _masterNameController,
                  decoration: const InputDecoration(
                    labelText: 'Nome do Mestre *',
                    hintText: 'Seu nome como mestre',
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Nome do mestre é obrigatório';
                    }
                    return null;
                  },
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Configurações
            _buildSection(
              title: 'Configurações',
              children: [
                DropdownButtonFormField<String>(
                  value: _system,
                  decoration: const InputDecoration(
                    labelText: 'Sistema de RPG',
                  ),
                  items: const [
                    DropdownMenuItem(
                      value: 'Sigil RPG',
                      child: Text('Sigil RPG'),
                    ),
                    DropdownMenuItem(value: 'D&D 5e', child: Text('D&D 5e')),
                    DropdownMenuItem(
                      value: 'Pathfinder',
                      child: Text('Pathfinder'),
                    ),
                    DropdownMenuItem(value: 'Outro', child: Text('Outro')),
                  ],
                  onChanged: (value) {
                    setState(() {
                      _system = value!;
                    });
                  },
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        initialValue: _maxPlayers.toString(),
                        decoration: const InputDecoration(
                          labelText: 'Máximo de Jogadores',
                        ),
                        keyboardType: TextInputType.number,
                        onChanged: (value) {
                          _maxPlayers = int.tryParse(value) ?? 6;
                        },
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          CheckboxListTile(
                            title: const Text('Campanha Ativa'),
                            value: _isActive,
                            onChanged: (value) {
                              setState(() {
                                _isActive = value ?? true;
                              });
                            },
                            contentPadding: EdgeInsets.zero,
                          ),
                          CheckboxListTile(
                            title: const Text('Campanha Pública'),
                            value: _isPublic,
                            onChanged: (value) {
                              setState(() {
                                _isPublic = value ?? false;
                              });
                            },
                            contentPadding: EdgeInsets.zero,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Detalhes da Campanha
            _buildSection(
              title: 'Detalhes da Campanha',
              children: [
                TextFormField(
                  controller: _settingController,
                  decoration: const InputDecoration(
                    labelText: 'Cenário/Mundo',
                    hintText: 'Descreva o mundo onde a campanha se passa...',
                  ),
                  maxLines: 3,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _rulesController,
                  decoration: const InputDecoration(
                    labelText: 'Regras Específicas',
                    hintText: 'Regras específicas para esta campanha...',
                  ),
                  maxLines: 3,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _notesController,
                  decoration: const InputDecoration(
                    labelText: 'Notas do Mestre',
                    hintText: 'Notas privadas sobre a campanha...',
                  ),
                  maxLines: 3,
                ),
              ],
            ),

            const SizedBox(height: 32),

            // Botões de Ação
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('Cancelar'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _saveCampaign,
                    child: Text(_isEditing ? 'Atualizar' : 'Criar'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection({
    required String title,
    required List<Widget> children,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            ...children,
          ],
        ),
      ),
    );
  }

  Future<void> _saveCampaign() async {
    if (!_formKey.currentState!.validate()) return;

    final controller = context.read<CampaignsController>();

    final campaign = Campaign(
      id: _isEditing ? widget.campaign!.id : '',
      name: _nameController.text.trim(),
      description: _descriptionController.text.trim(),
      system: _system,
      maxPlayers: _maxPlayers,
      isActive: _isActive,
      isPublic: _isPublic,
      setting: _settingController.text.trim(),
      rules: _rulesController.text.trim(),
      notes: _notesController.text.trim(),
      masterName: _masterNameController.text.trim(),
      createdAt: _isEditing ? widget.campaign!.createdAt : DateTime.now(),
    );

    if (_isEditing) {
      await controller.updateCampaign(campaign.id, campaign.toJson());
    } else {
      await controller.createCampaign(campaign);
    }

    if (mounted) {
      Navigator.pop(context);
    }
  }
}
