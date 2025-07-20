import 'package:flame/components.dart';
import 'package:flame/events.dart';
import 'package:flame/game.dart';
import 'package:flutter/material.dart';
import 'dart:math';
import 'dart:io';
import 'package:flutter/services.dart';

void main() {
  runApp(
    GameWidget(
      game: DodgeObstaclesGame(),
      overlayBuilderMap: {
        'MainMenu': (context, DodgeObstaclesGame game) => MainMenuOverlay(game: game),
        'Guide': (context, DodgeObstaclesGame game) => GuideOverlay(game: game),
        'GameOver': (context, DodgeObstaclesGame game) => GameOverOverlay(game: game),
        'PauseMenu': (context, DodgeObstaclesGame game) => PauseMenuOverlay(game: game),
        'Status': (context, DodgeObstaclesGame game) => StatusOverlay(game: game),
        'Choice': (context, DodgeObstaclesGame game) => ChoiceOverlay(game: game),
        'ConfirmChoice': (context, DodgeObstaclesGame game) => ConfirmChoiceOverlay(game: game),
        'PlayerStats': (context, DodgeObstaclesGame game) => PlayerStatsOverlay(game: game),
        'UpgradeIcons': (context, DodgeObstaclesGame game) => UpgradeIconsOverlay(game: game),
      },
    ),
  );
}

class DodgeObstaclesGame extends FlameGame with HasKeyboardHandlerComponents, TapDetector {
  late PlayerCircle player;
  final Random random = Random();
  bool gameOver = false;
  int wave = 1;
  int obstaclesToAdd = 3;
  late TextComponent waveText;
  int playerLife = 100;
  late TextComponent playerLifeText;
  bool paused = false;
  bool mousePressed = false;
  Vector2? lastMouseDirection;
  late TextComponent playerLevelText;
  bool choicePending = false;
  List<String> currentChoices = [];
  String? selectedChoice;
  int? selectedChoiceIndex;
  List<DamageMessage> damageMessages = [];
  void showChoices() {
    paused = true;
    choicePending = true;
    // Exemplo de tipos de escolhas possíveis (substitua depois)
    List<String> allChoices = [
      'Força de Sobrevivencia',
      'Recuperação Pós Wave',
      'Tanque de Guerra',
      'Mira Tática',
      'Projétil Vampírico',
      'Escudo de Impacto',
      'Combo de Tiros',
      'Golpe Decisivo',
    ];
    allChoices.shuffle();
    currentChoices = allChoices.take(3).toList();
    overlays.add('Choice');
  }
  void pickChoice(int idx) {
    selectedChoice = currentChoices[idx];
    selectedChoiceIndex = idx;
    overlays.remove('Choice');
    overlays.add('ConfirmChoice');
  }
  void confirmChoice() {
    if (selectedChoice == null || selectedChoiceIndex == null) return;
    
    String choice = selectedChoice!;
    if (choice == 'Tanque de Guerra') {
      tankUpgrades++;
      double extra = player.maxLife * 0.05;
      player.maxLife += extra.round();
      player.life = player.maxLife;
      playerLife = player.maxLife;
      updatePlayerLifeText();
    } else if (choice == 'Recuperação Pós Wave') {
      recoveryUpgrades++;
    } else if (choice == 'Força de Sobrevivencia') {
      survivalUpgrades++;
      lastSurvivalLife = player.life;
    } else if (choice == 'Mira Tática') {
      tacticalSightUpgrades++;
    } else if (choice == 'Projétil Vampírico') {
      vampiricBulletUpgrades++;
    } else if (choice == 'Escudo de Impacto') {
      impactShieldUpgrades++;
    } else if (choice == 'Combo de Tiros') {
      comboShotUpgrades++;
    } else if (choice == 'Golpe Decisivo') {
      decisiveBlowUpgrades++;
    }
    
    overlays.remove('ConfirmChoice');
    paused = false;
    choicePending = false;
    selectedChoice = null;
    selectedChoiceIndex = null;
  }
  void cancelChoice() {
    overlays.remove('ConfirmChoice');
    overlays.add('Choice');
    selectedChoice = null;
    selectedChoiceIndex = null;
  }

  // Controle de teclas pressionadas
  final Set<LogicalKeyboardKey> _pressedKeys = {};
  Vector2 lastMoveDirection = Vector2(0, -1); // Começa para cima
  double bulletCooldown = 0.0;
  final double bulletInterval = 0.25; // 2 tiros por segundo
  double timer = 0.0;

  // Upgrades ativos
  int tankUpgrades = 0;
  int recoveryUpgrades = 0;
  int survivalUpgrades = 0;
  double survivalBuffEnd = 0.0;
  double survivalBuffPercent = 0.0;
  int lastSurvivalLife = 0;
  int tacticalSightUpgrades = 0;
  int vampiricBulletUpgrades = 0;
  int impactShieldUpgrades = 0;
  double impactShieldLast = -10.0;
  int comboShotUpgrades = 0;
  int decisiveBlowUpgrades = 0;
  int comboHitCount = 0;

  // Overlay de status
  void openStatus() {
    paused = true;
    overlays.add('Status');
  }
  void closeStatus() {
    paused = false;
    overlays.remove('Status');
  }

  void openPlayerStats() {
    if (!gameOver && !paused) {
      paused = true;
      overlays.add('PlayerStats');
    }
  }
  void closePlayerStats() {
    paused = false;
    overlays.remove('PlayerStats');
  }

