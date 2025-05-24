import 'package:flutter/material.dart';
import 'package:animated_flip_counter/animated_flip_counter.dart';
import 'package:flutter_slidable/flutter_slidable.dart';

void main() {
  runApp(MarcadorTrucoApp());
}

class MarcadorTrucoApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: SplashScreen(), // Inicia com a splash em Dart
      debugShowCheckedModeBanner: false,
    );
  }
}

// ========================
// Splash Screen em Dart
// ========================
class SplashScreen extends StatefulWidget {
  @override
  _SplashScreenState createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    Future.delayed(Duration(seconds: 2), () {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => HomePage()),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.red,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset(
              'assets/logo.png',
              width: 200, // aumente aqui (exemplo: 200)
              // height: 200, // opcional, se quiser definir altura também
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
            CircularProgressIndicator(color: Colors.white),
          ],
        ),
      ),
    );
  }
}

class Player {
  String name;
  int points;
  int victories;
  Player({required this.name, this.points = 0, this.victories = 0});
}

class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  Player teamA = Player(name: 'Nós');
  Player teamB = Player(name: 'Eles');

  List<String> history = [];

  void addPoint(Player player) {
    if (player.points < 12) {
      setState(() {
        player.points++;
        history.add(
          '${player.name} - ${_formatNow()}: +1 ponto'
        );
        checkVictory(player);
        checkMaoDeOnze();
      });
    }
  }

  void subtractPoint(Player player) {
    if (player.points > 0) {
      setState(() {
        player.points--;
        history.add(
          '${player.name} - ${_formatNow()}: -1 ponto'
        );
      });
    }
  }

  void addTrucoPoints(Player player) {
    if (player.points <= 9) {
      setState(() {
        player.points += 3;
        if (player.points > 12) player.points = 12;
        history.add(
          '${player.name} - ${_formatNow()}: +3 pontos (Truco)'
        );
        checkVictory(player);
        checkMaoDeOnze();
      });
    }
  }

  void checkVictory(Player player) {
    if (player.points == 12) {
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: Text('${player.name} venceu!'),
          actions: [
            TextButton(
              onPressed: () {
                setState(() {
                  player.victories++;
                  teamA.points = 0;
                  teamB.points = 0;
                  history.clear();
                });
                Navigator.of(context).pop();
              },
              child: Text('OK'),
            ),
          ],
        ),
      );
    }
  }

  void checkMaoDeOnze() {
    if (teamA.points == 11 && teamB.points == 11) {
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: Text('Mão de Onze!'),
          content: Text('Ambos os times chegaram a 11 pontos!'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text('OK'),
            ),
          ],
        ),
      );
    }
  }

  void renamePlayer(Player player) {
    final controller = TextEditingController(text: player.name);
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text('Alterar nome'),
        content: TextField(controller: controller),
        actions: [
          TextButton(
            onPressed: () {
              setState(() => player.name = controller.text);
              Navigator.of(context).pop();
            },
            child: Text('Salvar'),
          ),
        ],
      ),
    );
  }

  void resetPoints() {
    setState(() {
      teamA.points = 0;
      teamB.points = 0;
      teamA.victories = 0; // Zera vitórias do time A
      teamB.victories = 0; // Zera vitórias do time B
      history.clear();
    });
  }

  void undoLastAction() {
    if (history.isEmpty) return;
    final last = history.removeLast();
    setState(() {
      if (last.contains('+1')) {
        if (last.startsWith(teamA.name)) teamA.points--;
        if (last.startsWith(teamB.name)) teamB.points--;
      } else if (last.contains('-1')) {
        if (last.startsWith(teamA.name)) teamA.points++;
        if (last.startsWith(teamB.name)) teamB.points++;
      }
    });
  }

  Widget buildPlayerColumn(Player player) {
    return Expanded(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          GestureDetector(
            onTap: () => renamePlayer(player),
            child: Text(player.name, style: TextStyle(fontSize: 24)),
          ),
          AnimatedFlipCounter(
            duration: Duration(milliseconds: 250),
            value: player.points,
            textStyle: TextStyle(fontSize: 40),
          ),
          Container(
            margin: EdgeInsets.symmetric(vertical: 12),
            padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.red,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black26,
                  blurRadius: 6,
                  offset: Offset(0, 3),
                ),
              ],
            ),
            child: Text(
              'Vitórias: ${player.victories}',
              style: TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.bold,
                color: Colors.white,
                letterSpacing: 1.2,
                shadows: [
                  Shadow(
                    color: Colors.black38,
                    blurRadius: 4,
                    offset: Offset(1, 2),
                  ),
                ],
              ),
              textAlign: TextAlign.center,
            ),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                onPressed: () => addPoint(player),
                icon: Icon(Icons.add),
              ),
              IconButton(
                onPressed: () => subtractPoint(player),
                icon: Icon(Icons.remove),
              ),
            ],
          ),
          SizedBox(height: 10),
          ElevatedButton(
            onPressed: () => addTrucoPoints(player),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.grey,
              foregroundColor: Colors.white,
              padding: EdgeInsets.symmetric(horizontal: 18, vertical: 10),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              textStyle: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.2,
              ),
            ),
            child: Text('Truco!'),
          ),
        ],
      ),
    );
  }

  Widget buildHistoryList() {
    return ListView.builder(
      itemCount: history.length,
      itemBuilder: (context, index) {
        final item = history[index];

        // Detecta o time pelo início da string
        Color? teamColor;
        String teamAName = teamA.name;
        String teamBName = teamB.name;
        if (item.startsWith('$teamAName -')) {
          teamColor = Colors.blue[700];
        } else if (item.startsWith('$teamBName -')) {
          teamColor = Colors.green[700];
        } else {
          teamColor = Colors.black87;
        }

        return Card(
          margin: EdgeInsets.symmetric(vertical: 6, horizontal: 12),
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Nome do time e ação (maior e colorido)
                Expanded(
                  child: Text(
                    // Nome do time + ação, sem cortar a hora!
                    '${item.split(' - ')[0]}: ${item.split(': ').sublist(1).join(': ')}',
                    style: TextStyle(
                      color: teamColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 20,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                SizedBox(width: 10),
                // Caixinha para data/hora
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.grey[400]!),
                  ),
                  child: Text(
                    // Data e hora certinho
                    item.split(' - ')[1].split(': ').first,
                    style: TextStyle(
                      color: Colors.black87,
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  String _formatNow() {
    final now = DateTime.now();
    return '${_pad2(now.day)}/${_pad2(now.month)}/${now.year} ${_pad2(now.hour)}:${_pad2(now.minute)}:${_pad2(now.second)}';
  }

  String _pad2(int n) => n.toString().padLeft(2, '0');

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.red,
        centerTitle: true,
        title: Text(
          'Marcador de Truco',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 24,
            letterSpacing: 1.2,
          ),
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.help_outline),
            tooltip: 'Regras do Truco',
            onPressed: () {
              showDialog(
                context: context,
                builder: (_) => AlertDialog(
                  title: Text('Regras Básicas do Truco'),
                  content: SingleChildScrollView(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('• O objetivo é fazer 12 pontos antes do adversário.\n'),
                        Text('• Cada rodada vale 1 ponto, mas pode valer 3 (Truco!).\n'),
                        Text('• O Truco pode ser pedido a qualquer momento, e o adversário pode aceitar, recusar (você ganha 1 ponto) ou pedir 6.\n'),
                        Text('• Se ambos os times chegarem a 11 pontos, é a "Mão de Onze".\n'),
                        Text('• O jogo é jogado em duplas ou individualmente.\n'),
                        Text('• Para mais detalhes, consulte as regras oficiais da sua região.'),
                      ],
                    ),
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.of(context).pop(),
                      child: Text('Fechar'),
                    ),
                  ],
                ),
              );
            },
          ),
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: resetPoints,
            tooltip: 'Resetar placar',
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Row(
              children: [
                buildPlayerColumn(teamA),
                VerticalDivider(),
                buildPlayerColumn(teamB),
              ],
            ),
          ),
          Divider(),
          Expanded(child: buildHistoryList()),
        ],
      ),
    );
  }
}
