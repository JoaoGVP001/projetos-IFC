import 'package:permission_handler/permission_handler.dart';
import 'package:flutter/foundation.dart';

/// Serviço para gerenciar permissões do app
class PermissionService {
  static final PermissionService _instance = PermissionService._internal();
  factory PermissionService() => _instance;
  PermissionService._internal();

  /// Solicita todas as permissões necessárias para o app funcionar
  Future<Map<Permission, PermissionStatus>> requestAllPermissions() async {
    if (defaultTargetPlatform != TargetPlatform.android) {
      // iOS e outros não precisam de permissões especiais (já são gerenciadas pelo sistema)
      return {};
    }

    // Lista de permissões necessárias
    final permissions = [
      Permission.notification, // Para notificações (Android 13+)
      // VIBRATE não precisa de permissão em runtime (já declarada no manifest)
    ];

    // Solicitar todas as permissões
    final statuses = await permissions.request();
    return statuses;
  }

  /// Verifica se todas as permissões necessárias foram concedidas
  Future<bool> hasAllPermissions() async {
    if (defaultTargetPlatform != TargetPlatform.android) {
      return true;
    }

    // Verificar permissão de notificação (Android 13+)
    final notificationStatus = await Permission.notification.status;
    
    // VIBRATE não precisa verificação em runtime
    return notificationStatus.isGranted;
  }

  /// Verifica e solicita permissões se necessário
  /// Retorna true se todas as permissões foram concedidas
  Future<bool> ensurePermissions() async {
    if (await hasAllPermissions()) {
      return true;
    }

    final statuses = await requestAllPermissions();
    
    // Verificar se todas foram concedidas
    final notificationStatus = statuses[Permission.notification];
    return notificationStatus?.isGranted ?? false;
  }

  /// Verifica status de uma permissão específica
  Future<PermissionStatus> checkPermission(Permission permission) async {
    return await permission.status;
  }
}