  @override
  Future<void> onLoad() async {
    super.onLoad();
    overlays.add('MainMenu');
    // Criar apenas os componentes de texto, mas não inicializar o jogo
    waveText = TextComponent(
      text: 'Wave 1',
      position: Vector2(20, 20),
      anchor: Anchor.topLeft,
      textRenderer: TextPaint(
        style: const TextStyle(
          color: Colors.white,
          fontSize: 32,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
    add(waveText);
    playerLifeText = TextComponent(
      text: 'Vida: 100',
      position: Vector2(20, 60),
      anchor: Anchor.topLeft,
      textRenderer: TextPaint(
        style: const TextStyle(
          color: Colors.white,
          fontSize: 28,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
    add(playerLifeText);
    playerLevelText = TextComponent(
      text: 'Nível: 1',
      position: Vector2(size.x - 20, 20),
      anchor: Anchor.topRight,
      textRenderer: TextPaint(
        style: const TextStyle(
          color: Colors.amber,
          fontSize: 32,
          fontWeight: FontWeight.bold,
          shadows: [Shadow(blurRadius: 2, color: Colors.black, offset: Offset(1,1))],
        ),
      ),
    );
    add(playerLevelText);
    overlays.add('UpgradeIcons');
    // Não inicializar o jogo aqui - apenas mostrar o menu
    gameOver = true; // Impedir que o jogo funcione até clicar em "COMEÇAR JOGO"
  }

  void startGame() {
    overlays.remove('MainMenu');
    gameOver = false;
    overlays.remove('GameOver');
    overlays.remove('Status');
    // Resetar todas as variáveis de estado
    wave = 1;
    obstaclesToAdd = 3;
    playerLife = 100;
    bulletCooldown = 0.0;
    timer = 0.0;
    paused = false;
    choicePending = false;
    mousePressed = false;
    lastMouseDirection = null;
    comboHitCount = 0;
    survivalBuffPercent = 0.0;
    lastSurvivalLife = 100;
    // Resetar upgrades (opcional - remover se quiser manter upgrades entre jogos)
    tankUpgrades = 0;
    recoveryUpgrades = 0;
    survivalUpgrades = 0;
    tacticalSightUpgrades = 0;
    vampiricBulletUpgrades = 0;
    impactShieldUpgrades = 0;
    comboShotUpgrades = 0;
    decisiveBlowUpgrades = 0;
    impactShieldLast = -10.0;
    survivalBuffEnd = 0.0;
    damageMessages.clear(); // Limpar mensagens de dano
    removeAll(children.where((c) => c is! TextComponent).toList());
    player = PlayerCircle(position: size / 2);
    player.life = playerLife;
    player.level = 1;
    player.xp = 0;
    player.xpToNextLevel = 100;
    player.statusPoints = 5; // Começa com 5 pontos de status
    player.statusHaki = 0;
    player.statusAkuma = 0;
    player.statusVida = 0;
    player.statusArmas = 0;
    player.statusStamina = 0;
    add(player);
    player.applyStatusEffects();
    // Garantir que os obstáculos sejam criados
    for (int i = 0; i < obstaclesToAdd; i++) {
      spawnObstacle();
    }
    updateWaveText();
    updatePlayerLifeText();
    updatePlayerLevelText();
    lastMoveDirection = Vector2(0, -1);
  }

  void nextWave() {
    wave++;
    obstaclesToAdd += 2;
    for (int i = 0; i < obstaclesToAdd; i++) {
      spawnObstacle();
    }
    updateWaveText();
    // Recuperação Pós Wave
    if (recoveryUpgrades > 0) {
      int lost = player.maxLife - player.life;
      if (lost > 0) {
        int heal = (lost * 0.05 * recoveryUpgrades).round();
        player.life += heal;
        playerLife = player.life;
        if (player.life > player.maxLife) player.life = player.maxLife;
        updatePlayerLifeText();
      }
    }
    // A cada 3 waves, mostrar tela de escolhas
    if (wave % 3 == 0) {
      showChoices();
    }
  }

  void updateWaveText() {
    waveText.text = 'Wave $wave';
  }
  void updatePlayerLifeText() {
    playerLifeText.text = 'Vida: $playerLife/${player.maxLife}';
  }
  void updatePlayerLevelText() {
    playerLevelText.text = 'Nível: ${player.level}';
  }

  @override
  void render(Canvas canvas) {
    super.render(canvas);
    
    // Renderizar mensagens de dano
    final currentTime = DateTime.now().millisecondsSinceEpoch / 1000;
    for (final message in damageMessages) {
      final elapsed = currentTime - message.startTime;
      final alpha = (1.0 - (elapsed / message.duration)).clamp(0.0, 1.0);
      
      // Posição com movimento para cima
      final yOffset = elapsed * 30; // Move 30 pixels por segundo
      final position = Vector2(message.position.x, message.position.y - yOffset);
      
      // Animação de bounce/zoom
      double scale = 1.0;
      if (elapsed < 0.15) {
        // Zoom in rápido no início (0 a 0.15s)
        scale = 1.0 + (1.5 * (1.0 - elapsed / 0.15));
      } else if (elapsed < 0.3) {
        // Bounce pequeno (0.15s a 0.3s)
        final bounceProgress = (elapsed - 0.15) / 0.15;
        scale = 1.0 + (0.2 * sin(bounceProgress * pi));
      }
      
      // Configurar o texto
      final baseSize = message.isCritical ? 32.0 : 20.0;
      final textStyle = TextStyle(
        fontSize: baseSize * scale,
        fontWeight: FontWeight.bold,
        color: message.text.startsWith('SANGUE') 
          ? Colors.red.withOpacity(alpha)
          : message.isCritical 
            ? Colors.orange.withOpacity(alpha)
            : Colors.white.withOpacity(alpha),
        shadows: [
          // Sombra base
          Shadow(
            blurRadius: 3,
            color: Colors.black.withOpacity(alpha),
            offset: const Offset(1, 1),
          ),
          // Glow para críticos
          if (message.isCritical) ...[
            Shadow(
              blurRadius: 8,
              color: Colors.orange.withOpacity(alpha * 0.7),
              offset: const Offset(-1, -1),
            ),
            Shadow(
              blurRadius: 8,
              color: Colors.orange.withOpacity(alpha * 0.7),
              offset: const Offset(1, -1),
            ),
            Shadow(
              blurRadius: 8,
              color: Colors.orange.withOpacity(alpha * 0.7),
              offset: const Offset(-1, 1),
            ),
            Shadow(
              blurRadius: 8,
              color: Colors.orange.withOpacity(alpha * 0.7),
              offset: const Offset(1, 1),
            ),
            // Glow central mais intenso
            Shadow(
              blurRadius: 12,
              color: Colors.orange.withOpacity(alpha * 0.8),
              offset: const Offset(0, 0),
            ),
          ],
        ],
      );
      
      final textPainter = TextPainter(
        text: TextSpan(text: message.text, style: textStyle),
        textDirection: TextDirection.ltr,
      )..layout();
      
      // Centralizar o texto na posição
      final textPosition = Offset(
        position.x - textPainter.width / 2,
        position.y - textPainter.height / 2,
      );
      
      textPainter.paint(canvas, textPosition);
    }
  }

  void spawnObstacle() {
    double angle = random.nextDouble() * 2 * pi;
    double distance = size.x > size.y ? size.x / 2 : size.y / 2;
    Vector2 start = size / 2 + Vector2(cos(angle), sin(angle)) * distance;
    Vector2 direction = (size / 2 - start).normalized();
    ObstacleCircle obstacle = ObstacleCircle(
      position: start,
      direction: direction,
      speed: 100 + random.nextDouble() * 100,
    );
    add(obstacle);
  }

  @override
  void update(double dt) {
    super.update(dt);
    timer += dt;
    final game = findGame() as DodgeObstaclesGame?;
    if (game != null && game.paused) return;
    if (gameOver || paused) return;
    // Força de Sobrevivência: verifica vida perdida
    if (survivalUpgrades > 0) {
      int lost = lastSurvivalLife - player.life;
      if (lost >= 50) {
        survivalBuffPercent += 0.05 * survivalUpgrades;
        survivalBuffEnd = timer + 10.0;
        lastSurvivalLife = player.life;
      }
      // Remove buff se tempo acabar
      if (survivalBuffPercent > 0 && timer > survivalBuffEnd) {
        survivalBuffPercent = 0.0;
      }
    }
    // Disparo contínuo com mouse pressionado
    if (mousePressed && lastMouseDirection != null) {
      if (bulletCooldown <= 0.0) {
        final critChance = tacticalSightUpgrades > 0 ? (player.statusArmas ~/ 2) * 0.05 * tacticalSightUpgrades : 0.0;
        bool isCrit;
        if (comboShotUpgrades > 0 && comboHitCount == 3) {
          isCrit = true;
        } else {
          isCrit = critChance > 0 && (random.nextDouble() < critChance);
        }
        final isVamp = vampiricBulletUpgrades > 0;
        int baseDmg = player.bulletDamage;
        int dmg = isCrit ? baseDmg * 2 : baseDmg;
        int vampAmount = isVamp ? (dmg * 0.1 * vampiricBulletUpgrades).round() : 0;
        add(BulletComponent(
          position: player.position.clone(),
          direction: lastMouseDirection!,
          damage: dmg,
          isCrit: isCrit,
          isVampiric: isVamp,
          vampiricAmount: vampAmount,
        ));
        bulletCooldown = bulletInterval;
      }
    }
    if (bulletCooldown > 0.0) {
      bulletCooldown -= dt;
    }
    // Movimento do player com WASD/setas
    const double speed = 250; // pixels por segundo
    Vector2 move = Vector2.zero();
    if (_pressedKeys.contains(LogicalKeyboardKey.keyW) || _pressedKeys.contains(LogicalKeyboardKey.arrowUp)) {
      move.y -= 1;
    }
    if (_pressedKeys.contains(LogicalKeyboardKey.keyS) || _pressedKeys.contains(LogicalKeyboardKey.arrowDown)) {
      move.y += 1;
    }
    if (_pressedKeys.contains(LogicalKeyboardKey.keyA) || _pressedKeys.contains(LogicalKeyboardKey.arrowLeft)) {
      move.x -= 1;
    }
    if (_pressedKeys.contains(LogicalKeyboardKey.keyD) || _pressedKeys.contains(LogicalKeyboardKey.arrowRight)) {
      move.x += 1;
    }
    if (move.length > 0) {
      move.normalize();
      player.position += move * speed * dt;
      // Limitar dentro da tela
      player.position.x = player.position.x.clamp(player.radius, size.x - player.radius);
      player.position.y = player.position.y.clamp(player.radius, size.y - player.radius);
      lastMoveDirection = move.clone();
    }
    // Checa colisão do player com obstáculos
    for (final obstacle in children.whereType<ObstacleCircle>()) {
      if (player.position.distanceTo(obstacle.position) <
          player.radius + obstacle.radius) {
        if (obstacle.attackCooldown <= 0) {
          int damage = 2;
          // Aplica buff de resistência
          if (survivalBuffPercent > 0) {
            damage = (damage * (1 - survivalBuffPercent)).round();
            if (damage < 1) damage = 1;
          }
          playerLife -= damage;
          player.life = playerLife;
          if (playerLife > player.maxLife) playerLife = player.maxLife;
          updatePlayerLifeText();
          obstacle.attackCooldown = ObstacleCircle.attackInterval;
          // Knockback: empurra o obstáculo para fora do player
          final toObstacle = (obstacle.position - player.position);
          final minDist = player.radius + obstacle.radius;
          final dist = toObstacle.length;
          final knockbackDir = dist > 0 ? toObstacle.normalized() : Vector2(1, 0);
          // Move para a borda exata (sem sobreposição)
          obstacle.position = player.position + knockbackDir * minDist;
          // Aplica knockback extra
          const double knockbackForce = 40;
          obstacle.position += knockbackDir * knockbackForce;
          // Escudo de Impacto
          if (impactShieldUpgrades > 0 && timer - impactShieldLast > 5.0) {
            for (final o in children.whereType<ObstacleCircle>()) {
              if (o != obstacle && o.position.distanceTo(player.position) < 180) {
                o.vida -= 10 * impactShieldUpgrades;
                if (o.vida < 0) o.vida = 0;
              }
            }
            impactShieldLast = timer;
          }
          if (playerLife <= 0) {
            gameOver = true;
            overlays.add('GameOver');
            break;
          }
        }
      }
    }
    // Checa colisão dos tiros com obstáculos
    final bullets = children.whereType<BulletComponent>().toList();
    final obstacles = children.whereType<ObstacleCircle>().toList();
    for (final bullet in bullets) {
      for (final obstacle in obstacles) {
        if (bullet.position.distanceTo(obstacle.position) < bullet.radius + obstacle.radius) {
          obstacle.vida -= bullet.damage;
          
          // Criar mensagem de dano
          final currentTime = DateTime.now().millisecondsSinceEpoch / 1000;
          final damageText = bullet.isCrit ? '${bullet.damage}!' : '${bullet.damage}';
          damageMessages.add(DamageMessage(
            damageText,
            obstacle.position.clone(),
            currentTime,
            bullet.isCrit,
          ));
          
          // Projétil Vampírico: cura o player
          if (bullet.isVampiric && bullet.vampiricAmount > 0) {
            player.life += bullet.vampiricAmount;
            playerLife = player.life;
            if (player.life > player.maxLife) player.life = player.maxLife;
            updatePlayerLifeText();
          }
          // Golpe Decisivo: críticos causam sangramento
          if (decisiveBlowUpgrades > 0 && bullet.isCrit) {
            obstacle.bleedTime = 3.0;
            obstacle.bleedDamage = 5 * decisiveBlowUpgrades;
            
            // Criar mensagem de sangramento aplicado
            final currentTime = DateTime.now().millisecondsSinceEpoch / 1000;
            damageMessages.add(DamageMessage(
              'SANGUE!',
              obstacle.position.clone(),
              currentTime,
              false,
            ));
          }
          bullet.removeFromParent();
          if (obstacle.vida <= 0) {
            obstacle.removeFromParent();
            bool up = player.addXp(10); // Ganha 10 XP por obstáculo eliminado
            if (up) {
              updatePlayerLevelText();
            }
          }
          // Combo de Tiros: contar acertos
          if (comboShotUpgrades > 0) {
            comboHitCount++;
            if (comboHitCount == 4) comboHitCount = 1; // Mantém 1 para o próximo ciclo
          }
          break; // Um tiro só acerta um obstáculo
        }
      }
    }
    // Limpar mensagens de dano expiradas
    damageMessages.removeWhere((msg) => msg.isExpired);
    
    // Avança wave apenas quando não há obstáculos
    if (children.whereType<ObstacleCircle>().isEmpty) {
      nextWave();
    }
  }

  // Handler de teclado
  @override
  KeyEventResult onKeyEvent(KeyEvent event, Set<LogicalKeyboardKey> keysPressed) {
    if (event is KeyDownEvent) {
      _pressedKeys.add(event.logicalKey);
      // Pausar/despausar com ESC
      if (event.logicalKey == LogicalKeyboardKey.escape) {
        if (!paused) {
          paused = true;
          overlays.add('PauseMenu');
        } else {
          paused = false;
          overlays.remove('PauseMenu');
        }
        return KeyEventResult.handled;
      }
      // Abrir/fechar tela de status com TAB
      if (event.logicalKey == LogicalKeyboardKey.tab) {
        if (!overlays.isActive('Status')) {
          openStatus();
        } else {
          closeStatus();
        }
        return KeyEventResult.handled;
      }
      // Abrir painel de estatísticas do player com E
      if (event.logicalKey == LogicalKeyboardKey.keyE) {
        if (!overlays.isActive('PlayerStats')) {
          openPlayerStats();
        } else {
          closePlayerStats();
        }
        return KeyEventResult.handled;
      }
    } else if (event is KeyUpEvent) {
      _pressedKeys.remove(event.logicalKey);
    }
    return KeyEventResult.handled;
  }

  // Handler de clique do mouse para atirar
  @override
  void onTapDown(TapDownInfo info) {
    if (gameOver) return;
    mousePressed = true;
    final clickPos = info.eventPosition.global;
    final dir = (clickPos - player.position).normalized();
    lastMouseDirection = dir;
    // Disparo único imediato ao clicar
    if (bulletCooldown <= 0.0) {
      final critChance = tacticalSightUpgrades > 0 ? (player.statusArmas ~/ 2) * 0.05 * tacticalSightUpgrades : 0.0;
      bool isCrit;
      if (comboShotUpgrades > 0 && comboHitCount == 3) {
        isCrit = true;
      } else {
        isCrit = critChance > 0 && (random.nextDouble() < critChance);
      }
      final isVamp = vampiricBulletUpgrades > 0;
      int baseDmg = player.bulletDamage;
      int dmg = isCrit ? baseDmg * 2 : baseDmg;
      int vampAmount = isVamp ? (dmg * 0.1 * vampiricBulletUpgrades).round() : 0;
      add(BulletComponent(
        position: player.position.clone(),
        direction: dir,
        damage: dmg,
        isCrit: isCrit,
        isVampiric: isVamp,
        vampiricAmount: vampAmount,
      ));
      bulletCooldown = bulletInterval;
    }
  }

  @override
  void onTapUp(TapUpInfo info) {
    mousePressed = false;
  }

  @override
  void onTapCancel() {
    mousePressed = false;
  }

  // Removido movimento por clique/tap
}

class PlayerCircle extends CircleComponent {
  int life = 100;
  int xp = 0;
  int level = 1;
  int xpToNextLevel = 100;
  int statusPoints = 0;
  int statusHaki = 0;
  int statusAkuma = 0;
  int statusVida = 0;
  int statusArmas = 0;
  int statusStamina = 0;
  // Confirmados
  int confirmedHaki = 0;
  int confirmedAkuma = 0;
  int confirmedVida = 0;
  int confirmedArmas = 0;
  int confirmedStamina = 0;
  int maxLife = 100;
  int bulletDamage = 5;
  PlayerCircle({required Vector2 position})
      : super(
          radius: 30,
          paint: Paint()..color = Colors.blue,
          position: position,
          anchor: Anchor.center,
        );

  /// Adiciona XP, retorna true se subiu de nível
  bool addXp(int amount) {
    xp += amount;
    bool leveledUp = false;
    while (xp >= xpToNextLevel) {
      xp -= xpToNextLevel;
      level++;
      statusPoints += 5;
      xpToNextLevel = 100 + (level - 1) * 25;
      leveledUp = true;
    }
    return leveledUp;
  }

  void applyStatusEffects() {
    maxLife = 100 + statusVida * 10;
    bulletDamage = 5 + statusArmas * 2;
    // Se a vida atual for maior que a nova vida máxima, ajusta
    if (life > maxLife) life = maxLife;
  }

  @override
  void render(Canvas canvas) {
    super.render(canvas);
    // Barra de XP (acima da barra de vida)
    const double xpBarWidth = 60;
    const double xpBarHeight = 7;
    final double xpX = -xpBarWidth / 2;
    final double xpY = radius + 2;
    final RRect xpBarBg = RRect.fromRectAndRadius(
      Rect.fromLTWH(xpX, xpY, xpBarWidth, xpBarHeight),
      const Radius.circular(4),
    );
    // Sombra
    canvas.drawRRect(
      xpBarBg.shift(const Offset(1.5, 1.5)),
      Paint()..color = Colors.black.withOpacity(0.25),
    );
    // Fundo (cinza escuro)
    canvas.drawRRect(
      xpBarBg,
      Paint()..color = Colors.grey.shade800,
    );
    // XP (gradiente azul)
    final double xpPercent = xpToNextLevel > 0 ? xp / xpToNextLevel : 0.0;
    final RRect xpBarFill = RRect.fromRectAndRadius(
      Rect.fromLTWH(xpX, xpY, xpBarWidth * xpPercent, xpBarHeight),
      const Radius.circular(4),
    );
    final Paint xpPaint = Paint()
      ..shader = LinearGradient(
        colors: [Colors.lightBlueAccent, Colors.blue.shade700],
      ).createShader(Rect.fromLTWH(xpX, xpY, xpBarWidth, xpBarHeight));
    canvas.drawRRect(xpBarFill, xpPaint);
    // Borda
    canvas.drawRRect(
      xpBarBg,
      Paint()
        ..color = Colors.white
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.2,
    );
    // Valor numérico XP
    final xpTextPainter = TextPainter(
      text: TextSpan(
        text: '$xp/$xpToNextLevel XP',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 10,
          fontWeight: FontWeight.bold,
          shadows: [Shadow(blurRadius: 1, color: Colors.black, offset: Offset(1,1))],
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    xpTextPainter.paint(canvas, Offset(-xpTextPainter.width/2, xpY - 13));
    // Barra de vida do player (melhorada)
    const double barWidth = 60;
    const double barHeight = 12;
    final double x = -barWidth / 2;
    final double y = radius + 14;
    final RRect barBg = RRect.fromRectAndRadius(
      Rect.fromLTWH(x, y, barWidth, barHeight),
      const Radius.circular(6),
    );
    // Sombra
    canvas.drawRRect(
      barBg.shift(const Offset(2, 2)),
      Paint()..color = Colors.black.withOpacity(0.4),
    );
    // Fundo (vermelho escuro)
    canvas.drawRRect(
      barBg,
      Paint()..color = Colors.red.shade900,
    );
    // Vida (gradiente verde)
    final double percent = life / 100;
    final RRect barLife = RRect.fromRectAndRadius(
      Rect.fromLTWH(x, y, barWidth * percent, barHeight),
      const Radius.circular(6),
    );
    final Paint lifePaint = Paint()
      ..shader = LinearGradient(
        colors: [Colors.greenAccent, Colors.green.shade700],
      ).createShader(Rect.fromLTWH(x, y, barWidth, barHeight));
    canvas.drawRRect(barLife, lifePaint);
    // Borda destacada
    canvas.drawRRect(
      barBg,
      Paint()
        ..color = Colors.white
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2,
    );
    // Valor numérico
    final textPainter = TextPainter(
      text: TextSpan(
        text: '$life/100',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 13,
          fontWeight: FontWeight.bold,
          shadows: [Shadow(blurRadius: 2, color: Colors.black, offset: Offset(1,1))],
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    textPainter.paint(canvas, Offset(-textPainter.width/2, y - 18));
  }
}

class ObstacleCircle extends CircleComponent {
  Vector2 direction;
  final double speed;
  int vida = 100;
  double attackCooldown = 0.0;
  static const double attackInterval = 0.7; // segundos entre ataques
  double bleedTime = 0.0;
  int bleedDamage = 0;

  ObstacleCircle({
    required Vector2 position,
    required this.direction,
    required this.speed,
  }) : super(
          radius: 25,
          paint: Paint()..color = Colors.red,
          position: position,
          anchor: Anchor.center,
        );

  @override
  void update(double dt) {
    super.update(dt);
    final game = findGame() as DodgeObstaclesGame?;
    if (game != null && game.paused) return;
    if (attackCooldown > 0) {
      attackCooldown -= dt;
    }
    // Sangramento
    if (bleedTime > 0 && bleedDamage > 0) {
      bleedTime -= dt;
      if (bleedTime <= 0) {
        bleedTime = 0;
        bleedDamage = 0;
      } else {
        // Dano de sangramento por segundo
        final bleedDmg = (bleedDamage * dt).round();
        if (bleedDmg > 0) {
          vida -= bleedDmg;
          if (vida <= 0) vida = 0;
          
          // Criar mensagem de dano de sangramento (apenas a cada 0.3 segundos para não spam)
          final game = findGame() as DodgeObstaclesGame?;
          if (game != null && (DateTime.now().millisecondsSinceEpoch % 300) < 16) { // ~30 FPS
            final currentTime = DateTime.now().millisecondsSinceEpoch / 1000;
            game.damageMessages.add(DamageMessage(
              'SANGUE $bleedDmg',
              position.clone(),
              currentTime,
              false, // Não é crítico, mas é sangramento
            ));
          }
        }
      }
    }
    // Segue o jogador
    if (game != null && !game.gameOver) {
      final playerPos = game.player.position;
      direction = (playerPos - position).normalized();
      // Prever próximo movimento
      final nextPos = position + direction * speed * dt;
      final minDist = game.player.radius + radius;
      final distToPlayer = nextPos.distanceTo(playerPos);
      if (distToPlayer < minDist) {
        // Colocá-lo exatamente na borda, sem sobreposição
        position = playerPos + (nextPos - playerPos).normalized() * minDist;
      } else {
        position = nextPos;
      }
    } else {
      position += direction * speed * dt;
    }
  }

  @override
  void render(Canvas canvas) {
    super.render(canvas);
    
    // Efeito visual de sangramento
    if (bleedTime > 0 && bleedDamage > 0) {
      // Desenhar um círculo vermelho pulsante ao redor do obstáculo
      final pulseAlpha = (0.4 + 0.3 * (DateTime.now().millisecondsSinceEpoch % 1000) / 1000).clamp(0.0, 1.0);
      canvas.drawCircle(
        Offset(position.x, position.y),
        radius + 8,
        Paint()
          ..color = Colors.red.withOpacity(pulseAlpha)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 4,
      );
      
      // Desenhar gotas de sangue
      final time = DateTime.now().millisecondsSinceEpoch;
      for (int i = 0; i < 3; i++) {
        final angle = (time / 1000 + i * 2.094) % (2 * pi); // 120° entre cada gota
        final dropX = position.x + cos(angle) * (radius + 15);
        final dropY = position.y + sin(angle) * (radius + 15);
        canvas.drawCircle(
          Offset(dropX, dropY),
          3,
          Paint()..color = Colors.red.withOpacity(0.8),
        );
      }
    }
    
    // Barra de vida do obstáculo (melhorada)
    const double barWidth = 44;
    const double barHeight = 8;
    final double x = -barWidth / 2;
    final double y = radius + 10;
    final RRect barBg = RRect.fromRectAndRadius(
      Rect.fromLTWH(x, y, barWidth, barHeight),
      const Radius.circular(4),
    );
    // Sombra
    canvas.drawRRect(
      barBg.shift(const Offset(1.5, 1.5)),
      Paint()..color = Colors.black.withOpacity(0.35),
    );
    // Fundo (vermelho escuro)
    canvas.drawRRect(
      barBg,
      Paint()..color = Colors.red.shade900,
    );
    // Vida (gradiente laranja-amarelo)
    final double percent = vida / 100;
    final RRect barLife = RRect.fromRectAndRadius(
      Rect.fromLTWH(x, y, barWidth * percent, barHeight),
      const Radius.circular(4),
    );
    final Paint lifePaint = Paint()
      ..shader = LinearGradient(
        colors: [Colors.yellowAccent, Colors.orange.shade700],
      ).createShader(Rect.fromLTWH(x, y, barWidth, barHeight));
    canvas.drawRRect(barLife, lifePaint);
    // Borda destacada
    canvas.drawRRect(
      barBg,
      Paint()
        ..color = Colors.white
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.5,
    );
    // Valor numérico
    final textPainter = TextPainter(
      text: TextSpan(
        text: ' $vida/100',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 11,
          fontWeight: FontWeight.bold,
          shadows: [Shadow(blurRadius: 1.5, color: Colors.black, offset: Offset(1,1))],
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    textPainter.paint(canvas, Offset(-textPainter.width/2, y - 14));
  }
}

// Overlay de Game Over
class GameOverOverlay extends StatelessWidget {
  final DodgeObstaclesGame game;
  const GameOverOverlay({super.key, required this.game});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black.withOpacity(0.8),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Você perdeu!',
              style: TextStyle(
                color: Colors.white,
                fontSize: 40,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: () {
                game.startGame();
              },
              child: const Text('Recomeçar', style: TextStyle(fontSize: 24)),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                // Fecha o app
                exit(0);
              },
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
              child: const Text('Fechar', style: TextStyle(fontSize: 24)),
            ),
          ],
        ),
      ),
    );
  }
}

// Overlay de Pause
class PauseMenuOverlay extends StatelessWidget {
  final DodgeObstaclesGame game;
  const PauseMenuOverlay({super.key, required this.game});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black.withOpacity(0.8),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Jogo Pausado',
              style: TextStyle(
                color: Colors.white,
                fontSize: 40,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: () {
                game.paused = false;
                game.overlays.remove('PauseMenu');
              },
              child: const Text('Voltar ao jogo', style: TextStyle(fontSize: 24)),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                exit(0);
              },
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
              child: const Text('Fechar', style: TextStyle(fontSize: 24)),
            ),
          ],
        ),
      ),
    );
  }
}

