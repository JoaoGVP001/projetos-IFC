import 'package:flutter/material.dart';
import 'package:sigilrpg/constants/app_colors.dart';
import 'package:sigilrpg/constants/app_routes.dart';
import 'package:sigilrpg/constants/app_theme.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/controllers/characters_controller.dart';
import 'package:sigilrpg/controllers/campaigns_controller.dart';
import 'package:sigilrpg/controllers/teams_controller.dart';
import 'package:sigilrpg/controllers/dicecontroller.dart';
import 'package:sigilrpg/views/home/home_view.dart';
import 'package:sigilrpg/views/characters/characters_list_view.dart';
import 'package:sigilrpg/views/characters/character_create_view.dart';
import 'package:sigilrpg/views/characters/character_detail_view.dart';
import 'package:sigilrpg/views/campaigns/campaigns_view.dart';
import 'package:sigilrpg/views/teams/teams_view.dart';
import 'package:sigilrpg/views/dice/dice_view.dart';

void main() {
  runApp(const SigilRpgApp());
}

class SigilRpgApp extends StatelessWidget {
  const SigilRpgApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => CharactersController()),
        ChangeNotifierProvider(create: (_) => CampaignsController()),
        ChangeNotifierProvider(create: (_) => TeamsController()),
        ChangeNotifierProvider(create: (_) => DiceController()),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'SIGIL RPG',
        theme: buildAppTheme(brightness: Brightness.dark, seed: AppColors.seed),
        initialRoute: AppRoutes.home,
        routes: {
          AppRoutes.home: (_) => const HomeView(),
          AppRoutes.characters: (_) => const CharactersListView(),
          AppRoutes.characterCreate: (_) => const CharacterCreateView(),
          AppRoutes.campaigns: (_) => const CampaignsView(),
          AppRoutes.teams: (_) => const TeamsView(),
          AppRoutes.dice: (_) => const DiceView(),
          // simple dynamic route for detail via onGenerateRoute fallback
        },
        onGenerateRoute: (settings) {
          final name = settings.name ?? '';
          if (name.startsWith(AppRoutes.characters + '/')) {
            final character = settings.arguments;
            if (character is! Object) return null;
            return MaterialPageRoute(
              builder: (_) =>
                  CharacterDetailView(character: character as dynamic),
              settings: settings,
            );
          }
          return null;
        },
      ),
    );
  }
}
