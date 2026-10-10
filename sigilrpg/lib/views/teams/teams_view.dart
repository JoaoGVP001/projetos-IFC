import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/controllers/teams_controller.dart';
import 'package:sigilrpg/models/team.dart';

class TeamsView extends StatefulWidget {
  const TeamsView({super.key});

  @override
  State<TeamsView> createState() => _TeamsViewState();
}

class _TeamsViewState extends State<TeamsView> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<TeamsController>().load();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Equipes / Parties')),
      body: Consumer<TeamsController>(
        builder: (context, controller, _) {
          if (controller.isLoading && controller.teams.isEmpty) {
            return const Center(child: CircularProgressIndicator());
          }

          if (controller.error != null && controller.teams.isEmpty) {
            return _ErrorView(
              message: controller.error!,
              onRetry: controller.load,
            );
          }

          if (controller.teams.isEmpty) {
            return RefreshIndicator(
              onRefresh: controller.load,
              child: ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                children: const [
                  SizedBox(height: 120),
                  Icon(Icons.group, size: 64, color: Colors.grey),
                  SizedBox(height: 12),
                  Center(
                    child: Padding(
                      padding: EdgeInsets.symmetric(horizontal: 24),
                      child: Text(
                        'Nenhuma equipe encontrada. Crie equipes nas campanhas para que apareçam aqui.',
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: controller.load,
            child: ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: controller.teams.length,
              separatorBuilder: (_, __) => const SizedBox(height: 16),
              itemBuilder: (context, index) {
                final team = controller.teams[index];
                return _TeamCard(team: team);
              },
            ),
          );
        },
      ),
    );
  }
}

class _TeamCard extends StatelessWidget {
  const _TeamCard({required this.team});

  final Team team;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              team.name,
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            if ((team.description ?? '').isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(team.description!),
            ],
            const SizedBox(height: 8),
            Text(
              'Campanha: ${team.campaignName ?? team.campaignId}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: team.members.isEmpty
                  ? [
                      Chip(
                        avatar: const Icon(Icons.info_outline, size: 16),
                        label: const Text('Nenhum membro ainda'),
                      ),
                    ]
                  : team.members
                      .map(
                        (member) => Chip(
                          avatar: const Icon(Icons.person, size: 16),
                          label: Text(
                            member.role == null || member.role!.isEmpty
                                ? (member.character?.name ??
                                    'Personagem ${member.characterId}')
                                : '${member.character?.name ?? member.characterId} • ${member.role}',
                          ),
                        ),
                      )
                      .toList(),
            ),
            if (team.members.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Text(
                  '${team.members.length} membro(s)',
                  style: Theme.of(context)
                      .textTheme
                      .labelMedium
                      ?.copyWith(color: Colors.grey[600]),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});

  final String message;
  final Future<void> Function() onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Colors.redAccent),
            const SizedBox(height: 12),
            Text(
              message,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('Tentar novamente'),
            ),
          ],
        ),
      ),
    );
  }
}