// Classe para mensagens de dano
class DamageMessage {
  final String text;
  final Vector2 position;
  final double startTime;
  final bool isCritical;
  final double duration = 1.5; // Duração em segundos
  
  DamageMessage(this.text, this.position, this.startTime, this.isCritical);
  
  bool get isExpired => (DateTime.now().millisecondsSinceEpoch / 1000) - startTime > duration;
}

// Componente de tiro
class BulletComponent extends CircleComponent {
  final Vector2 direction;
  final double speed = 500;
  int damage;
  bool isCrit;
  bool isVampiric;
  int vampiricAmount;
  BulletComponent({required Vector2 position, required this.direction, required this.damage, this.isCrit = false, this.isVampiric = false, this.vampiricAmount = 0})
      : super(
          radius: 8,
          paint: Paint()..color = const Color.fromARGB(255, 140, 137, 108),
          position: position,
          anchor: Anchor.center,
        );

  @override
  void update(double dt) {
    super.update(dt);
    final game = findGame() as DodgeObstaclesGame?;
    if (game != null && game.paused) return;
    position += direction * speed * dt;
    // Remove se sair da tela
    final g = game;
    if (g != null) {
      if (position.x < -radius || position.x > g.size.x + radius ||
          position.y < -radius || position.y > g.size.y + radius) {
        removeFromParent();
      }
    }
  }
}

