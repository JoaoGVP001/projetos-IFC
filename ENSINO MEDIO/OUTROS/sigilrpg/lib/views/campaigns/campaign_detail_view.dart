import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/constants/app_colors.dart';
import 'package:sigilrpg/controllers/campaigns_controller.dart';
import 'package:sigilrpg/controllers/characters_controller.dart';
import 'package:sigilrpg/models/campaign.dart';
import 'package:sigilrpg/models/campaign_member.dart';
import 'package:sigilrpg/models/character.dart';
import 'package:sigilrpg/models/team.dart';
import 'package:sigilrpg/views/campaigns/campaign_create_edit_view.dart';

class CampaignDetailView extends StatefulWidget {
  final Campaign campaign;

  const CampaignDetailView({super.key, required this.campaign});

  @override
  State<CampaignDetailView> createState() => _CampaignDetailViewState();
}

class _CampaignDetailViewState extends State<CampaignDetailView> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final campaignsController = context.read<CampaignsController>();
      final charactersController = context.read<CharactersController>();

      await Future.wait([
        campaignsController.loadCampaignMembers(widget.campaign.id),
        campaignsController.loadCampaignTeams(
          widget.campaign.id,
          campaignName: widget.campaign.name,
        ),
        if (charactersController.characters.isEmpty)
          charactersController.load(),
      ]);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.campaign.name),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) =>
                      CampaignCreateEditView(campaign: widget.campaign),
                ),
              );
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          final campaignsController = context.read<CampaignsController>();
          await campaignsController.loadCampaignMembers(widget.campaign.id);
          await campaignsController.loadCampaignTeams(
            widget.campaign.id,
            campaignName: widget.campaign.name,
          );
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildHeaderCard(context),
            const SizedBox(height: 16),
            if (widget.campaign.description.isNotEmpty) ...[
              _buildInfoCard(
                context,
                title: 'Descrição',
                content: Text(widget.campaign.description),
                icon: Icons.description,
              ),
              const SizedBox(height: 16),
            ],
            if (widget.campaign.setting.isNotEmpty) ...[
              _buildInfoCard(
                context,
                title: 'Cenário/Mundo',
                content: Text(widget.campaign.setting),
                icon: Icons.map,
              ),
              const SizedBox(height: 16),
            ],
            if (widget.campaign.rules.isNotEmpty) ...[
              _buildInfoCard(
                context,
                title: 'Regras Específicas',
                content: Text(widget.campaign.rules),
                icon: Icons.rule,
              ),
              const SizedBox(height: 16),
            ],
            if (widget.campaign.notes.isNotEmpty) ...[
              _buildInfoCard(
                context,
                title: 'Notas do Mestre',
                content: Text(widget.campaign.notes),
                icon: Icons.note,
              ),
              const SizedBox(height: 16),
            ],
            _buildInfoCard(
              context,
              title: 'Informações',
              content: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Criada em: ${_formatDate(widget.campaign.createdAt)}'),
                  if (widget.campaign.updatedAt != null)
                    Text(
                      'Atualizada em: '
                      '${_formatDate(widget.campaign.updatedAt!)}',
                    ),
                ],
              ),
              icon: Icons.info,
            ),
            const SizedBox(height: 24),
            _buildMembersSection(context),
            const SizedBox(height: 24),
            _buildTeamsSection(context),
            const SizedBox(height: 32),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) =>
                              CampaignCreateEditView(campaign: widget.campaign),
                        ),
                      );
                    },
                    icon: const Icon(Icons.edit),
                    label: const Text('Editar campanha'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _promptAddMember(context),
                    icon: const Icon(Icons.person_add_alt_1),
                    label: const Text('Adicionar personagem'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeaderCard(BuildContext context) {
    final campaign = widget.campaign;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    campaign.name,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: campaign.isActive
                        ? Colors.green.withOpacity(0.2)
                        : Colors.grey.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    campaign.isActive ? 'Ativa' : 'Inativa',
                    style: TextStyle(
                      color: campaign.isActive
                          ? Colors.green[700]
                          : Colors.grey[700],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Mestre: ${campaign.masterName}',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(color: AppColors.accent),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.casino, size: 16, color: AppColors.accent),
                const SizedBox(width: 4),
                Text(campaign.system),
                const SizedBox(width: 16),
                Icon(Icons.people, size: 16, color: AppColors.accent),
                const SizedBox(width: 4),
                Text('Máx. ${campaign.maxPlayers} jogadores'),
                const Spacer(),
                Text(
                  campaign.isPublic ? 'Pública' : 'Privada',
                  style: TextStyle(
                    color: campaign.isPublic ? Colors.blue : Colors.grey,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoCard(
    BuildContext context, {
    required String title,
    required Widget content,
    required IconData icon,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: AppColors.accent),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            content,
          ],
        ),
      ),
    );
  }

  Widget _buildMembersSection(BuildContext context) {
    return Consumer<CampaignsController>(
      builder: (context, controller, _) {
        final members = controller.membersFor(widget.campaign.id);
        final isLoading = controller.membersLoading(widget.campaign.id);
        final error = controller.membersError(widget.campaign.id);

        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        'Personagens na campanha',
                        style: Theme.of(context)
                            .textTheme
                            .titleMedium
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                    ),
                    IconButton(
                      tooltip: 'Adicionar personagem',
                      onPressed: () => _promptAddMember(context),
                      icon: const Icon(Icons.person_add_alt_1),
                    ),
                    IconButton(
                      tooltip: 'Atualizar',
                      onPressed: () => context
                          .read<CampaignsController>()
                          .loadCampaignMembers(widget.campaign.id),
                      icon: const Icon(Icons.refresh),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                if (isLoading)
                  const Center(child: CircularProgressIndicator())
                else if (error != null)
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(error),
                      const SizedBox(height: 8),
                      ElevatedButton.icon(
                        onPressed: () => context
                            .read<CampaignsController>()
                            .loadCampaignMembers(widget.campaign.id),
                        icon: const Icon(Icons.refresh),
                        label: const Text('Tentar novamente'),
                      ),
                    ],
                  )
                else if (members.isEmpty)
                  const Text(
                    'Nenhum personagem vinculado ainda. Adicione personagens para acompanhar a campanha.',
                  )
                else
                  ...members.map((member) => _buildMemberTile(context, member)),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildMemberTile(BuildContext context, CampaignMember member) {
    final character = member.character;
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 6),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: AppColors.seed.withOpacity(0.1),
          child: Text(
            _initialLetter(character?.name),
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
        title: Text(character?.name ?? 'Personagem ${member.characterId}'),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (member.role != null && member.role!.isNotEmpty)
              Text('Função: ${member.role}'),
            if (character?.playerName.isNotEmpty ?? false)
              Text('Jogador(a): ${character!.playerName}'),
            Text(
              member.isActive ? 'Status: Ativo' : 'Status: Inativo',
              style: TextStyle(
                color: member.isActive ? Colors.green[700] : Colors.red[700],
              ),
            ),
          ],
        ),
        trailing: Wrap(
          spacing: 4,
          children: [
            IconButton(
              tooltip: 'Editar função',
              onPressed: () => _promptEditMemberRole(context, member),
              icon: const Icon(Icons.edit),
            ),
            IconButton(
              tooltip: 'Remover da campanha',
              onPressed: () => _confirmRemoveMember(context, member),
              icon: const Icon(Icons.person_remove_alt_1),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTeamsSection(BuildContext context) {
    return Consumer<CampaignsController>(
      builder: (context, controller, _) {
        final teams = controller.teamsFor(widget.campaign.id);
        final isLoading = controller.teamsLoading(widget.campaign.id);
        final error = controller.teamsError(widget.campaign.id);

        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        'Equipes / Parties',
                        style: Theme.of(context)
                            .textTheme
                            .titleMedium
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                    ),
                    IconButton(
                      tooltip: 'Criar equipe',
                      onPressed: () => _promptCreateTeam(context),
                      icon: const Icon(Icons.group_add),
                    ),
                    IconButton(
                      tooltip: 'Atualizar',
                      onPressed: () => context
                          .read<CampaignsController>()
                          .loadCampaignTeams(
                            widget.campaign.id,
                            campaignName: widget.campaign.name,
                          ),
                      icon: const Icon(Icons.refresh),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                if (isLoading)
                  const Center(child: CircularProgressIndicator())
                else if (error != null)
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(error),
                      const SizedBox(height: 8),
                      ElevatedButton.icon(
                        onPressed: () => context
                            .read<CampaignsController>()
                            .loadCampaignTeams(
                              widget.campaign.id,
                              campaignName: widget.campaign.name,
                            ),
                        icon: const Icon(Icons.refresh),
                        label: const Text('Tentar novamente'),
                      ),
                    ],
                  )
                else if (teams.isEmpty)
                  const Text(
                    'Nenhuma equipe cadastrada ainda. Crie uma equipe para organizar missões ou sessões.',
                  )
                else
                  ...teams.map((team) => _buildTeamCard(context, team)),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildTeamCard(BuildContext context, Team team) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 6),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    team.name,
                    style: Theme.of(context)
                        .textTheme
                        .titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ),
                PopupMenuButton<_TeamAction>(
                  onSelected: (action) {
                    switch (action) {
                      case _TeamAction.edit:
                        _promptEditTeam(context, team);
                        break;
                      case _TeamAction.delete:
                        _confirmDeleteTeam(context, team);
                        break;
                    }
                  },
                  itemBuilder: (context) => const [
                    PopupMenuItem(
                      value: _TeamAction.edit,
                      child: ListTile(
                        leading: Icon(Icons.edit),
                        title: Text('Editar equipe'),
                      ),
                    ),
                    PopupMenuItem(
                      value: _TeamAction.delete,
                      child: ListTile(
                        leading: Icon(Icons.delete_outline),
                        title: Text('Excluir equipe'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
            if ((team.description ?? '').isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(team.description!),
            ],
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: team.members.isEmpty
                  ? [
                      const Text('Sem membros atribuídos ainda.'),
                    ]
                  : team.members
                      .map((member) => _buildTeamMemberChip(context, team, member))
                      .toList(),
            ),
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton.icon(
                onPressed: () => _promptAddMemberToTeam(context, team),
                icon: const Icon(Icons.person_add),
                label: const Text('Adicionar membro'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTeamMemberChip(
    BuildContext context,
    Team team,
    TeamMember member,
  ) {
    final characterName = member.character?.name ?? 'Personagem ${member.characterId}';
    final role = member.role;
    return InputChip(
      label: Text(role == null || role.isEmpty
          ? characterName
          : '$characterName • $role'),
      onPressed: () => _promptEditTeamMember(context, team, member),
      onDeleted: () => _confirmRemoveTeamMember(context, team, member),
      deleteIcon: const Icon(Icons.remove_circle_outline),
    );
  }

  Future<void> _promptAddMember(BuildContext context) async {
    final campaignsController = context.read<CampaignsController>();
    final charactersController = context.read<CharactersController>();

    if (charactersController.characters.isEmpty) {
      await charactersController.load();
      if (!mounted) return;
    }

    final existingIds = campaignsController
        .membersFor(widget.campaign.id)
        .map((member) => member.characterId)
        .toSet();

    final availableCharacters = charactersController.characters
        .where((character) => !existingIds.contains(character.id))
        .toList();

    final selectedId = await _showCharacterPicker(
      context,
      characters: availableCharacters,
      title: 'Adicionar personagem à campanha',
      emptyLabel:
          'Nenhum personagem disponível. Crie novos personagens ou remova alguém da campanha.',
    );

    if (!mounted || selectedId == null) return;

    final role = await _askForRole(
      context,
      title: 'Função do personagem (opcional)',
    );
    if (!mounted) return;

    try {
      await campaignsController.addCharacterToCampaign(
        campaignId: widget.campaign.id,
        characterId: selectedId,
        role: role == null || role.isEmpty ? null : role,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Personagem adicionado à campanha.')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao adicionar personagem: $e')),
      );
    }
  }

  Future<void> _promptEditMemberRole(
    BuildContext context,
    CampaignMember member,
  ) async {
    final newRole = await _askForRole(
      context,
      title: 'Editar função',
      initialValue: member.role,
    );

    if (!mounted || newRole == null) return;

    try {
      await context.read<CampaignsController>().updateCampaignMember(
            campaignId: widget.campaign.id,
            characterId: member.characterId,
            role: newRole.isEmpty ? null : newRole,
            clearRole: newRole.isEmpty,
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Função atualizada.')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao atualizar função: $e')),
      );
    }
  }

  Future<void> _confirmRemoveMember(
    BuildContext context,
    CampaignMember member,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Remover personagem'),
        content: Text(
          'Deseja remover ${member.character?.name ?? 'este personagem'} da campanha?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Remover'),
          ),
        ],
      ),
    );

    if (!mounted || confirmed != true) return;

    try {
      await context.read<CampaignsController>().removeCampaignMember(
            campaignId: widget.campaign.id,
            characterId: member.characterId,
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Personagem removido da campanha.')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao remover personagem: $e')),
      );
    }
  }

  Future<void> _promptCreateTeam(BuildContext context) async {
    final nameController = TextEditingController();
    final descriptionController = TextEditingController();

    final created = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Nova equipe'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(labelText: 'Nome da equipe'),
              autofocus: true,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: descriptionController,
              decoration: const InputDecoration(
                labelText: 'Descrição (opcional)',
              ),
              minLines: 1,
              maxLines: 3,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              if (nameController.text.trim().isEmpty) return;
              Navigator.pop(context, true);
            },
            child: const Text('Criar'),
          ),
        ],
      ),
    );

    if (!mounted || created != true) {
      nameController.dispose();
      descriptionController.dispose();
      return;
    }

    final name = nameController.text.trim();
    final description = descriptionController.text.trim().isEmpty
        ? null
        : descriptionController.text.trim();

    nameController.dispose();
    descriptionController.dispose();

    try {
      await context.read<CampaignsController>().createTeam(
            campaignId: widget.campaign.id,
            name: name,
            description: description,
            campaignName: widget.campaign.name,
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Equipe criada com sucesso.')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao criar equipe: $e')),
      );
    }
  }

  Future<void> _promptEditTeam(BuildContext context, Team team) async {
    final nameController = TextEditingController(text: team.name);
    final descriptionController =
        TextEditingController(text: team.description ?? '');

    final updated = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Editar equipe'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(labelText: 'Nome da equipe'),
              autofocus: true,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: descriptionController,
              decoration: const InputDecoration(
                labelText: 'Descrição (opcional)',
              ),
              minLines: 1,
              maxLines: 3,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              if (nameController.text.trim().isEmpty) return;
              Navigator.pop(context, true);
            },
            child: const Text('Salvar'),
          ),
        ],
      ),
    );

    if (!mounted || updated != true) {
      nameController.dispose();
      descriptionController.dispose();
      return;
    }

    final name = nameController.text.trim();
    final description = descriptionController.text.trim().isEmpty
        ? null
        : descriptionController.text.trim();

    nameController.dispose();
    descriptionController.dispose();

    try {
      await context.read<CampaignsController>().updateTeam(
            campaignId: widget.campaign.id,
            teamId: team.id,
            name: name,
            description: description,
            campaignName: widget.campaign.name,
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Equipe atualizada.')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao atualizar equipe: $e')),
      );
    }
  }

  Future<void> _confirmDeleteTeam(BuildContext context, Team team) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Excluir equipe'),
        content: Text('Deseja excluir a equipe "${team.name}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Excluir'),
          ),
        ],
      ),
    );

    if (!mounted || confirmed != true) return;

    try {
      await context.read<CampaignsController>().deleteTeam(
            campaignId: widget.campaign.id,
            teamId: team.id,
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Equipe removida.')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao excluir equipe: $e')),
      );
    }
  }

  Future<void> _promptAddMemberToTeam(BuildContext context, Team team) async {
    final campaignsController = context.read<CampaignsController>();

    final members = campaignsController.membersFor(widget.campaign.id);
    if (members.isEmpty) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Adicione personagens à campanha antes de montar equipes.'),
        ),
      );
      return;
    }

    final memberIdsInTeam = team.members.map((m) => m.characterId).toSet();
    final available = members
        .where((member) => !memberIdsInTeam.contains(member.characterId))
        .toList();

    if (available.isEmpty) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Todos os personagens da campanha já estão nesta equipe.'),
        ),
      );
      return;
    }

    final selected = await showModalBottomSheet<CampaignMember>(
      context: context,
      isScrollControlled: true,
      builder: (context) {
        return SafeArea(
          child: SizedBox(
            height: MediaQuery.of(context).size.height * 0.5,
            child: Column(
              children: [
                ListTile(
                  title: const Text('Selecionar membro'),
                  trailing: IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ),
                const Divider(),
                Expanded(
                  child: ListView.builder(
                    itemCount: available.length,
                    itemBuilder: (context, index) {
                      final member = available[index];
                      return ListTile(
                        title: Text(member.character?.name ?? 'Personagem ${member.characterId}'),
                        subtitle: member.role != null && member.role!.isNotEmpty
                            ? Text('Função: ${member.role}')
                            : null,
                        onTap: () => Navigator.pop(context, member),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );

    if (!mounted || selected == null) return;

    final role = await _askForRole(
      context,
      title: 'Função do membro na equipe (opcional)',
      initialValue: selected.role,
    );
    if (!mounted) return;

    try {
      await context.read<CampaignsController>().addMemberToTeam(
            campaignId: widget.campaign.id,
            teamId: team.id,
            characterId: selected.characterId,
            role: role == null || role.isEmpty ? null : role,
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Membro adicionado à equipe.')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao adicionar membro: $e')),
      );
    }
  }

  Future<void> _promptEditTeamMember(
    BuildContext context,
    Team team,
    TeamMember member,
  ) async {
    final newRole = await _askForRole(
      context,
      title: 'Editar função do membro',
      initialValue: member.role,
    );

    if (!mounted || newRole == null) return;

    try {
      await context.read<CampaignsController>().updateTeamMember(
            campaignId: widget.campaign.id,
            teamId: team.id,
            characterId: member.characterId,
            role: newRole.isEmpty ? null : newRole,
            clearRole: newRole.isEmpty,
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Função atualizada.')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao atualizar membro: $e')),
      );
    }
  }

  Future<void> _confirmRemoveTeamMember(
    BuildContext context,
    Team team,
    TeamMember member,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Remover membro'),
        content: Text(
          'Deseja remover ${member.character?.name ?? 'este membro'} da equipe "${team.name}"?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Remover'),
          ),
        ],
      ),
    );

    if (!mounted || confirmed != true) return;

    try {
      await context.read<CampaignsController>().removeTeamMember(
            campaignId: widget.campaign.id,
            teamId: team.id,
            characterId: member.characterId,
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Membro removido da equipe.')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao remover membro: $e')),
      );
    }
  }

  Future<String?> _askForRole(
    BuildContext context, {
    required String title,
    String? initialValue,
  }) async {
    final controller = TextEditingController(text: initialValue ?? '');
    final result = await showDialog<String?>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: TextField(
          controller: controller,
          decoration:
              const InputDecoration(labelText: 'Função (deixe vazio para remover)'),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, null),
            child: const Text('Cancelar'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, ''),
            child: const Text('Remover'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, controller.text),
            child: const Text('Salvar'),
          ),
        ],
      ),
    );

    controller.dispose();

    if (result == null) return null;
    return result.trim();
  }

  Future<String?> _showCharacterPicker(
    BuildContext context, {
    required List<Character> characters,
    required String title,
    required String emptyLabel,
  }) {
    return showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      builder: (context) {
        return SafeArea(
          child: SizedBox(
            height: MediaQuery.of(context).size.height * 0.6,
            child: Column(
              children: [
                ListTile(
                  title: Text(title),
                  trailing: IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ),
                const Divider(height: 1),
                if (characters.isEmpty)
                  Expanded(
                    child: Center(
                      child: Padding(
                        padding: const EdgeInsets.all(24),
                        child: Text(
                          emptyLabel,
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                  )
                else
                  Expanded(
                    child: ListView.separated(
                      itemCount: characters.length,
                      separatorBuilder: (_, __) => const Divider(height: 1),
                      itemBuilder: (context, index) {
                        final character = characters[index];
                        return ListTile(
                          title: Text(character.name),
                          subtitle: character.playerName.isNotEmpty
                              ? Text('Jogador(a): ${character.playerName}')
                              : null,
                          onTap: () => Navigator.pop(context, character.id),
                        );
                      },
                    ),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}/'
        '${date.month.toString().padLeft(2, '0')}/'
        '${date.year} às '
        '${date.hour.toString().padLeft(2, '0')}:'
        '${date.minute.toString().padLeft(2, '0')}';
  }

  String _initialLetter(String? text) {
    if (text == null || text.trim().isEmpty) return '?';
    final trimmed = text.trim();
    return trimmed.substring(0, 1).toUpperCase();
  }
}

enum _TeamAction { edit, delete }
