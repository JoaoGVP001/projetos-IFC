import 'package:flutter/material.dart';
import 'package:sigilrpg/constants/app_colors.dart';

ThemeData buildAppTheme({
  Brightness brightness = Brightness.dark,
  Color seed = AppColors.seed,
}) {
  final isDark = brightness == Brightness.dark;
  
  final colorScheme = ColorScheme.fromSeed(
    seedColor: seed,
    brightness: brightness,
  );

  return ThemeData(
    brightness: brightness,
    colorScheme: colorScheme.copyWith(
      background: isDark ? AppColors.background : Colors.grey[50],
      surface: isDark ? AppColors.surface : Colors.white,
      surfaceVariant: isDark ? AppColors.surfaceElevated : Colors.grey[100],
      onSurface: isDark ? Colors.white : Colors.black87,
      onBackground: isDark ? Colors.white : Colors.black87,
    ),
    scaffoldBackgroundColor: isDark ? AppColors.background : Colors.grey[50],
    appBarTheme: AppBarTheme(
      backgroundColor: isDark ? AppColors.surface : Colors.white,
      foregroundColor: isDark ? Colors.white : Colors.black87,
      elevation: 0,
      centerTitle: false,
      surfaceTintColor: Colors.transparent,
    ),
    cardTheme: CardThemeData(
      margin: EdgeInsets.zero,
      clipBehavior: Clip.antiAlias,
      color: isDark ? AppColors.surface : Colors.white,
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
    ),
    listTileTheme: ListTileThemeData(
      iconColor: isDark ? Colors.white70 : Colors.black54,
      textColor: isDark ? Colors.white : Colors.black87,
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: isDark ? AppColors.surface : Colors.white,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: isDark ? Colors.white12 : Colors.grey[300]!,
        ),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: isDark ? Colors.white12 : Colors.grey[300]!,
        ),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: seed,
          width: 2,
        ),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: AppColors.danger,
        ),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: AppColors.danger,
          width: 2,
        ),
      ),
    ),
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: isDark ? AppColors.surface : Colors.white,
      selectedItemColor: seed,
      unselectedItemColor: isDark ? Colors.white60 : Colors.grey,
      type: BottomNavigationBarType.fixed,
      elevation: 8,
    ),
    useMaterial3: true,
    visualDensity: VisualDensity.standard,
    textTheme: TextTheme(
      displayLarge: TextStyle(
        color: isDark ? Colors.white : Colors.black87,
        fontWeight: FontWeight.bold,
      ),
      displayMedium: TextStyle(
        color: isDark ? Colors.white : Colors.black87,
        fontWeight: FontWeight.bold,
      ),
      headlineSmall: TextStyle(
        color: isDark ? Colors.white : Colors.black87,
        fontWeight: FontWeight.w600,
      ),
      titleLarge: TextStyle(
        color: isDark ? Colors.white : Colors.black87,
        fontWeight: FontWeight.w600,
      ),
      bodyLarge: TextStyle(
        color: isDark ? Colors.white : Colors.black87,
      ),
      bodyMedium: TextStyle(
        color: isDark ? Colors.white70 : Colors.black54,
      ),
      bodySmall: TextStyle(
        color: isDark ? Colors.white60 : Colors.black45,
      ),
    ),
  );
}