// Overlay de Status
class StatusOverlay extends StatefulWidget {
  final DodgeObstaclesGame game;
  const StatusOverlay({super.key, required this.game});

  @override
  State<StatusOverlay> createState() => _StatusOverlayState();
}

class _StatusOverlayState extends State<StatusOverlay> {
  late int haki, akuma, vida, armas, stamina, points;
  late int confirmedHaki, confirmedAkuma, confirmedVida, confirmedArmas, confirmedStamina;

  @override
  void initState() {
    super.initState();
    final p = widget.game.player;
    haki = p.statusHaki;
    akuma = p.statusAkuma;
    vida = p.statusVida;
    armas = p.statusArmas;
    stamina = p.statusStamina;
    points = p.statusPoints;
    confirmedHaki = p.confirmedHaki;
    confirmedAkuma = p.confirmedAkuma;
    confirmedVida = p.confirmedVida;
    confirmedArmas = p.confirmedArmas;
    confirmedStamina = p.confirmedStamina;
  }

  void _inc(String type) {
    if (points > 0) {
      setState(() {
        switch (type) {
          case 'Haki': haki++; break;
          case 'Akuma': akuma++; break;
          case 'Vida': vida++; break;
          case 'Armas': armas++; break;
          case 'Stamina': stamina++; break;
        }
        points--;
      });
    }
  }
  void _dec(String type) {
    setState(() {
      switch (type) {
        case 'Haki': if (haki > confirmedHaki) { haki--; points++; } break;
        case 'Akuma': if (akuma > confirmedAkuma) { akuma--; points++; } break;
        case 'Vida': if (vida > confirmedVida) { vida--; points++; } break;
        case 'Armas': if (armas > confirmedArmas) { armas--; points++; } break;
        case 'Stamina': if (stamina > confirmedStamina) { stamina--; points++; } break;
      }
    });
  }
  Widget _bar(String label, int value, int confirmed, VoidCallback onInc, VoidCallback onDec) {
    return Row(
      children: [
        SizedBox(width: 80, child: Text(label, style: const TextStyle(fontSize: 20, color: Colors.white))),
        IconButton(
          icon: const Icon(Icons.remove, color: Colors.red),
          onPressed: value > confirmed ? onDec : null,
        ),
        Expanded(
          child: LinearProgressIndicator(
            value: value / 20.0,
            minHeight: 18,
            backgroundColor: Colors.grey.shade800,
            valueColor: AlwaysStoppedAnimation<Color>(Colors.blueAccent),
          ),
        ),
        IconButton(
          icon: const Icon(Icons.add, color: Colors.green),
          onPressed: onInc,
        ),
        SizedBox(width: 32, child: Text('$value', style: const TextStyle(fontSize: 18, color: Colors.white))),
      ],
    );
  }
  void _confirm() {
    final p = widget.game.player;
    setState(() {
      p.statusHaki = haki;
      p.statusAkuma = akuma;
      p.statusVida = vida;
      p.statusArmas = armas;
      p.statusStamina = stamina;
      p.statusPoints = points;
      p.confirmedHaki = haki;
      p.confirmedAkuma = akuma;
      p.confirmedVida = vida;
      p.confirmedArmas = armas;
      p.confirmedStamina = stamina;
      confirmedHaki = haki;
      confirmedAkuma = akuma;
      confirmedVida = vida;
      confirmedArmas = armas;
      confirmedStamina = stamina;
      p.applyStatusEffects();
    });
  }
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black.withOpacity(0.92),
      child: Center(
        child: Container(
          padding: const EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: Colors.grey.shade900,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: Colors.amber, width: 3),
          ),
          width: 480,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Pontos de Status: $points', style: const TextStyle(fontSize: 24, color: Colors.amber, fontWeight: FontWeight.bold)),
              const SizedBox(height: 24),
              _bar('Haki', haki, confirmedHaki, () => _inc('Haki'), () => _dec('Haki')),
              const SizedBox(height: 12),
              _bar('Akuma no Mi', akuma, confirmedAkuma, () => _inc('Akuma'), () => _dec('Akuma')),
              const SizedBox(height: 12),
              _bar('Armas', armas, confirmedArmas, () => _inc('Armas'), () => _dec('Armas')),
              const SizedBox(height: 12),
              _bar('Vida', vida, confirmedVida, () => _inc('Vida'), () => _dec('Vida')),
              const SizedBox(height: 12),
              _bar('Stamina', stamina, confirmedStamina, () => _inc('Stamina'), () => _dec('Stamina')),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: _confirm,
                child: const Text('Confirmar', style: TextStyle(fontSize: 22)),
              ),
              const SizedBox(height: 12),
              ElevatedButton(
                onPressed: () {
                  widget.game.closeStatus();
                },
                child: const Text('Fechar', style: TextStyle(fontSize: 22)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Overlay de escolhas
class ChoiceOverlay extends StatelessWidget {
  final DodgeObstaclesGame game;
  const ChoiceOverlay({super.key, required this.game});

  Widget _buildUpgradeCard(String choice, VoidCallback onPressed) {
    Map<String, Map<String, dynamic>> upgradeInfo = {
      'Força de Sobrevivencia': {
        'icon': Icons.shield,
        'color': Colors.red,
        'description': 'A cada 50 de vida perdida, ganha +5% de resistência temporária por 10 segundos.',
        'category': 'VIDA',
      },
      'Recuperação Pós Wave': {
        'icon': Icons.healing,
        'color': Colors.pink,
        'description': 'Ao completar uma wave, recupera 5% da vida perdida.',
        'category': 'VIDA',
      },
      'Tanque de Guerra': {
        'icon': Icons.fitness_center,
        'color': Colors.redAccent,
        'description': '+5% de vida máxima adicional sobre o valor total atual.',
        'category': 'VIDA',
      },
      'Mira Tática': {
        'icon': Icons.center_focus_strong,
        'color': Colors.orange,
        'description': 'A cada 2 pontos em Armas, aumenta +5% de chance de acerto crítico.',
        'category': 'ARMAS',
      },
      'Projétil Vampírico': {
        'icon': Icons.bloodtype,
        'color': Colors.deepOrange,
        'description': '10% do dano causado com armas retorna como vida para o jogador.',
        'category': 'ARMAS',
      },
      'Escudo de Impacto': {
        'icon': Icons.security,
        'color': Colors.deepOrange,
        'description': 'Ao receber um ataque, inimigos ao redor tomam 10 de dano (cooldown: 5s).',
        'category': 'VIDA',
      },
      'Combo de Tiros': {
        'icon': Icons.auto_awesome,
        'color': Colors.orangeAccent,
        'description': 'A cada 3 tiros consecutivos acertados, o quarto é crítico garantido.',
        'category': 'ARMAS',
      },
      'Golpe Decisivo': {
        'icon': Icons.water_drop,
        'color': Colors.deepOrange,
        'description': 'Críticos causam sangramento: 5 de dano por segundo por 3 segundos.',
        'category': 'ARMAS',
      },
    };

    final info = upgradeInfo[choice] ?? {
      'icon': Icons.star,
      'color': Colors.amber,
      'description': 'Upgrade especial!',
      'category': 'ESPECIAL',
    };

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            info['color'].withOpacity(0.8),
            info['color'].withOpacity(0.6),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: info['color'], width: 2),
        boxShadow: [
          BoxShadow(
            color: info['color'].withOpacity(0.4),
            blurRadius: 10,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    info['icon'],
                    size: 32,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            choice,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                              shadows: [Shadow(blurRadius: 2, color: Colors.black, offset: Offset(1,1))],
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.3),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              info['category'],
                              style: const TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        info['description'],
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.white,
                          height: 1.3,
                        ),
                      ),
                    ],
                  ),
                ),
                const Icon(
                  Icons.arrow_forward_ios,
                  color: Colors.white,
                  size: 20,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black.withOpacity(0.85),
      child: Center(
        child: Container(
          padding: const EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: Colors.grey.shade900,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: Colors.blueAccent, width: 3),
          ),
          width: 500,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                '🏴‍☠️ ESCOLHA SEU UPGRADE! 🏴‍☠️',
                style: TextStyle(
                  fontSize: 24,
                  color: Colors.amber,
                  fontWeight: FontWeight.bold,
                  shadows: [Shadow(blurRadius: 2, color: Colors.black, offset: Offset(1,1))],
                ),
              ),
              const SizedBox(height: 32),
              ...game.currentChoices.asMap().entries.map((entry) {
                int index = entry.key;
                String choice = entry.value;
                return _buildUpgradeCard(choice, () => game.pickChoice(index));
              }).toList(),
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.amber.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.amber.withOpacity(0.3)),
                ),
                child: const Text(
                  '💡 Dica: Os upgrades acumulam efeitos se escolhidos múltiplas vezes!',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.amber,
                    fontStyle: FontStyle.italic,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Overlay para mostrar ícones dos upgrades ativos
class UpgradeIconsOverlay extends StatelessWidget {
  final DodgeObstaclesGame game;
  const UpgradeIconsOverlay({super.key, required this.game});

  @override
  Widget build(BuildContext context) {
    final List<_UpgradeIconData> icons = [];
    if (game.tankUpgrades > 0) {
      icons.add(_UpgradeIconData(Icons.fitness_center, 'Tanque de Guerra', game.tankUpgrades, color: Colors.redAccent));
    }
    if (game.recoveryUpgrades > 0) {
      icons.add(_UpgradeIconData(Icons.healing, 'Recuperação Pós Wave', game.recoveryUpgrades, color: Colors.pinkAccent));
    }
    if (game.survivalUpgrades > 0) {
      icons.add(_UpgradeIconData(Icons.shield, 'Força de Sobrevivência', game.survivalUpgrades, color: Colors.red));
    }
    if (game.tacticalSightUpgrades > 0) {
      icons.add(_UpgradeIconData(Icons.center_focus_strong, 'Mira Tática', game.tacticalSightUpgrades, color: Colors.orange));
    }
    if (game.vampiricBulletUpgrades > 0) {
      icons.add(_UpgradeIconData(Icons.bloodtype, 'Projétil Vampírico', game.vampiricBulletUpgrades, color: Colors.deepOrangeAccent));
    }
    if (game.impactShieldUpgrades > 0) {
      icons.add(_UpgradeIconData(Icons.security, 'Escudo de Impacto', game.impactShieldUpgrades, color: Colors.deepOrange));
    }
    if (game.comboShotUpgrades > 0) {
      icons.add(_UpgradeIconData(Icons.auto_awesome, 'Combo de Tiros', game.comboShotUpgrades, color: Colors.orangeAccent));
    }
    if (game.decisiveBlowUpgrades > 0) {
      icons.add(_UpgradeIconData(Icons.water_drop, 'Golpe Decisivo', game.decisiveBlowUpgrades, color: Colors.deepOrange));
    }
    if (icons.isEmpty) return const SizedBox.shrink();
    return Positioned(
      left: 16,
      bottom: 16,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: icons.map((iconData) => Padding(
          padding: const EdgeInsets.only(right: 18),
          child: Stack(
            alignment: Alignment.bottomRight,
            children: [
              Container(
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.7),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: iconData.color, width: 2),
                ),
                padding: const EdgeInsets.all(8),
                child: Icon(iconData.icon, size: 38, color: iconData.color),
              ),
              if (iconData.count > 1)
                Positioned(
                  right: 2,
                  bottom: 2,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: iconData.color,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      '${iconData.count}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
                        shadows: [Shadow(blurRadius: 2, color: Colors.black, offset: Offset(1,1))],
                      ),
                    ),
                  ),
                ),
            ],
          ),
        )).toList(),
      ),
    );
  }
}

