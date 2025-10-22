import 'package:flutter/material.dart';
import 'package:sigilrpg/constants/app_colors.dart';
import 'package:sigilrpg/constants/app_routes.dart';

class HomeView extends StatelessWidget {
  const HomeView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('SIGIL RPG')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _Section(
            title: 'Personagens',
            children: [
              _ActionTile(
                icon: Icons.people_alt,
                title: 'Meus Personagens',
                subtitle: 'Veja e gerencie suas fichas',
                onTap: () => Navigator.pushNamed(context, AppRoutes.characters),
              ),
              _ActionTile(
                icon: Icons.person_add_alt,
                title: 'Criar Personagem',
                subtitle: 'Wizard passo a passo',
                onTap: () =>
                    Navigator.pushNamed(context, AppRoutes.characterCreate),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _Section(
            title: 'Campanhas',
            children: [
              _ActionTile(
                icon: Icons.map,
                title: 'Campanhas',
                subtitle: 'Gerencie campanhas e sessões',
                onTap: () => Navigator.pushNamed(context, AppRoutes.campaigns),
              ),
              _ActionTile(
                icon: Icons.group_work,
                title: 'Equipes',
                subtitle: 'Jogadores, mapas e anotações',
                onTap: () => Navigator.pushNamed(context, AppRoutes.teams),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _Section(
            title: 'Ferramentas',
            children: [
              _ActionTile(
                icon: Icons.casino,
                title: 'Rolador de Dados',
                subtitle: 'd20, múltiplos dados e histórico',
                onTap: () => Navigator.pushNamed(context, AppRoutes.dice),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _Section extends StatelessWidget {
  final String title;
  final List<Widget> children;
  const _Section({required this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: Text(
              title,
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700),
            ),
          ),
          const Divider(height: 1),
          ...children,
        ],
      ),
    );
  }
}

class _ActionTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  const _ActionTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: AppColors.accent.withOpacity(0.15),
        child: Icon(icon, color: AppColors.accent),
      ),
      title: Text(title),
      subtitle: Text(subtitle),
      onTap: onTap,
    );
  }
}
