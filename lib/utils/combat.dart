import 'package:sigilrpg/models/character.dart';

class CombatCalculator {
  static int calculateMaxPV(Character c) {
    // Assumido: PV base 10 + 5*VIG + 2*FOR
    return 10 + (c.attributes.vigor * 5) + (c.attributes.forca * 2);
  }

  static int calculateMaxPE(Character c) {
    // Assumido: PE base 6 + 4*INT + 2*PRE
    return 6 + (c.attributes.intelecto * 4) + (c.attributes.presenca * 2);
    }

  static int calculateMaxPS(Character c) {
    // Assumido: PS base 8 + 3*INT + 3*PRE
    return 8 + (c.attributes.intelecto * 3) + (c.attributes.presenca * 3);
  }

  static int calculateDefense(Character c) {
    // Defesa já exibida como 10 + AGI
    return 10 + c.attributes.agilidade;
  }

  static int resistanceFisica(Character c) => c.attributes.vigor;
  static int resistanceBalistica(Character c) => c.attributes.vigor;
  static int resistanceMental(Character c) => c.attributes.intelecto;
}




