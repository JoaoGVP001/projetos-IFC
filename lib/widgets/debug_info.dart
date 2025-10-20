import 'package:flutter/material.dart';
import 'package:sigilrpg/services/auth_service.dart';

class DebugInfo extends StatelessWidget {
  const DebugInfo({super.key});

  @override
  Widget build(BuildContext context) {
    final authService = AuthService();
    return Container(
      padding: const EdgeInsets.all(8),
      margin: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.orange.withOpacity(0.1),
        border: Border.all(color: Colors.orange),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text(
            '🔧 Debug Info',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text('API URL: ${authService.baseUrl}'),
          const SizedBox(height: 4),
          const Text(
            'Certifique-se de que a API está rodando:',
            style: TextStyle(fontSize: 12),
          ),
          const Text(
            'python -m uvicorn app.main:app --reload',
            style: TextStyle(fontSize: 12, fontFamily: 'monospace'),
          ),
        ],
      ),
    );
  }
}
