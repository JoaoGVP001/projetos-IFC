import 'package:flutter/material.dart';
import 'package:sigilrpg/models/character_class.dart';
import 'package:sigilrpg/models/character_origin.dart';
import 'package:sigilrpg/models/character.dart';

class CharacterCreateView extends StatefulWidget {
  const CharacterCreateView({super.key});

  @override
  State<CharacterCreateView> createState() => _CharacterCreateViewState();
}

class _CharacterCreateViewState extends State<CharacterCreateView> {
  int _currentStep = 0;

  // Step 1: Básicas
  final _formBasics = GlobalKey<FormState>();
  final TextEditingController _nameCtrl = TextEditingController();
  final TextEditingController _playerCtrl = TextEditingController();
  int _nex = 5;
  String? _avatarUrl;

  // Step 2: Atributos (sistema novo)
  int _agi = 1, _int = 1, _vig = 1, _pre = 1, _for = 1;
  int get _attributesTotal => _agi + _int + _vig + _pre + _for;
  int get _pointsAvailable =>
      4 -
      (_attributesTotal - 5); // 4 pontos para distribuir, todos começam em 1

  // Step 3: Classe
  CharacterClass? _selectedClass;

  // Step 4: Origem
  CharacterOrigin? _selectedOrigin;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Criar Personagem')),
      body: Stepper(
        currentStep: _currentStep,
        type: StepperType.vertical,
        onStepTapped: (i) => setState(() => _currentStep = i),
        onStepContinue: _onContinue,
        onStepCancel: _onBack,
        controlsBuilder: (context, details) {
          final isLast = _currentStep == 3;
          return Row(
            children: [
              ElevatedButton(
                onPressed: details.onStepContinue,
                child: Text(isLast ? 'Concluir' : 'Continuar'),
              ),
              const SizedBox(width: 12),
              if (_currentStep > 0)
                TextButton(
                  onPressed: details.onStepCancel,
                  child: const Text('Voltar'),
                ),
            ],
          );
        },
        steps: [
          Step(
            title: const Text('Informações Básicas'),
            isActive: _currentStep >= 0,
            state: _stepState(0),
            content: Form(
              key: _formBasics,
              child: Column(
                children: [
                  TextFormField(
                    controller: _nameCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Nome do Personagem',
                    ),
                    validator: (v) => (v == null || v.trim().isEmpty)
                        ? 'Informe o nome'
                        : null,
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _playerCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Jogador Responsável',
                    ),
                    validator: (v) => (v == null || v.trim().isEmpty)
                        ? 'Informe o jogador'
                        : null,
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      const Text('NEX:'),
                      Expanded(
                        child: Slider(
                          min: 5,
                          max: 50,
                          divisions: 9,
                          value: _nex.toDouble(),
                          label: '$_nex%',
                          onChanged: (v) => setState(() => _nex = v.round()),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    decoration: const InputDecoration(
                      labelText: 'Avatar URL (opcional)',
                    ),
                    onChanged: (v) =>
                        _avatarUrl = v.trim().isEmpty ? null : v.trim(),
                  ),
                ],
              ),
            ),
          ),
          Step(
            title: const Text('Atributos'),
            isActive: _currentStep >= 1,
            state: _stepState(1),
            content: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surfaceVariant,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    'Quando você cria um personagem, todos os seus atributos começam em 1 e você recebe 4 pontos para distribuir entre eles como quiser. Você também pode reduzir um atributo para 0 para receber 1 ponto adicional. O valor máximo inicial que você pode ter em cada atributo é 3.',
                    style: TextStyle(fontSize: 14),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  'Pontos disponíveis: ${_pointsAvailable >= 0 ? _pointsAvailable : 0}',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                _attrRow('AGI', _agi, (v) => setState(() => _agi = v)),
                _attrRow('INT', _int, (v) => setState(() => _int = v)),
                _attrRow('VIG', _vig, (v) => setState(() => _vig = v)),
                _attrRow('PRE', _pre, (v) => setState(() => _pre = v)),
                _attrRow('FOR', _for, (v) => setState(() => _for = v)),
              ],
            ),
          ),
          Step(
            title: const Text('Classe'),
            isActive: _currentStep >= 2,
            state: _stepState(2),
            content: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surfaceVariant,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    'Sua classe indica o treinamento que você recebeu na Ordem para enfrentar os perigos do Outro Lado.\n\nEm termos de jogo, é a sua característica mais importante, pois define o que você faz e qual é o seu papel no grupo de investigadores.\n\nPerícias concedidas serão adicionadas automaticamente. Perícias opcionais podem ser adicionadas ao agente após sua criação.',
                    style: TextStyle(fontSize: 14),
                  ),
                ),
                const SizedBox(height: 16),
                ...CharacterClasses.allClasses.map(
                  (classe) => _buildClassCard(classe),
                ),
              ],
            ),
          ),
          Step(
            title: const Text('Origem'),
            isActive: _currentStep >= 3,
            state: _stepState(3),
            content: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surfaceVariant,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    'Sua origem define seu passado antes de se tornar um agente da Ordem. Cada origem oferece perícias treinadas específicas e um poder único que reflete sua experiência anterior.',
                    style: TextStyle(fontSize: 14),
                  ),
                ),
                const SizedBox(height: 16),
                Expanded(
                  child: ListView.builder(
                    itemCount: CharacterOrigins.allOrigins.length,
                    itemBuilder: (context, index) {
                      final origin = CharacterOrigins.allOrigins[index];
                      return _buildOriginCard(origin);
                    },
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildClassCard(CharacterClass classe) {
    final isSelected = _selectedClass?.name == classe.name;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => setState(() => _selectedClass = classe),
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            border: isSelected
                ? Border.all(
                    color: Theme.of(context).colorScheme.primary,
                    width: 2,
                  )
                : null,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      classe.name,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  if (isSelected)
                    Icon(
                      Icons.check_circle,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                classe.description,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 12),
              Text(
                'Famosos: ${classe.famousCharacters}',
                style: Theme.of(
                  context,
                ).textTheme.bodySmall?.copyWith(fontStyle: FontStyle.italic),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildStatInfo(
                      'PV Iniciais',
                      '${classe.stats.initialHealth}+VIGOR',
                    ),
                  ),
                  Expanded(
                    child: _buildStatInfo(
                      'PE Iniciais',
                      '${classe.stats.initialEffort}+PRESENÇA',
                    ),
                  ),
                  Expanded(
                    child: _buildStatInfo(
                      'SAN Inicial',
                      '${classe.stats.initialSanity}',
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

  Widget _buildStatInfo(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.bodySmall),
        Text(
          value,
          style: Theme.of(
            context,
          ).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold),
        ),
      ],
    );
  }

  Widget _buildOriginCard(CharacterOrigin origin) {
    final isSelected = _selectedOrigin?.name == origin.name;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => setState(() => _selectedOrigin = origin),
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            border: isSelected
                ? Border.all(
                    color: Theme.of(context).colorScheme.primary,
                    width: 2,
                  )
                : null,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      origin.name,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  if (isSelected)
                    Icon(
                      Icons.check_circle,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                origin.description,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildOriginInfo(
                      'Perícias Treinadas',
                      origin.trainedSkills.join(', '),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(child: _buildOriginInfo('Poder', origin.powerName)),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                origin.powerDescription,
                style: Theme.of(
                  context,
                ).textTheme.bodySmall?.copyWith(fontStyle: FontStyle.italic),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildOriginInfo(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(
            context,
          ).textTheme.bodySmall?.copyWith(fontWeight: FontWeight.bold),
        ),
        Text(value, style: Theme.of(context).textTheme.bodyMedium),
      ],
    );
  }

  void _onContinue() {
    if (_currentStep == 0) {
      if (!(_formBasics.currentState?.validate() ?? false)) return;
    }
    if (_currentStep == 1) {
      if (_pointsAvailable < 0) {
        _showSnack('Distribua até o limite de pontos disponíveis.');
        return;
      }
    }
    if (_currentStep == 2 && _selectedClass == null) {
      _showSnack('Selecione uma classe.');
      return;
    }
    if (_currentStep == 3 && _selectedOrigin == null) {
      _showSnack('Selecione uma origem.');
      return;
    }

    if (_currentStep < 3) {
      setState(() => _currentStep++);
      return;
    }

    // Finish
    _finish();
  }

  void _onBack() {
    if (_currentStep > 0) setState(() => _currentStep--);
  }

  void _finish() async {
    final attributes = CharacterAttributes(
      agilidade: _agi,
      intelecto: _int,
      vigor: _vig,
      presenca: _pre,
      forca: _for,
    );

    final character = Character(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      name: _nameCtrl.text,
      playerName: _playerCtrl.text,
      origin: _selectedOrigin!.name,
      characterClass: _selectedClass!.name,
      nex: _nex,
      avatarUrl: _avatarUrl,
      attributes: attributes,
    );

    await showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Personagem criado!'),
        content: Text(
          'Nome: ${character.name}\nJogador: ${character.playerName}\nClasse: ${character.characterClass}\nOrigem: ${character.origin}\nNEX: ${character.nex}%',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
    if (mounted) Navigator.pop(context);
  }

  StepState _stepState(int index) {
    if (_currentStep > index) return StepState.complete;
    return StepState.indexed;
  }

  Widget _attrRow(String label, int value, ValueChanged<int> onChanged) {
    return Row(
      children: [
        SizedBox(width: 48, child: Text(label)),
        Expanded(
          child: Slider(
            min: 0,
            max: 3,
            divisions: 3,
            label: '$value',
            value: value.toDouble(),
            onChanged: (v) => onChanged(v.round()),
          ),
        ),
        SizedBox(width: 32, child: Text('$value', textAlign: TextAlign.end)),
      ],
    );
  }

  void _showSnack(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }
}
