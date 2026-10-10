import 'package:flutter/material.dart';
import 'package:animated_flip_counter/animated_flip_counter.dart';

// ========================
// Main App
// ========================
void main() {
  runApp(const MarcadorTrucoApp());
}

// ========================
// App Widget Principal
// ========================
class MarcadorTrucoApp extends StatelessWidget {
  const MarcadorTrucoApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: const SplashScreen(),
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.red,
        visualDensity: VisualDensity.adaptivePlatformDensity,
        scaffoldBackgroundColor: Colors.grey[100],
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.black87,
          foregroundColor: Colors.white,
        ),
        dialogTheme: DialogThemeData(
          backgroundColor: Colors.grey[50],
          titleTextStyle: TextStyle(
            color: Colors.black87,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}

// ========================
// Splash Screen Otimizada
// ========================
class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _navigateToHome();
  }

  // Aguarda 2 segundos e navega para a HomePage
  void _navigateToHome() {
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const HomePage()),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: Colors.black87,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.casino,
              size: 120,
              color: Colors.red,
            ),
            SizedBox(height: 20),
            Text(
              'Marcador de Truco',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            SizedBox(height: 20),
            CircularProgressIndicator(color: Colors.red),
          ],
        ),
      ),
    );
  }
}

// ========================
// Modelo Player Otimizado
// ========================
class Player {
  String name;
  int points;
  int victories;

  Player({
    required this.name,
    this.points = 0,
    this.victories = 0,
  });

  void addPoints(int value) => points = (points + value).clamp(0, 12);
  void subtractPoints(int value) => points = (points - value).clamp(0, 12);
  void reset() => points = 0;
  bool get hasWon => points >= 12;
}

// ========================
// Modelo de Histórico
// ========================
class HistoryEntry {
  final String playerName;
  final String action;
  final DateTime timestamp;

  HistoryEntry({
    required this.playerName,
    required this.action,
    required this.timestamp,
  });

  // Formata a data/hora para exibição
  String get formattedTime {
    return '${_pad2(timestamp.day)}/${_pad2(timestamp.month)}/${timestamp.year} '
           '${_pad2(timestamp.hour)}:${_pad2(timestamp.minute)}:${_pad2(timestamp.second)}';
  }

  String _pad2(int n) => n.toString().padLeft(2, '0');
}

