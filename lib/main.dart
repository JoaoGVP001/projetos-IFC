import 'package:flutter/material.dart';
import 'package:sigilrpg/constants/app_routes.dart';
import 'package:sigilrpg/constants/app_theme.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/controllers/characters_controller.dart';
import 'package:sigilrpg/controllers/auth_controller.dart';
import 'package:sigilrpg/controllers/character_draft_controller.dart';
import 'package:sigilrpg/controllers/campaigns_controller.dart';
import 'package:sigilrpg/controllers/teams_controller.dart';
import 'package:sigilrpg/controllers/dicecontroller.dart';
import 'package:sigilrpg/controllers/theme_controller.dart';
import 'package:sigilrpg/views/main_scaffold.dart';
import 'package:sigilrpg/views/characters/characters_list_view.dart';
import 'package:sigilrpg/views/characters/character_create_basics_view.dart';
import 'package:sigilrpg/views/characters/character_create_origin_view.dart';
import 'package:sigilrpg/views/characters/character_create_class_view.dart';
import 'package:sigilrpg/views/characters/character_create_details_view.dart';
import 'package:sigilrpg/views/characters/character_create_wizard_routes.dart';
import 'package:sigilrpg/views/characters/character_detail_view.dart';
import 'package:sigilrpg/views/characters/character_attributes_edit_view.dart';
import 'package:sigilrpg/views/campaigns/campaigns_view.dart';
import 'package:sigilrpg/views/teams/teams_view.dart';
import 'package:sigilrpg/views/dice/dice_view.dart';
import 'package:sigilrpg/views/auth/login_view.dart';
import 'package:sigilrpg/views/auth/register_view.dart';
import 'package:sigilrpg/views/fights/fights_view.dart';
import 'package:sigilrpg/services/notification_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Inicializa o serviço de notificações
  await NotificationService().initialize();
  
  runApp(const SigilRpgApp());
}

class SigilRpgApp extends StatelessWidget {
  const SigilRpgApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ThemeController()),
        ChangeNotifierProvider(create: (_) => AuthController()),
        ChangeNotifierProvider(create: (_) => CharactersController()),
        ChangeNotifierProvider(create: (_) => CharacterDraftController()),
        ChangeNotifierProvider(create: (_) => CampaignsController()),
        ChangeNotifierProvider(create: (_) => TeamsController()),
        ChangeNotifierProvider(create: (_) => DiceController()),
      ],
      child: Consumer<ThemeController>(
        builder: (context, themeController, _) {
          return MaterialApp(
            debugShowCheckedModeBanner: false,
            title: 'SIGIL RPG',
            theme: buildAppTheme(
              brightness: Brightness.light,
              seed: themeController.seedColor,
            ),
            darkTheme: buildAppTheme(
              brightness: Brightness.dark,
              seed: themeController.seedColor,
            ),
            themeMode: themeController.themeMode == AppThemeMode.system
                ? ThemeMode.system
                : themeController.themeMode == AppThemeMode.dark
                    ? ThemeMode.dark
                    : ThemeMode.light,
            initialRoute: AppRoutes.home,
            routes: {
              AppRoutes.home: (_) => const MainScaffold(initialIndex: 0),
              AppRoutes.characters: (_) => const CharactersListView(),
              AppRoutes.characterCreate: (_) => const CharacterCreateBasicsView(),
              CharacterCreateRoutes.basics: (_) =>
                  const CharacterCreateBasicsView(),
              CharacterCreateRoutes.origin: (_) =>
                  const CharacterCreateOriginView(),
              CharacterCreateRoutes.clazz: (_) => const CharacterCreateClassView(),
              CharacterCreateRoutes.details: (_) =>
                  const CharacterCreateDetailsView(),
              AppRoutes.campaigns: (_) => const CampaignsView(),
              AppRoutes.teams: (_) => const TeamsView(),
              AppRoutes.dice: (_) => const DiceView(),
              AppRoutes.login: (_) => const LoginView(),
              AppRoutes.register: (_) => const RegisterView(),
              AppRoutes.fights: (_) => const FightsView(),
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
              if (name == '/characters/attributes/edit') {
                final args = settings.arguments;
                if (args is! String) return null;
                return MaterialPageRoute(
                  builder: (_) => CharacterAttributesEditView(characterId: args),
                  settings: settings,
                );
              }
              return null;
            },
          );
        },
      ),
    );
  }
}
