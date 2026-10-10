/// EXEMPLOS DE USO - VIBRAÇÃO E NOTIFICAÇÕES
/// 
/// Este arquivo contém exemplos de como usar os serviços de vibração e notificações
/// no projeto Sigil RPG. Você pode copiar e adaptar estes exemplos conforme necessário.

import 'package:sigilrpg/services/vibration_service.dart';
import 'package:sigilrpg/services/notification_service.dart';

class MobileFeaturesExamples {
  final _vibration = VibrationService();
  final _notification = NotificationService();

  /// ===== EXEMPLOS DE VIBRAÇÃO =====

  /// Exemplo 1: Vibração simples ao clicar em um botão
  void exemploVibracaoSimples() {
    _vibration.vibrate(); // Vibração padrão de 100ms
  }

  /// Exemplo 2: Vibração de feedback ao salvar personagem
  void exemploVibracaoSucesso() async {
    await _vibration.success(); // Vibração dupla de sucesso
  }

  /// Exemplo 3: Vibração de erro ao falhar ação
  void exemploVibracaoErro() async {
    await _vibration.error(); // Vibração pesada de erro
  }

  /// Exemplo 4: Vibração ao receber dano
  void exemploVibracaoDano() {
    _vibration.heavyImpact(); // Vibração forte
  }

  /// Exemplo 5: Vibração ao rolar dados críticos (20 em d20)
  void exemploVibracaoCritico() async {
    await _vibration.vibrateLong(duration: 300);
    await Future.delayed(const Duration(milliseconds: 100));
    await _vibration.vibrateLong(duration: 300);
  }

  /// ===== EXEMPLOS DE NOTIFICAÇÕES =====

  /// Exemplo 1: Notificação simples - Sessão começou
  void exemploNotificacaoSimples() async {
    await _notification.showNotification(
      id: 1,
      title: 'Sessão Iniciada!',
      body: 'A campanha começa agora!',
    );
  }

  /// Exemplo 2: Notificação quando é seu turno
  void exemploNotificacaoTurno() async {
    await _notification.notifyPlayerTurn(
      playerName: 'Gandalf',
      payload: 'turno_123',
    );
  }

  /// Exemplo 3: Notificação ao receber item
  void exemploNotificacaoItem() async {
    await _notification.notifyItemReceived(
      itemName: 'Espada Mágica +3',
      payload: 'item_456',
    );
  }

  /// Exemplo 4: Agendar notificação para lembrar sessão
  void exemploNotificacaoAgendada() async {
    final amanha = DateTime.now().add(const Duration(days: 1));
    await _notification.scheduleNotification(
      id: 10,
      title: 'Lembrete de Sessão',
      body: 'Sua sessão começa em 1 hora!',
      scheduledDate: amanha,
    );
  }

  /// Exemplo 5: Notificação periódica (diária)
  void exemploNotificacaoPeriodica() async {
    await _notification.schedulePeriodicNotification(
      id: 20,
      title: 'Hora de Jogar!',
      body: 'Que tal criar um novo personagem?',
      repeatInterval: RepeatInterval.daily,
    );
  }

  /// ===== EXEMPLO COMBINADO =====

  /// Notificação + Vibração ao vencer uma batalha
  void exemploVitoriaBatalha() async {
    // Vibração de sucesso
    await _vibration.success();
    
    // Notificação
    await _notification.showNotification(
      id: 100,
      title: 'Vitória!',
      body: 'Você derrotou o dragão!',
      payload: 'vitoria_123',
    );
  }

  /// Notificação + Vibração de erro ao falhar
  void exemploFalhaAcao() async {
    // Vibração de erro
    await _vibration.error();
    
    // Notificação
    await _notification.showNotification(
      id: 101,
      title: 'Ação Falhou',
      body: 'Você não conseguiu usar a habilidade.',
      payload: 'falha_456',
    );
  }
}

/// ===== COMO USAR EM SEU CÓDIGO =====
/// 
/// 1. VIBRAÇÃO:
///    ```dart
///    // Simples
///    VibrationService().vibrate();
///    
///    // Sucesso
///    await VibrationService().success();
///    
///    // Erro
///    await VibrationService().error();
///    ```
/// 
/// 2. NOTIFICAÇÕES:
///    ```dart
///    // Notificação imediata
///    await NotificationService().showNotification(
///      id: 1,
///      title: 'Título',
///      body: 'Corpo da mensagem',
///    );
///    
///    // Notificação agendada
///    await NotificationService().scheduleNotification(
///      id: 2,
///      title: 'Lembrete',
///      body: 'Mensagem',
///      scheduledDate: DateTime.now().add(Duration(hours: 1)),
///    );
///    ```
/// 
/// 3. INTEGRAÇÃO EM CONTROLLERS/SERVICES:
///    Adicione vibração em ações importantes como:
///    - Salvar personagem
///    - Vencer combate
///    - Receber dano
///    - Rolar dados críticos
///    
///    Adicione notificações para:
///    - Início de sessão
///    - Turno do jogador
///    - Novos itens recebidos
///    - Lembretes de eventos