class _UpgradeIconData {
  final IconData icon;
  final String label;
  final int count;
  final Color color;
  _UpgradeIconData(this.icon, this.label, this.count, {this.color = Colors.amberAccent});
}

// Overlay do Menu Principal
class MainMenuOverlay extends StatelessWidget {
  final DodgeObstaclesGame game;
  const MainMenuOverlay({super.key, required this.game});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Color(0xFF1a1a2e),
            Color(0xFF16213e),
            Color(0xFF0f3460),
          ],
        ),
      ),
      child: Center(
        child: Container(
          padding: const EdgeInsets.all(40),
          decoration: BoxDecoration(
            color: const Color(0xFF1a1a2e).withOpacity(0.95),
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: const Color(0xFFffd700), width: 4),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFFffd700).withOpacity(0.4),
                blurRadius: 25,
                spreadRadius: 8,
              ),
              BoxShadow(
                color: Colors.black.withOpacity(0.5),
                blurRadius: 15,
                spreadRadius: 2,
              ),
            ],
          ),
          width: 450,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFF8B0000).withOpacity(0.8),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFFffd700), width: 2),
                ),
                child: const Text(
                  'ROGUE PIECE',
                  style: TextStyle(
                    fontSize: 42,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFFffd700),
                    shadows: [
                      Shadow(blurRadius: 8, color: Colors.black, offset: Offset(3,3)),
                      Shadow(blurRadius: 4, color: Color(0xFF8B0000), offset: Offset(1,1)),
                    ],
                    letterSpacing: 3,
                  ),
                ),
              ),
              const SizedBox(height: 40),
              Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  gradient: const LinearGradient(
                    colors: [Color(0xFF228B22), Color(0xFF32CD32)],
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF228B22).withOpacity(0.5),
                      blurRadius: 10,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: ElevatedButton(
                  onPressed: () {
                    game.startGame();
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 40),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: const Text(
                    'COMEÇAR JOGO',
                    style: TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      shadows: [Shadow(blurRadius: 2, color: Colors.black, offset: Offset(1,1))],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  gradient: const LinearGradient(
                    colors: [Color(0xFFFF8C00), Color(0xFFFFA500)],
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFFFF8C00).withOpacity(0.5),
                      blurRadius: 10,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: ElevatedButton(
                  onPressed: () {
                    game.overlays.add('Guide');
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 40),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: const Text(
                    'GUIA',
                    style: TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      shadows: [Shadow(blurRadius: 2, color: Colors.black, offset: Offset(1,1))],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  gradient: const LinearGradient(
                    colors: [Color(0xFFDC143C), Color(0xFFB22222)],
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFFDC143C).withOpacity(0.5),
                      blurRadius: 10,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: ElevatedButton(
                  onPressed: () {
                    exit(0);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 40),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: const Text(
                    'FECHAR JOGO',
                    style: TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      shadows: [Shadow(blurRadius: 2, color: Colors.black, offset: Offset(1,1))],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 30),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                decoration: BoxDecoration(
                  color: const Color(0xFFffd700).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFffd700).withOpacity(0.3), width: 1),
                ),
                child: const Text(
                  '🏴‍☠️ Aventure-se no mundo dos piratas! 🏴‍☠️',
                  style: TextStyle(
                    fontSize: 16,
                    color: Color(0xFFffd700),
                    fontWeight: FontWeight.w600,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Overlay do Guia
class GuideOverlay extends StatelessWidget {
  final DodgeObstaclesGame game;
  const GuideOverlay({super.key, required this.game});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Color(0xFF1a1a2e),
            Color(0xFF16213e),
            Color(0xFF0f3460),
          ],
        ),
      ),
      child: Center(
        child: Container(
          padding: const EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: const Color(0xFF1a1a2e).withOpacity(0.95),
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: const Color(0xFFffd700), width: 4),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFFffd700).withOpacity(0.4),
                blurRadius: 25,
                spreadRadius: 8,
              ),
            ],
          ),
          width: 600,
          height: 700,
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      '🏴‍☠️ GUIA DO JOGO 🏴‍☠️',
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFFffd700),
                        shadows: [Shadow(blurRadius: 4, color: Colors.black, offset: Offset(2,2))],
                      ),
                    ),
                    IconButton(
                      onPressed: () {
                        game.overlays.remove('Guide');
                      },
                      icon: const Icon(Icons.close, color: Color(0xFFffd700), size: 30),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                
                // OBJETIVO
                _buildSection('🎯 OBJETIVO', [
                  'Elimine todos os obstáculos vermelhos para avançar de wave!',
                  'Sobreviva o máximo possível e colete upgrades para se tornar mais forte.',
                  'A cada 3 waves, escolha um upgrade para melhorar suas habilidades.',
                ]),
                
                // COMANDOS
                _buildSection('⌨️ COMANDOS', [
                  'WASD ou Setas: Mover o jogador',
                  'Mouse (Clique e segure): Atirar na direção do mouse',
                  'TAB: Abrir tela de status',
                  'E: Abrir painel de estatísticas do player',
                  'ESC: Pausar/despausar o jogo',
                ]),
                
                // UPGRADES DE VIDA
                _buildSection('❤️ UPGRADES DE VIDA', [
                  '🛡️ Força de Sobrevivência: A cada 50 de vida perdida, ganha +5% de resistência temporária (10s)',
                  '💚 Recuperação Pós Wave: Ao completar uma wave, recupera 5% da vida perdida',
                  '💪 Tanque de Guerra: +5% de vida máxima adicional sobre o valor total atual',
                  '⚡ Escudo de Impacto: Ao receber um ataque, inimigos ao redor tomam 10 de dano (cooldown: 5s)',
                ]),
                
                // UPGRADES DE ARMAS
                _buildSection('🔫 UPGRADES DE ARMAS', [
                  '🎯 Mira Tática: A cada 2 pontos em Armas, aumenta +5% de chance de acerto crítico',
                  '🩸 Projétil Vampírico: 10% do dano causado com armas retorna como vida',
                  '🎲 Combo de Tiros: A cada 3 tiros consecutivos acertados, o quarto é crítico garantido',
                  '💧 Golpe Decisivo: Críticos causam sangramento: 5 de dano por segundo por 3s',
                ]),
                
                // SISTEMA DE STATUS
                _buildSection('📊 SISTEMA DE STATUS', [
                  'A cada nível, ganhe 5 pontos de status para distribuir:',
                  '• Haki: Aumenta chance de crítico',
                  '• Akuma no Mi: Aumenta velocidade dos tiros',
                  '• Vida: Aumenta vida máxima',
                  '• Armas: Aumenta dano dos tiros',
                  '• Stamina: Aumenta velocidade de movimento',
                ]),
                
                // DICAS
                _buildSection('💡 DICAS', [
                  'Use o mouse para mirar e atirar com precisão!',
                  'Distribua seus pontos de status sabiamente.',
                  'Combos de upgrades da mesma classe são poderosos!',
                  'Mantenha-se em movimento para evitar obstáculos.',
                  'Pressione E para ver suas estatísticas detalhadas durante o jogo!',
                ]),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildSection(String title, List<String> items) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Color(0xFFffd700),
              shadows: [Shadow(blurRadius: 2, color: Colors.black, offset: Offset(1,1))],
            ),
          ),
          const SizedBox(height: 8),
          ...items.map((item) => Padding(
            padding: const EdgeInsets.only(left: 16, bottom: 4),
            child: Text(
              '• $item',
              style: const TextStyle(
                fontSize: 14,
                color: Colors.white,
                height: 1.4,
              ),
            ),
          )).toList(),
        ],
      ),
    );
  }
}

