import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:flutter/foundation.dart';

/// Serviço para gerenciar notificações locais
class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _notifications =
      FlutterLocalNotificationsPlugin();
  
  bool _isInitialized = false;

  /// Inicializa o serviço de notificações
  Future<bool> initialize() async {
    if (_isInitialized) return true;

    // Configuração Android
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    
    // Configuração iOS
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    final initialized = await _notifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );

    if (initialized ?? false) {
      _isInitialized = true;
      // Solicita permissões no Android 13+
      await requestPermissions();
    }

    return initialized ?? false;
  }

  /// Callback quando uma notificação é tocada
  void _onNotificationTapped(NotificationResponse response) {
    debugPrint('Notificação tocada: ${response.id} - ${response.payload}');
    // Aqui você pode adicionar navegação ou outras ações
  }

  /// Solicita permissões necessárias (Android 13+)
  Future<bool> requestPermissions() async {
    if (defaultTargetPlatform != TargetPlatform.android) return true;

    final status = await Permission.notification.request();
    return status.isGranted;
  }

  /// Verifica se as permissões foram concedidas
  Future<bool> hasPermission() async {
    if (defaultTargetPlatform != TargetPlatform.android) return true;
    final status = await Permission.notification.status;
    return status.isGranted;
  }

  /// Mostra uma notificação simples
  Future<void> showNotification({
    required int id,
    required String title,
    required String body,
    String? payload,
  }) async {
    if (!_isInitialized) {
      await initialize();
    }

    // Verifica permissão antes de mostrar
    if (!await hasPermission()) {
      await requestPermissions();
    }

    const androidDetails = AndroidNotificationDetails(
      'sigil_rpg_channel',
      'Sigil RPG Notificações',
      channelDescription: 'Notificações do jogo Sigil RPG',
      importance: Importance.high,
      priority: Priority.high,
      showWhen: true,
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _notifications.show(
      id,
      title,
      body,
      details,
      payload: payload,
    );
  }

  /// Mostra uma notificação com ações personalizadas
  Future<void> showNotificationWithActions({
    required int id,
    required String title,
    required String body,
    String? payload,
    List<AndroidNotificationAction>? actions,
  }) async {
    if (!_isInitialized) {
      await initialize();
    }

    final androidDetails = AndroidNotificationDetails(
      'sigil_rpg_channel',
      'Sigil RPG Notificações',
      channelDescription: 'Notificações do jogo Sigil RPG',
      importance: Importance.high,
      priority: Priority.high,
      showWhen: true,
      actions: actions,
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _notifications.show(
      id,
      title,
      body,
      details,
      payload: payload,
    );
  }

  /// Agenda uma notificação para um horário específico
  Future<void> scheduleNotification({
    required int id,
    required String title,
    required String body,
    required DateTime scheduledDate,
    String? payload,
  }) async {
    if (!_isInitialized) {
      await initialize();
    }

    const androidDetails = AndroidNotificationDetails(
      'sigil_rpg_channel',
      'Sigil RPG Notificações',
      channelDescription: 'Notificações do jogo Sigil RPG',
      importance: Importance.high,
      priority: Priority.high,
    );

    const iosDetails = DarwinNotificationDetails();

    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _notifications.zonedSchedule(
      id,
      title,
      body,
      _convertToTZDateTime(scheduledDate),
      details,
      payload: payload,
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
    );
  }

  /// Agenda uma notificação periódica
  Future<void> schedulePeriodicNotification({
    required int id,
    required String title,
    required String body,
    required RepeatInterval repeatInterval,
    String? payload,
  }) async {
    if (!_isInitialized) {
      await initialize();
    }

    const androidDetails = AndroidNotificationDetails(
      'sigil_rpg_channel',
      'Sigil RPG Notificações',
      channelDescription: 'Notificações do jogo Sigil RPG',
      importance: Importance.high,
      priority: Priority.high,
    );

    const iosDetails = DarwinNotificationDetails();

    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _notifications.periodicallyShow(
      id,
      title,
      body,
      repeatInterval,
      details,
      payload: payload,
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
    );
  }

  /// Cancela uma notificação específica
  Future<void> cancelNotification(int id) async {
    await _notifications.cancel(id);
  }

  /// Cancela todas as notificações
  Future<void> cancelAllNotifications() async {
    await _notifications.cancelAll();
  }

  /// Converte DateTime para TZDateTime (necessário para agendamento)
  dynamic _convertToTZDateTime(DateTime dateTime) {
    // Para simplificar, retornamos DateTime
    // Em produção, considere usar o pacote timezone
    return dateTime;
  }

  /// Notificação de exemplo - Sessão iniciada
  Future<void> notifySessionStarted({
    required String campaignName,
    String? payload,
  }) async {
    await showNotification(
      id: 1001,
      title: 'Sessão Iniciada',
      body: 'A sessão de $campaignName começou!',
      payload: payload,
    );
  }

  /// Notificação de exemplo - Turno do jogador
  Future<void> notifyPlayerTurn({
    required String playerName,
    String? payload,
  }) async {
    await showNotification(
      id: 1002,
      title: 'Seu Turno!',
      body: 'É a vez de $playerName agir',
      payload: payload,
    );
  }

  /// Notificação de exemplo - Novo item recebido
  Future<void> notifyItemReceived({
    required String itemName,
    String? payload,
  }) async {
    await showNotification(
      id: 1003,
      title: 'Novo Item!',
      body: 'Você recebeu: $itemName',
      payload: payload,
    );
  }
}

