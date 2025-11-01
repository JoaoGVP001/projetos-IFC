import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/constants/app_routes.dart';
import 'package:sigilrpg/controllers/theme_controller.dart';
import 'package:sigilrpg/controllers/auth_controller.dart';
import 'package:sigilrpg/widgets/bottom_nav_bar.dart';
import 'package:sigilrpg/views/home/home_view.dart';
import 'package:sigilrpg/views/characters/characters_list_view.dart';
import 'package:sigilrpg/views/campaigns/campaigns_view.dart';
import 'package:sigilrpg/views/dice/dice_view.dart';

class MainScaffold extends StatefulWidget {
  final int initialIndex;
  
  const MainScaffold({
    super.key,
    this.initialIndex = 0,
  });

  @override
  State<MainScaffold> createState() => _MainScaffoldState();
}

class _MainScaffoldState extends State<MainScaffold> {
  late int _currentIndex;
  final PageController _pageController = PageController();

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _onNavTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
    _pageController.animateToPage(
      index,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  @override
  Widget build(BuildContext context) {
    final themeController = context.watch<ThemeController>();
    final authController = context.watch<AuthController>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('SIGIL RPG'),
        actions: [
          IconButton(
            icon: Icon(
              themeController.isDark ? Icons.light_mode : Icons.dark_mode,
            ),
            tooltip: 'Alternar tema',
            onPressed: () => themeController.toggleTheme(),
          ),
          if (authController.isAuthenticated)
            IconButton(
              tooltip: 'Sair',
              onPressed: () => context.read<AuthController>().logout(),
              icon: const Icon(Icons.logout),
            )
          else
            IconButton(
              tooltip: 'Entrar',
              onPressed: () => Navigator.pushNamed(context, AppRoutes.login),
              icon: const Icon(Icons.login),
            ),
        ],
      ),
      body: PageView(
        controller: _pageController,
        physics: const NeverScrollableScrollPhysics(),
        children: const [
          HomeView(),
          CharactersListView(),
          CampaignsView(),
          DiceView(),
        ],
      ),
      bottomNavigationBar: CustomBottomNavBar(
        currentIndex: _currentIndex,
        onTap: _onNavTapped,
      ),
    );
  }
}