// Overlay de Confirmação de Escolha
class ConfirmChoiceOverlay extends StatelessWidget {
  final DodgeObstaclesGame game;
  const ConfirmChoiceOverlay({super.key, required this.game});

  @override
  Widget build(BuildContext context) {
    if (game.selectedChoice == null) return const SizedBox.shrink();
    
    Map<String, Map<String, dynamic>> upgradeInfo = {
      'Força de Sobrevivencia': {
        'icon': Icons.shield,
        'color': Colors.red,
        'description': 'A cada 50 de vida perdida, ganha +5% de resistência temporária por 10 segundos.',
        'category': 'VIDA',
      },
      'Recuperação Pós Wave': {
        'icon': Icons.healing,
        'color': Colors.pink,
        'description': 'Ao completar uma wave, recupera 5% da vida perdida.',
        'category': 'VIDA',
      },
      'Tanque de Guerra': {
        'icon': Icons.fitness_center,
        'color': Colors.redAccent,
        'description': '+5% de vida máxima adicional sobre o valor total atual.',
        'category': 'VIDA',
      },
      'Mira Tática': {
        'icon': Icons.center_focus_strong,
        'color': Colors.orange,
        'description': 'A cada 2 pontos em Armas, aumenta +5% de chance de acerto crítico.',
        'category': 'ARMAS',
      },
      'Projétil Vampírico': {
        'icon': Icons.bloodtype,
        'color': Colors.deepOrange,
        'description': '10% do dano causado com armas retorna como vida para o jogador.',
        'category': 'ARMAS',
      },
      'Escudo de Impacto': {
        'icon': Icons.security,
        'color': Colors.deepOrange,
        'description': 'Ao receber um ataque, inimigos ao redor tomam 10 de dano (cooldown: 5s).',
        'category': 'VIDA',
      },
      'Combo de Tiros': {
        'icon': Icons.auto_awesome,
        'color': Colors.orangeAccent,
        'description': 'A cada 3 tiros consecutivos acertados, o quarto é crítico garantido.',
        'category': 'ARMAS',
      },
      'Golpe Decisivo': {
        'icon': Icons.water_drop,
        'color': Colors.deepOrange,
        'description': 'Críticos causam sangramento: 5 de dano por segundo por 3 segundos.',
        'category': 'ARMAS',
      },
    };

    final info = upgradeInfo[game.selectedChoice!] ?? {
      'icon': Icons.star,
      'color': Colors.amber,
      'description': 'Upgrade especial!',
      'category': 'ESPECIAL',
    };

    return Container(
      color: Colors.black.withOpacity(0.9),
      child: Center(
        child: Container(
          padding: const EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: const Color(0xFF1a1a2e).withOpacity(0.95),
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: info['color'], width: 4),
            boxShadow: [
              BoxShadow(
                color: info['color'].withOpacity(0.4),
                blurRadius: 25,
                spreadRadius: 8,
              ),
            ],
          ),
          width: 450,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '❓ TEM CERTEZA? ❓',
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.amber,
                  shadows: [Shadow(blurRadius: 4, color: Colors.black, offset: Offset(2,2))],
                ),
              ),
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      info['color'].withOpacity(0.8),
                      info['color'].withOpacity(0.6),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: info['color'], width: 2),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(
                        info['icon'],
                        size: 32,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text(
                                game.selectedChoice!,
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                  shadows: [Shadow(blurRadius: 2, color: Colors.black, offset: Offset(1,1))],
                                ),
                              ),
                              const SizedBox(width: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.3),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  info['category'],
                                  style: const TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            info['description'],
                            style: const TextStyle(
                              fontSize: 14,
                              color: Colors.white,
                              height: 1.3,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  ElevatedButton(
                    onPressed: () {
                      game.cancelChoice();
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.grey.shade600,
                      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: const Text(
                      'CANCELAR',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                  ),
                  ElevatedButton(
                    onPressed: () {
                      game.confirmChoice();
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: const Text(
                      'CONFIRMAR',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Overlay de Estatísticas do Player
class PlayerStatsOverlay extends StatelessWidget {
  final DodgeObstaclesGame game;
  const PlayerStatsOverlay({super.key, required this.game});

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              title,
              style: const TextStyle(color: Colors.white, fontSize: 14),
            ),
          ),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUpgradeCard(String title, int count, IconData icon, Color color) {
    if (count == 0) return const SizedBox.shrink();
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [color.withOpacity(0.3), color.withOpacity(0.1)],
        ),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              title,
              style: const TextStyle(color: Colors.white, fontSize: 14),
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              '$count',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final player = game.player;
    
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Color(0xFF1a1a2e),
            Color(0xFF16213e),
            Color(0xFF0f3460),
          ],
        ),
      ),
      child: Center(
        child: Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: const Color(0xFF1a1a2e).withOpacity(0.95),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: const Color(0xFFffd700), width: 3),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFFffd700).withOpacity(0.3),
                blurRadius: 20,
                spreadRadius: 5,
              ),
            ],
          ),
          width: 500,
          height: 600,
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      '📊 ESTATÍSTICAS DO PLAYER 📊',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFFffd700),
                        shadows: [Shadow(blurRadius: 2, color: Colors.black, offset: Offset(1,1))],
                      ),
                    ),
                    IconButton(
                      onPressed: () {
                        game.closePlayerStats();
                      },
                      icon: const Icon(Icons.close, color: Color(0xFFffd700), size: 24),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                
                // INFORMAÇÕES BÁSICAS
                const Text(
                  '🎯 INFORMAÇÕES BÁSICAS',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.amber,
                  ),
                ),
                const SizedBox(height: 8),
                _buildStatCard('Nível', '${player.level}', Icons.star, Colors.amber),
                _buildStatCard('XP Atual', '${player.xp}/${player.xpToNextLevel}', Icons.trending_up, Colors.blue),
                _buildStatCard('Pontos de Status', '${player.statusPoints}', Icons.add_circle, Colors.green),
                _buildStatCard('Vida Atual', '${player.life}/${player.maxLife}', Icons.favorite, Colors.red),
                _buildStatCard('Dano do Tiro', '${player.bulletDamage}', Icons.gps_fixed, Colors.orange),
                
                const SizedBox(height: 20),
                
                // STATUS ATRIBUTOS
                const Text(
                  '⚔️ ATRIBUTOS',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.amber,
                  ),
                ),
                const SizedBox(height: 8),
                _buildStatCard('Haki', '${player.statusHaki}', Icons.psychology, Colors.purple),
                _buildStatCard('Akuma no Mi', '${player.statusAkuma}', Icons.flash_on, Colors.yellow),
                _buildStatCard('Vida', '${player.statusVida}', Icons.favorite, Colors.red),
                _buildStatCard('Armas', '${player.statusArmas}', Icons.gps_fixed, Colors.orange),
                _buildStatCard('Stamina', '${player.statusStamina}', Icons.directions_run, Colors.cyan),
                
                const SizedBox(height: 20),
                
                // UPGRADES DE VIDA
                const Text(
                  '❤️ UPGRADES DE VIDA',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.red,
                  ),
                ),
                const SizedBox(height: 8),
                _buildUpgradeCard('Força de Sobrevivência', game.survivalUpgrades, Icons.shield, Colors.red),
                _buildUpgradeCard('Recuperação Pós Wave', game.recoveryUpgrades, Icons.healing, Colors.pink),
                _buildUpgradeCard('Tanque de Guerra', game.tankUpgrades, Icons.fitness_center, Colors.redAccent),
                _buildUpgradeCard('Escudo de Impacto', game.impactShieldUpgrades, Icons.security, Colors.deepOrange),
                
                const SizedBox(height: 20),
                
                // UPGRADES DE ARMAS
                const Text(
                  '🔫 UPGRADES DE ARMAS',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange,
                  ),
                ),
                const SizedBox(height: 8),
                _buildUpgradeCard('Mira Tática', game.tacticalSightUpgrades, Icons.center_focus_strong, Colors.orange),
                _buildUpgradeCard('Projétil Vampírico', game.vampiricBulletUpgrades, Icons.bloodtype, Colors.deepOrange),
                _buildUpgradeCard('Combo de Tiros', game.comboShotUpgrades, Icons.auto_awesome, Colors.orangeAccent),
                _buildUpgradeCard('Golpe Decisivo', game.decisiveBlowUpgrades, Icons.water_drop, Colors.deepOrange),
                
                const SizedBox(height: 20),
                
                // BÔNUS ATIVOS
                const Text(
                  '⚡ BÔNUS ATIVOS',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.green,
                  ),
                ),
                const SizedBox(height: 8),
                if (game.survivalBuffPercent > 0)
                  _buildStatCard('Resistência Temporária', '${(game.survivalBuffPercent * 100).round()}%', Icons.shield, Colors.green),
                if (game.comboHitCount > 0)
                  _buildStatCard('Combo Atual', '${game.comboHitCount}/3', Icons.auto_awesome, Colors.orange),
                
                const SizedBox(height: 20),
                
                // CONTROLES
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.blue.withOpacity(0.3)),
                  ),
                  child: const Text(
                    '💡 Dica: Pressione E novamente para fechar este painel',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.blue,
                      fontStyle: FontStyle.italic,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
