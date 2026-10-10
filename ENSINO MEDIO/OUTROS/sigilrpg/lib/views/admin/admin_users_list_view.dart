import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/controllers/auth_controller.dart';
import 'package:sigilrpg/services/users_service.dart';

class AdminUsersListView extends StatefulWidget {
  const AdminUsersListView({super.key});

  @override
  State<AdminUsersListView> createState() => _AdminUsersListViewState();
}

class _AdminUsersListViewState extends State<AdminUsersListView> {
  final _service = UsersService();
  bool _loading = true;
  List<Map<String, dynamic>> _users = const [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final list = await _service.listUsers();
      if (!mounted) return;
      setState(() {
        _users = list;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  bool _isAdmin(BuildContext context) {
    final auth = context.read<AuthController>();
    final user = auth.user;
    if (user == null) return false;
    final id = user['id'];
    return id == 1 || id == '1';
  }

  @override
  Widget build(BuildContext context) {
    final isAdmin = _isAdmin(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Usuários (Admin)')),
      body: !isAdmin
          ? Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: const [
                    Icon(Icons.lock, size: 64, color: Colors.grey),
                    SizedBox(height: 12),
                    Text('Acesso restrito a administradores.'),
                  ],
                ),
              ),
            )
          : _loading
              ? const Center(child: CircularProgressIndicator())
              : _error != null
                  ? Center(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.error_outline, size: 48, color: Colors.redAccent),
                            const SizedBox(height: 8),
                            Text('Erro: $_error'),
                            const SizedBox(height: 12),
                            ElevatedButton.icon(
                              onPressed: _load,
                              icon: const Icon(Icons.refresh),
                              label: const Text('Tentar novamente'),
                            ),
                          ],
                        ),
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.separated(
                        padding: const EdgeInsets.all(12),
                        itemBuilder: (context, index) {
                          final u = _users[index];
                          return ListTile(
                            leading: CircleAvatar(child: Text('${u['id']}')),
                            title: Text(u['name'] ?? ''),
                            subtitle: Text(u['email'] ?? ''),
                            trailing: Text(
                              (u['created_at'] ?? '')
                                  .toString()
                                  .replaceAll('T', ' ')
                                  .split('.')
                                  .first,
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          );
                        },
                        separatorBuilder: (_, __) => const Divider(height: 1),
                        itemCount: _users.length,
                      ),
                    ),
    );
  }
}