// ========================
// HomePage Otimizada
// ========================
class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  // Constantes do jogo
  static const int _maxPoints = 12;
  static const int _trucoPoints = 3;
  static const int _maoDeOnzePoints = 11;

  // Times e histórico
  late Player _teamA;
  late Player _teamB;
  final List<HistoryEntry> _history = [];

  @override
  void initState() {
    super.initState();
    _teamA = Player(name: 'Nós');
    _teamB = Player(name: 'Eles');
  }

  // Adiciona 1 ponto ao jogador e registra no histórico
  void _addPoint(Player player) {
    if (player.points < _maxPoints) {
      setState(() {
        player.addPoints(1);
        _addToHistory(player, '+1 ponto');
        _checkGameEnd(player);
      });
    }
  }

  // Remove 1 ponto do jogador e registra no histórico
  void _subtractPoint(Player player) {
    if (player.points > 0) {
      setState(() {
        player.subtractPoints(1);
        _addToHistory(player, '-1 ponto');
      });
    }
  }

  // Adiciona pontos de Truco ao jogador e registra no histórico
  void _addTrucoPoints(Player player) {
    if (player.points <= (_maxPoints - _trucoPoints)) {
      setState(() {
        player.addPoints(_trucoPoints);
        _addToHistory(player, '+3 pontos (Truco)');
        _checkGameEnd(player);
      });
    }
  }

  // Adiciona uma entrada ao histórico
  void _addToHistory(Player player, String action) {
    _history.add(HistoryEntry(
      playerName: player.name,
      action: action,
      timestamp: DateTime.now(),
    ));
  }

  // Verifica se alguém venceu ou se chegou a mão de onze
  void _checkGameEnd(Player player) {
    if (player.hasWon) {
      _showVictoryDialog(player);
    } else if (_teamA.points == _maoDeOnzePoints && _teamB.points == _maoDeOnzePoints) {
      _showMaoDeOnzeDialog();
    }
  }

  // Mostra o diálogo de vitória
  void _showVictoryDialog(Player winner) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => Dialog(
        backgroundColor: Colors.grey[900],
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(
                Icons.emoji_events,
                size: 64,
                color: Colors.red,
              ),
              const SizedBox(height: 16),
              Text(
                '${winner.name} venceu!',
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                'Parabéns! ${winner.name} chegou aos $_maxPoints pontos!',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey[300],
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _startNewGame,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
                ),
                child: const Text('Nova Partida'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Mostra o diálogo de mão de onze
  void _showMaoDeOnzeDialog() {
    showDialog(
      context: context,
      builder: (_) => Dialog(
        backgroundColor: Colors.grey[900],
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(
                Icons.bolt,
                size: 64,
                color: Colors.red,
              ),
              const SizedBox(height: 16),
              const Text(
                'Mão de Onze!',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                'Ambos os times chegaram a 11 pontos!\nA próxima rodada decide tudo!',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey[300],
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => Navigator.of(context).pop(),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                ),
                child: const Text('Entendi'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Inicia nova partida, soma vitória ao vencedor e reseta pontos
  void _startNewGame() {
    setState(() {
      final winner = _teamA.hasWon ? _teamA : _teamB;
      winner.victories++;
      _teamA.reset();
      _teamB.reset();
      _history.clear();
    });
    Navigator.of(context).pop();
  }

  // Mostra diálogo para renomear o time
  void _renamePlayer(Player player) {
    final controller = TextEditingController(text: player.name);
    showDialog(
      context: context,
      builder: (_) => Dialog(
        backgroundColor: Colors.grey[900],
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Alterar nome do time',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: controller,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Nome do time',
                  labelStyle: TextStyle(color: Colors.grey[400]),
                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey[600]!),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderSide: const BorderSide(color: Colors.red),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  filled: true,
                  fillColor: Colors.grey[800],
                ),
              ),
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(),
                    style: TextButton.styleFrom(
                      foregroundColor: Colors.grey[400],
                    ),
                    child: const Text('Cancelar'),
                  ),
                  ElevatedButton(
                    onPressed: () {
                      final newName = controller.text.trim();
                      if (newName.isNotEmpty) {
                        setState(() => player.name = newName);
                      }
                      Navigator.of(context).pop();
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      foregroundColor: Colors.white,
                    ),
                    child: const Text('Salvar'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Mostra diálogo para resetar o jogo
  void _resetGame() {
    showDialog(
      context: context,
      builder: (_) => Dialog(
        backgroundColor: Colors.grey[900],
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(
                Icons.refresh,
                size: 48,
                color: Colors.red,
              ),
              const SizedBox(height: 16),
              const Text(
                'Resetar Jogo',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Isso irá zerar todos os pontos e vitórias. Confirma?',
                style: TextStyle(
                  color: Colors.grey[300],
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(),
                    style: TextButton.styleFrom(
                      foregroundColor: Colors.grey[400],
                    ),
                    child: const Text('Cancelar'),
                  ),
                  ElevatedButton(
                    onPressed: () {
                      setState(() {
                        _teamA.points = 0;
                        _teamA.victories = 0;
                        _teamB.points = 0;
                        _teamB.victories = 0;
                        _history.clear();
                      });
                      Navigator.of(context).pop();
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      foregroundColor: Colors.white,
                    ),
                    child: const Text('Confirmar'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Desfaz a última ação do histórico
  void _undoLastAction() {
    if (_history.isEmpty) return;
    
    final lastEntry = _history.removeLast();
    setState(() {
      final player = lastEntry.playerName == _teamA.name ? _teamA : _teamB;
      
      if (lastEntry.action.contains('+1')) {
        player.subtractPoints(1);
      } else if (lastEntry.action.contains('-1')) {
        player.addPoints(1);
      } else if (lastEntry.action.contains('+3')) {
        player.subtractPoints(3);
      }
    });
  }

  // Monta a coluna de cada jogador (nome, pontos, vitórias, botões)
  Widget _buildPlayerColumn(Player player) {
    final isWinning = player.points > (player == _teamA ? _teamB.points : _teamA.points);
    
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Nome do time (pode ser alterado ao tocar)
            GestureDetector(
              onTap: () => _renamePlayer(player),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: isWinning ? Colors.red.withOpacity(0.1) : Colors.grey[200],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: isWinning ? Colors.red : Colors.grey,
                    width: 2,
                  ),
                ),
                child: Text(
                  player.name,
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: isWinning ? Colors.red[700] : Colors.black87,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),
            // Pontuação animada
            AnimatedFlipCounter(
              duration: const Duration(milliseconds: 300),
              value: player.points,
              textStyle: TextStyle(
                fontSize: 64,
                fontWeight: FontWeight.bold,
                color: player.points == _maoDeOnzePoints ? Colors.red : Colors.black87,
              ),
            ),
            const SizedBox(height: 16),
            // Contador de vitórias destacado
            _buildVictoryCounter(player),
            const SizedBox(height: 24),
            // Botões de controle (adicionar/remover ponto, truco)
            _buildControlButtons(player),
          ],
        ),
      ),
    );
  }

  // Widget para o contador de vitórias
  Widget _buildVictoryCounter(Player player) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Colors.black87, Colors.grey],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Text(
        'Vitórias: ${player.victories}',
        style: const TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
    );
  }

  // Botões de adicionar/remover ponto e truco
  Widget _buildControlButtons(Player player) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _buildActionButton(
              icon: Icons.add,
              onPressed: () => _addPoint(player),
              color: Colors.red,
              tooltip: 'Adicionar ponto',
            ),
            _buildActionButton(
              icon: Icons.remove,
              onPressed: player.points > 0 ? () => _subtractPoint(player) : null,
              color: Colors.grey[700]!,
              tooltip: 'Remover ponto',
            ),
          ],
        ),
        const SizedBox(height: 12),
        // Botão de Truco, só habilitado se possível
        ElevatedButton.icon(
          onPressed: player.points <= (_maxPoints - _trucoPoints) 
              ? () => _addTrucoPoints(player) 
              : null,
          icon: const Icon(Icons.whatshot),
          label: const Text('TRUCO!'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            textStyle: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }

  // Botão de ação (add/remove ponto)
  Widget _buildActionButton({
    required IconData icon,
    required VoidCallback? onPressed,
    required Color color,
    required String tooltip,
  }) {
    return FloatingActionButton(
      onPressed: onPressed,
      backgroundColor: color,
      heroTag: '$tooltip${icon.codePoint}',
      tooltip: tooltip,
      child: Icon(icon, color: Colors.white),
    );
  }

  // Lista de histórico estilizada
  Widget _buildHistoryList() {
    if (_history.isEmpty) {
      return const Center(
        child: Text(
          'Nenhuma ação registrada ainda',
          style: TextStyle(fontSize: 16, color: Colors.grey),
        ),
      );
    }

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Histórico da Partida',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              if (_history.isNotEmpty)
                TextButton.icon(
                  onPressed: _undoLastAction,
                  icon: const Icon(Icons.undo),
                  label: const Text('Desfazer'),
                ),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            itemCount: _history.length,
            reverse: true,
            itemBuilder: (context, index) {
              final entry = _history[_history.length - 1 - index];
              final isTeamA = entry.playerName == _teamA.name;
              
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: isTeamA ? Colors.red : Colors.grey[700],
                    child: Text(
                      entry.playerName[0].toUpperCase(),
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                  ),
                  title: Text(
                    '${entry.playerName}: ${entry.action}',
                    style: const TextStyle(fontWeight: FontWeight.w500),
                  ),
                  subtitle: Text(entry.formattedTime),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  // Mostra o diálogo com as regras do truco
  void _showRulesDialog() {
    showDialog(
      context: context,
      builder: (_) => Dialog(
        backgroundColor: Colors.grey[900],
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.help_outline, color: Colors.red, size: 28),
                  SizedBox(width: 8),
                  Text(
                    'Regras do Truco',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Text(
                '🎯 Objetivo:\n• Primeiro time a fazer 12 pontos vence\n',
                style: TextStyle(color: Colors.grey[300]),
              ),
              Text(
                '⚡ Pontuação:\n• Rodada normal: 1 ponto\n• Truco aceito: 3 pontos\n',
                style: TextStyle(color: Colors.grey[300]),
              ),
              Text(
                '🔥 Mão de Onze:\n• Quando ambos chegam a 11 pontos\n• Próxima rodada decide o jogo\n',
                style: TextStyle(color: Colors.grey[300]),
              ),
              Text(
                '🎮 Dicas do App:\n• Toque no nome para alterá-lo\n• Use "Desfazer" para corrigir erros\n• Acompanhe o histórico na parte inferior',
                style: TextStyle(color: Colors.grey[300]),
              ),
              const SizedBox(height: 24),
              Center(
                child: ElevatedButton(
                  onPressed: () => Navigator.of(context).pop(),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Entendi'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Monta a tela principal
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.black87,
        elevation: 4,
        centerTitle: true,
        title: const Text(
          'Marcador de Truco',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 22,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline, color: Colors.red),
            onPressed: _showRulesDialog,
            tooltip: 'Regras',
          ),
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.red),
            onPressed: _resetGame,
            tooltip: 'Resetar jogo',
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            flex: 2,
            child: Row(
              children: [
                _buildPlayerColumn(_teamA),
                Container(
                  width: 2,
                  color: Colors.grey[600],
                  margin: const EdgeInsets.symmetric(vertical: 20),
                ),
                _buildPlayerColumn(_teamB),
              ],
            ),
          ),
          Container(
            height: 2,
            color: Colors.grey[600],
          ),
          Expanded(
            flex: 1,
            child: _buildHistoryList(),
          ),
        ],
      ),
    );
  }
}