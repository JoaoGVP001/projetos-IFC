import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/constants/app_routes.dart';
import 'package:sigilrpg/controllers/auth_controller.dart';
import 'package:sigilrpg/config/api_config.dart';

class LoginView extends StatefulWidget {
  const LoginView({super.key});

  @override
  State<LoginView> createState() => _LoginViewState();
}

class _LoginViewState extends State<LoginView> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _submitting = false;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthController>();
    return Scaffold(
      appBar: AppBar(title: const Text('Entrar')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              // Informação de debug sobre a URL da API
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue.withOpacity(0.3)),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline, size: 20, color: Colors.blue[700]),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Conectando em: ${ApiConfig.baseUrl}',
                        style: TextStyle(fontSize: 12, color: Colors.blue[900]),
                      ),
                    ),
                  ],
                ),
              ),
              TextFormField(
                controller: _emailCtrl,
                decoration: const InputDecoration(labelText: 'E-mail'),
                validator: (v) => (v == null || v.trim().isEmpty)
                    ? 'Informe seu e-mail'
                    : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _passwordCtrl,
                obscureText: true,
                decoration: const InputDecoration(labelText: 'Senha'),
                validator: (v) => (v == null || v.trim().isEmpty)
                    ? 'Informe sua senha'
                    : null,
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _submitting
                          ? null
                          : () async {
                              if (!(_formKey.currentState?.validate() ??
                                  false)) {
                                return;
                              }
                              setState(() => _submitting = true);
                              try {
                                await auth.login(
                                  _emailCtrl.text.trim(),
                                  _passwordCtrl.text.trim(),
                                );
                                if (!mounted) return;
                                Navigator.pop(context);
                              } catch (e) {
                                if (!mounted) return;
                                String errorMessage = 'Falha no login';
                                if (e.toString().contains('conectar') || 
                                    e.toString().contains('timeout') ||
                                    e.toString().contains('SocketException')) {
                                  errorMessage = 'Erro de conexão:\n'
                                      'Verifique se a API está rodando e se o celular está na mesma rede Wi-Fi do notebook.';
                                } else if (e.toString().contains('401') || 
                                          e.toString().contains('credenciais')) {
                                  errorMessage = 'E-mail ou senha incorretos';
                                } else {
                                  errorMessage = 'Erro: ${e.toString().replaceAll('HttpException(', '').replaceAll(')', '')}';
                                }
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text(errorMessage),
                                    duration: const Duration(seconds: 5),
                                    backgroundColor: Colors.red,
                                  ),
                                );
                              } finally {
                                if (mounted)
                                  setState(() => _submitting = false);
                              }
                            },
                      child: _submitting
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Entrar'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              TextButton(
                onPressed: () =>
                    Navigator.pushNamed(context, AppRoutes.register),
                child: const Text('Não tem conta? Registre-se'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
