import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/controllers/auth_controller.dart';
import 'package:sigilrpg/views/home/home_view.dart';
import 'package:sigilrpg/views/auth/login_view.dart';

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthController>(
      builder: (context, auth, child) {
        // Se ainda está carregando a sessão, mostra loading
        if (auth.isLoading && !auth.isAuthenticated) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        // Se não está autenticado, mostra login
        if (!auth.isAuthenticated) {
          return const LoginView();
        }

        // Se está autenticado, mostra a home
        return const HomeView();
      },
    );
  }
}
