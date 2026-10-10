import 'package:flutter/material.dart';
import 'package:sigilrpg/services/fights_service.dart';

class FightsView extends StatefulWidget {
  const FightsView({super.key});

  @override
  State<FightsView> createState() => _FightsViewState();
}

class _FightsViewState extends State<FightsView> {
  final _service = FightsService();
  bool _loading = true;
  String? _error;
  List<Fight> _fights = const [];
  final _opponentCtrl = TextEditingController();

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
      final fights = await _service.getUserFights();
      if (!mounted) return;
      setState(() => _fights = fights);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  void dispose() {
    _opponentCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Lutas')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _opponentCtrl,
                    decoration: const InputDecoration(
                      labelText: 'ID do Oponente',
                    ),
                    keyboardType: TextInputType.number,
                  ),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: () async {
                    final id = int.tryParse(_opponentCtrl.text.trim());
                    if (id == null) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Informe um ID válido')),
                      );
                      return;
                    }
                    try {
                      final fight = await _service.createFight(id);
                      if (!mounted) return;
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                            'Luta: ${fight.status} (+${fight.experience} XP)',
                          ),
                        ),
                      );
                      _opponentCtrl.clear();
                      await _load();
                    } catch (e) {
                      if (!mounted) return;
                      ScaffoldMessenger.of(
                        context,
                      ).showSnackBar(SnackBar(content: Text('Erro: $e')));
                    }
                  },
                  child: const Text('Lutar'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Expanded(
              child: Builder(
                builder: (context) {
                  if (_loading) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (_error != null) {
                    return Center(child: Text(_error!));
                  }
                  if (_fights.isEmpty) {
                    return const Center(child: Text('Nenhuma luta realizada.'));
                  }
                  return ListView.separated(
                    itemCount: _fights.length,
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemBuilder: (context, i) {
                      final f = _fights[i];
                      return ListTile(
                        title: Text('Status: ${f.status}'),
                        subtitle: Text(
                          'EXP: ${f.experience}  •  Oponente: ${f.opponentId}',
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
