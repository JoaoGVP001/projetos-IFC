import 'package:flutter/material.dart';
import 'package:sigilrpg/constants/app_colors.dart';
import 'package:sigilrpg/models/campaign.dart';
import 'package:sigilrpg/views/campaigns/campaign_create_edit_view.dart';

class CampaignDetailView extends StatelessWidget {
  final Campaign campaign;

  const CampaignDetailView({super.key, required this.campaign});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(campaign.name),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) =>
                      CampaignCreateEditView(campaign: campaign),
                ),
              );
            },
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Header da Campanha
          Card(
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
                          style: Theme.of(context).textTheme.headlineSmall
                              ?.copyWith(fontWeight: FontWeight.bold),
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
                    style: Theme.of(
                      context,
                    ).textTheme.titleMedium?.copyWith(color: AppColors.accent),
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
          ),

          const SizedBox(height: 16),

          // Descrição
          if (campaign.description.isNotEmpty) ...[
            _buildInfoCard(
              context,
              title: 'Descrição',
              content: Text(campaign.description),
              icon: Icons.description,
            ),
            const SizedBox(height: 16),
          ],

          // Cenário
          if (campaign.setting.isNotEmpty) ...[
            _buildInfoCard(
              context,
              title: 'Cenário/Mundo',
              content: Text(campaign.setting),
              icon: Icons.map,
            ),
            const SizedBox(height: 16),
          ],

          // Regras
          if (campaign.rules.isNotEmpty) ...[
            _buildInfoCard(
              context,
              title: 'Regras Específicas',
              content: Text(campaign.rules),
              icon: Icons.rule,
            ),
            const SizedBox(height: 16),
          ],

          // Notas do Mestre
          if (campaign.notes.isNotEmpty) ...[
            _buildInfoCard(
              context,
              title: 'Notas do Mestre',
              content: Text(campaign.notes),
              icon: Icons.note,
            ),
            const SizedBox(height: 16),
          ],

          // Informações de Data
          _buildInfoCard(
            context,
            title: 'Informações',
            content: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Criada em: ${_formatDate(campaign.createdAt)}'),
                if (campaign.updatedAt != null)
                  Text('Atualizada em: ${_formatDate(campaign.updatedAt!)}'),
              ],
            ),
            icon: Icons.info,
          ),

          const SizedBox(height: 32),

          // Botões de Ação
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) =>
                            CampaignCreateEditView(campaign: campaign),
                      ),
                    );
                  },
                  icon: const Icon(Icons.edit),
                  label: const Text('Editar'),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () {
                    // TODO: Implementar visualização de personagens da campanha
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Funcionalidade em desenvolvimento'),
                      ),
                    );
                  },
                  icon: const Icon(Icons.people),
                  label: const Text('Personagens'),
                ),
              ),
            ],
          ),
        ],
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

  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}/'
        '${date.month.toString().padLeft(2, '0')}/'
        '${date.year} às '
        '${date.hour.toString().padLeft(2, '0')}:'
        '${date.minute.toString().padLeft(2, '0')}';
  }
}
