import 'package:flutter/material.dart';
import 'package:sigilrpg/constants/app_routes.dart';

class CustomBottomNavBar extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;

  const CustomBottomNavBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: currentIndex,
      onTap: onTap,
      type: BottomNavigationBarType.fixed,
      selectedFontSize: 12,
      unselectedFontSize: 12,
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.home),
          activeIcon: Icon(Icons.home),
          label: 'Início',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.people),
          activeIcon: Icon(Icons.people),
          label: 'Personagens',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.map),
          activeIcon: Icon(Icons.map),
          label: 'Campanhas',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.build),
          activeIcon: Icon(Icons.build),
          label: 'Ferramentas',
        ),
      ],
    );
  }

  static int getIndexForRoute(String route) {
    switch (route) {
      case AppRoutes.home:
        return 0;
      case AppRoutes.characters:
        return 1;
      case AppRoutes.campaigns:
        return 2;
      case AppRoutes.dice:
      case AppRoutes.fights:
      case AppRoutes.teams:
        return 3;
      default:
        return 0;
    }
  }
}

