import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/models/character.dart';
import 'package:sigilrpg/widgets/character_card.dart';
import 'package:sigilrpg/constants/app_routes.dart';
import 'package:sigilrpg/controllers/characters_controller.dart';

class CharactersListView extends StatefulWidget {
  const CharactersListView({super.key});

  @override
  State<CharactersListView> createState() => _CharactersListViewState();
}

class _CharactersListViewState extends State<CharactersListView> {
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final controller = context.read<CharactersController>();
      try {
        await controller.load();
      } catch (e) {
        setState(() => _error = e.toString());
      } finally {
        if (mounted) setState(() => _loading = false);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Personagens')),
      body: Builder(
        builder: (context) {
          if (_loading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (_error != null) {
            return Center(child: Text(_error!));
          }
          final characters = context.watch<CharactersController>().characters;
          if (characters.isEmpty) {
            return const Center(child: Text('Nenhum personagem.'));
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: characters.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, i) => CharacterCard(
              character: characters[i],
              onTap: () => Navigator.pushNamed(
                context,
                AppRoutes.characters + '/${characters[i].id}',
                arguments: characters[i],
              ),
            ),
          );
        },
      ),
    );
  }
}
