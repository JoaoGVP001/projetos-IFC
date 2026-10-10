import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';

enum AppThemeMode { light, dark, system }

class ThemeController extends ChangeNotifier {
  AppThemeMode _themeMode = AppThemeMode.dark;
  Color _seedColor = const Color(0xFF6B46C1);

  AppThemeMode get themeMode => _themeMode;
  Color get seedColor => _seedColor;
  bool get isDark => _themeMode == AppThemeMode.dark;

  void setThemeMode(AppThemeMode mode) {
    _themeMode = mode;
    notifyListeners();
  }

  void toggleTheme() {
    _themeMode = _themeMode == AppThemeMode.dark
        ? AppThemeMode.light
        : AppThemeMode.dark;
    notifyListeners();
  }

  void setSeedColor(Color color) {
    _seedColor = color;
    notifyListeners();
  }

  Brightness getBrightness(BuildContext context) {
    switch (_themeMode) {
      case AppThemeMode.light:
        return Brightness.light;
      case AppThemeMode.dark:
        return Brightness.dark;
      case AppThemeMode.system:
        return MediaQuery.of(context).platformBrightness;
    }
  }
}

