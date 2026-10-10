import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/widgets/character_card.dart';
import 'package:sigilrpg/widgets/empty_state.dart';
import 'package:sigilrpg/widgets/error_state.dart';
import 'package:sigilrpg/constants/app_routes.dart';
import 'package:sigilrpg/controllers/characters_controller.dart';
import 'package:sigilrpg/controllers/auth_controller.dart';

class CharactersListView extends StatefulWidget {
  const CharactersListView({super.key});

  @override
  State<CharactersListView> createState() => _CharactersListViewState();
}

class _CharactersListViewState extends State<CharactersListView> {
  bool _loading = true;
  String? _error;
  bool _hasLoaded = false;
  DateTime? _lastReload;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await _loadCharacters();
    });
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Recarregar quando voltar para esta tela (evitar recarregar muito rápido)
    final now = DateTime.now();
    if (_hasLoaded && 
        !_loading && 
        ModalRoute.of(context)?.isCurrent == true &&
        (_lastReload == null || now.difference(_lastReload!).inSeconds > 1)) {
      _lastReload = now;
      _loadCharacters();
    }
  }

  Future<void> _loadCharacters() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final controller = context.read<CharactersController>();
      await controller.load();
      _hasLoaded = true;
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthController>();
    
    if (!auth.isAuthenticated) {
      return Scaffold(
        appBar: AppBar(title: const Text('Personagens')),
        body: EmptyState(
          icon: Icons.login,
          title: 'Login necessário',
          message: 'Faça login para ver seus personagens',
          actionLabel: 'Fazer Login',
          onAction: () => Navigator.pushNamed(context, AppRoutes.login),
        ),
      );
    }

    if (_loading) {
      return Scaffold(
        appBar: AppBar(title: const Text('Personagens')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_error != null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Personagens')),
        body: ErrorState(
          message: _error,
          onRetry: _loadCharacters,
        ),
      );
    }

    final characters = context.watch<CharactersController>().characters;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Personagens'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            tooltip: 'Criar personagem',
            onPressed: () => Navigator.pushNamed(context, AppRoutes.characterCreate),
          ),
        ],
      ),
      body: characters.isEmpty
          ? EmptyState(
              icon: Icons.person_add,
              title: 'Nenhum personagem',
              message: 'Crie seu primeiro personagem para começar',
              actionLabel: 'Criar Personagem',
              onAction: () => Navigator.pushNamed(context, AppRoutes.characterCreate),
            )
          : RefreshIndicator(
              onRefresh: _loadCharacters,
              child: ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: characters.length,
                separatorBuilder: (_, __) => const SizedBox(height: 12),
                itemBuilder: (context, i) => CharacterCard(
                  character: characters[i],
                  onTap: () => Navigator.pushNamed(
                    context,
                    AppRoutes.characters + '/${characters[i].id}',
                    arguments: characters[i],
                  ),
                ),
              ),
            ),
    );
  }
}
