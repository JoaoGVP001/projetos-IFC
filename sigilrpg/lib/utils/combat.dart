import 'package:sigilrpg/models/character.dart';

class CombatCalculator {
  static int calculateMaxPV(Character c) {
    // PV base 10 + 5*VIG + 2*FOR
    return 10 + (c.attributes.vigor * 5) + (c.attributes.forca * 2);
  }

  static int calculateMaxPE(Character c) {
    // PE base 6 + 4*INT + 2*PRE
    return 6 + (c.attributes.intelecto * 4) + (c.attributes.presenca * 2);
  }

  static int calculateMaxPS(Character c) {
    // PS base 8 + 3*INT + 3*PRE
    return 8 + (c.attributes.intelecto * 3) + (c.attributes.presenca * 3);
  }

  static int calculateDefense(Character c) {
    // Defesa: 10 + AGI
    return 10 + c.attributes.agilidade;
  }

  static int resistanceFisica(Character c) => c.attributes.vigor;
  static int resistanceBalistica(Character c) => c.attributes.vigor;
  static int resistanceMental(Character c) => c.attributes.intelecto;
  
  // Obter valores atuais (ou máximo se não definido)
  static int getCurrentPV(Character c) {
    return c.currentPv ?? calculateMaxPV(c);
  }
  
  static int getCurrentPE(Character c) {
    return c.currentPe ?? calculateMaxPE(c);
  }
  
  static int getCurrentPS(Character c) {
    return c.currentPs ?? calculateMaxPS(c);
  }
  
  // Funções para modificar valores
  static int addPV(Character c, int amount) {
    final current = getCurrentPV(c);
    final max = calculateMaxPV(c);
    return (current + amount).clamp(0, max);
  }
  
  static int subtractPV(Character c, int amount) {
    final current = getCurrentPV(c);
    return (current - amount).clamp(0, calculateMaxPV(c));
  }
  
  static int addPE(Character c, int amount) {
    final current = getCurrentPE(c);
    final max = calculateMaxPE(c);
    return (current + amount).clamp(0, max);
  }
  
  static int subtractPE(Character c, int amount) {
    final current = getCurrentPE(c);
    return (current - amount).clamp(0, calculateMaxPE(c));
  }
  
  static int addPS(Character c, int amount) {
    final current = getCurrentPS(c);
    final max = calculateMaxPS(c);
    return (current + amount).clamp(0, max);
  }
  
  static int subtractPS(Character c, int amount) {
    final current = getCurrentPS(c);
    return (current - amount).clamp(0, calculateMaxPS(c));
  }
}




