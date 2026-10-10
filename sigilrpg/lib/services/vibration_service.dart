import 'package:vibration/vibration.dart';
import 'package:flutter/services.dart';

/// Serviço para gerenciar vibração no dispositivo móvel
class VibrationService {
  static final VibrationService _instance = VibrationService._internal();
  factory VibrationService() => _instance;
  VibrationService._internal();

  bool? _hasVibrator;

  /// Verifica se o dispositivo possui vibrador
  Future<bool> hasVibrator() async {
    if (_hasVibrator != null) return _hasVibrator!;
    _hasVibrator = await Vibration.hasVibrator() ?? false;
    return _hasVibrator!;
  }

  /// Vibração padrão (curta)
  Future<void> vibrate({int duration = 100}) async {
    if (await hasVibrator()) {
      if (await Vibration.hasAmplitudeControl() ?? false) {
        await Vibration.vibrate(duration: duration);
      } else {
        await Vibration.vibrate();
      }
    }
  }

  /// Vibração longa
  Future<void> vibrateLong({int duration = 500}) async {
    if (await hasVibrator()) {
      await vibrate(duration: duration);
    }
  }

  /// Vibração com padrão personalizado
  /// Exemplo: [0, 100, 200, 100] = espera 0ms, vibra 100ms, espera 200ms, vibra 100ms
  Future<void> vibratePattern(List<int> pattern) async {
    if (await hasVibrator()) {
      await Vibration.vibrate(pattern: pattern, repeat: -1);
    }
  }

  /// Vibração de feedback leve (HapticFeedback)
  void lightImpact() {
    HapticFeedback.lightImpact();
  }

  /// Vibração de feedback médio (HapticFeedback)
  void mediumImpact() {
    HapticFeedback.mediumImpact();
  }

  /// Vibração de feedback pesado (HapticFeedback)
  void heavyImpact() {
    HapticFeedback.heavyImpact();
  }

  /// Vibração de seleção (HapticFeedback)
  void selectionClick() {
    HapticFeedback.selectionClick();
  }

  /// Vibração de confirmação (sucesso)
  Future<void> success() async {
    lightImpact();
    await Future.delayed(const Duration(milliseconds: 50));
    lightImpact();
  }

  /// Vibração de erro
  Future<void> error() async {
    heavyImpact();
  }

  /// Vibração de atenção (alerta)
  Future<void> warning() async {
    mediumImpact();
    await Future.delayed(const Duration(milliseconds: 100));
    mediumImpact();
  }

  /// Cancela qualquer vibração em andamento
  Future<void> cancel() async {
    if (await hasVibrator()) {
      await Vibration.cancel();
    }
  }
}

