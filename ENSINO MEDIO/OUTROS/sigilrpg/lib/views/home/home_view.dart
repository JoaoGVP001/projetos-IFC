import 'package:flutter/material.dart';
import 'package:sigilrpg/constants/app_colors.dart';
import 'package:sigilrpg/constants/app_routes.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/controllers/auth_controller.dart';
import 'package:sigilrpg/controllers/characters_controller.dart';
import 'package:sigilrpg/controllers/campaigns_controller.dart';
import 'package:sigilrpg/widgets/stat_card.dart';
import 'package:sigilrpg/widgets/custom_button.dart';
import 'package:sigilrpg/widgets/empty_state.dart';

class HomeView extends StatefulWidget {
  const HomeView({super.key});

  @override
  State<HomeView> createState() => _HomeViewState();
}

class _HomeViewState extends State<HomeView> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    final auth = context.read<AuthController>();
    if (auth.isAuthenticated) {
      try {
        await context.read<CharactersController>().load();
        await context.read<CampaignsController>().loadCampaigns();
      } catch (e) {
        // Silently handle errors
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthController>();
    final characters = context.watch<CharactersController>().characters;
    final campaigns = context.watch<CampaignsController>().campaigns;

    return RefreshIndicator(
      onRefresh: _loadData,
      child: CustomScrollView(
        slivers: [
          SliverToBoxAdapter(
            child: _buildHeader(context, auth),
          ),
          if (auth.isAuthenticated) ...[
            SliverToBoxAdapter(
              child: _buildStats(context, characters.length, campaigns.length),
            ),
            SliverToBoxAdapter(
              child: _buildQuickActions(context, auth),
            ),
            SliverToBoxAdapter(
              child: _buildRecentActivity(context),
            ),
          ] else ...[
            SliverFillRemaining(
              hasScrollBody: false,
              child: EmptyState(
                icon: Icons.login,
                title: 'Bem-vindo ao SIGIL RPG',
                message: 'Faça login para criar personagens e gerenciar suas campanhas',
                actionLabel: 'Fazer Login',
                onAction: () => Navigator.pushNamed(context, AppRoutes.login),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context, AuthController auth) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppColors.seed.withOpacity(0.3),
            AppColors.seed.withOpacity(0.1),
          ],
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'SIGIL RPG',
            style: Theme.of(context).textTheme.displaySmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppColors.seed,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            auth.isAuthenticated
                ? 'Gerencie seus personagens e campanhas'
                : 'Sistema de gerenciamento para Ordem Paranormal',
            style: Theme.of(context).textTheme.bodyLarge,
          ),
        ],
      ),
    );
  }

  Widget _buildStats(BuildContext context, int charactersCount, int campaignsCount) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: StatCard(
              label: 'Personagens',
              value: charactersCount.toString(),
              icon: Icons.people,
              color: AppColors.seed,
              onTap: () => Navigator.pushNamed(context, AppRoutes.characters),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: StatCard(
              label: 'Campanhas',
              value: campaignsCount.toString(),
              icon: Icons.map,
              color: Colors.blue,
              onTap: () => Navigator.pushNamed(context, AppRoutes.campaigns),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions(BuildContext context, AuthController auth) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Ações Rápidas',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              _buildQuickActionCard(
                context,
                icon: Icons.person_add,
                label: 'Criar Personagem',
                color: AppColors.seed,
                onTap: () => Navigator.pushNamed(context, AppRoutes.characterCreate),
              ),
              _buildQuickActionCard(
                context,
                icon: Icons.casino,
                label: 'Rolador de Dados',
                color: Colors.orange,
                onTap: () => Navigator.pushNamed(context, AppRoutes.dice),
              ),
              _buildQuickActionCard(
                context,
                icon: Icons.sports_mma,
                label: 'Lutas',
                color: Colors.red,
                onTap: () => Navigator.pushNamed(context, AppRoutes.fights),
              ),
              _buildQuickActionCard(
                context,
                icon: Icons.group_work,
                label: 'Equipes',
                color: Colors.blue,
                onTap: () => Navigator.pushNamed(context, AppRoutes.teams),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionCard(
    BuildContext context, {
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        width: (MediaQuery.of(context).size.width - 44) / 2,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: color.withOpacity(0.3),
            width: 1,
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 32, color: color),
            const SizedBox(height: 8),
            Text(
              label,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: color,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentActivity(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Atividade Recente',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              TextButton(
                onPressed: () {},
                child: const Text('Ver tudo'),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.seed.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(Icons.history, color: AppColors.seed),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Nenhuma atividade recente',
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                        Text(
                          'Suas ações aparecerão aqui',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
