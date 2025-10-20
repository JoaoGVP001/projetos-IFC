import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/controllers/auth_controller.dart';
import 'package:sigilrpg/constants/app_routes.dart';
import 'package:sigilrpg/widgets/debug_info.dart';
import 'package:sigilrpg/services/auth_service.dart';

class LoginView extends StatefulWidget {
  const LoginView({super.key});
  @override
  State<LoginView> createState() => _LoginViewState();
}

class _LoginViewState extends State<LoginView> {
  final _formKey = GlobalKey<FormState>();
  final _userCtrl = TextEditingController();
  final _passCtrl = TextEditingController();

  @override
  void dispose() {
    _userCtrl.dispose();
    _passCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthController>();
    return Scaffold(
      appBar: AppBar(title: const Text('Entrar')),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const DebugInfo(),
                  const SizedBox(height: 16),
                  Form(
                    key: _formKey,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        TextFormField(
                          controller: _userCtrl,
                          decoration: const InputDecoration(
                            labelText: 'Usuário',
                          ),
                          validator: (v) => (v == null || v.isEmpty)
                              ? 'Informe o usuário'
                              : null,
                        ),
                        const SizedBox(height: 12),
                        TextFormField(
                          controller: _passCtrl,
                          decoration: const InputDecoration(labelText: 'Senha'),
                          obscureText: true,
                          validator: (v) => (v == null || v.isEmpty)
                              ? 'Informe a senha'
                              : null,
                        ),
                        const SizedBox(height: 20),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: auth.isLoading
                                ? null
                                : () async {
                                    if (!(_formKey.currentState?.validate() ??
                                        false))
                                      return;
                                    try {
                                      // Testa conexão primeiro
                                      final authService = AuthService();
                                      final isConnected = await authService
                                          .testConnection();
                                      if (!isConnected) {
                                        if (!mounted) return;
                                        ScaffoldMessenger.of(
                                          context,
                                        ).showSnackBar(
                                          const SnackBar(
                                            content: Text(
                                              'API não está acessível. Verifique se está rodando em http://localhost:8000',
                                            ),
                                            duration: Duration(seconds: 5),
                                          ),
                                        );
                                        return;
                                      }

                                      await context
                                          .read<AuthController>()
                                          .login(
                                            _userCtrl.text,
                                            _passCtrl.text,
                                          );
                                      if (!mounted) return;
                                      // Se veio de uma navegação, volta; senão vai para home
                                      if (Navigator.canPop(context)) {
                                        Navigator.pop(context);
                                      } else {
                                        Navigator.pushReplacementNamed(
                                          context,
                                          AppRoutes.home,
                                        );
                                      }
                                    } catch (e) {
                                      if (!mounted) return;
                                      String errorMessage =
                                          'Erro ao fazer login';
                                      if (e.toString().contains(
                                        'TimeoutException',
                                      )) {
                                        errorMessage =
                                            'Timeout: Verifique se a API está rodando em http://localhost:8000';
                                      } else if (e.toString().contains(
                                        'Connection refused',
                                      )) {
                                        errorMessage =
                                            'Conexão recusada: API não está rodando';
                                      } else {
                                        errorMessage = 'Erro: $e';
                                      }
                                      ScaffoldMessenger.of(
                                        context,
                                      ).showSnackBar(
                                        SnackBar(
                                          content: Text(errorMessage),
                                          duration: const Duration(seconds: 5),
                                        ),
                                      );
                                    }
                                  },
                            child: auth.isLoading
                                ? const SizedBox(
                                    height: 20,
                                    width: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                    ),
                                  )
                                : const Text('Entrar'),
                          ),
                        ),
                        const SizedBox(height: 8),
                        TextButton(
                          onPressed: auth.isLoading
                              ? null
                              : () => Navigator.pushNamed(context, '/register'),
                          child: const Text('Criar conta'),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
