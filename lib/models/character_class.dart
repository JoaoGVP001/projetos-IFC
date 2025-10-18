class CharacterClass {
  final String name;
  final String description;
  final String detailedDescription;
  final String famousCharacters;
  final CharacterStats stats;
  final List<String> trainedSkills;
  final List<String> proficiencies;
  final List<ClassAbility> abilities;
  final List<ClassPath> paths;

  const CharacterClass({
    required this.name,
    required this.description,
    required this.detailedDescription,
    required this.famousCharacters,
    required this.stats,
    required this.trainedSkills,
    required this.proficiencies,
    required this.abilities,
    required this.paths,
  });
}

class CharacterStats {
  final int initialHealth;
  final String healthPerLevel;
  final int initialEffort;
  final String effortPerLevel;
  final int initialSanity;
  final String sanityPerLevel;

  const CharacterStats({
    required this.initialHealth,
    required this.healthPerLevel,
    required this.initialEffort,
    required this.effortPerLevel,
    required this.initialSanity,
    required this.sanityPerLevel,
  });
}

class ClassAbility {
  final String name;
  final String description;
  final int nexRequired;

  const ClassAbility({
    required this.name,
    required this.description,
    required this.nexRequired,
  });
}

class ClassPath {
  final String name;
  final String description;
  final List<PathAbility> abilities;

  const ClassPath({
    required this.name,
    required this.description,
    required this.abilities,
  });
}

class PathAbility {
  final String name;
  final String description;
  final int nexRequired;

  const PathAbility({
    required this.name,
    required this.description,
    required this.nexRequired,
  });
}

// Predefined classes data
class CharacterClasses {
  static const combatente = CharacterClass(
    name: 'Combatente',
    description:
        'Treinado para lutar com todo tipo de armas, e com a força e a coragem para encarar os perigos de frente',
    detailedDescription:
        '''É o tipo de agente que prefere abordagens mais diretas e costuma atirar primeiro e perguntar depois.

Do mercenário especialista em armas de fogo até o perito em espadas, combatentes apresentam uma gama enorme de habilidades e técnicas especiais que aprimoram sua eficiência no campo de batalha, tornando-os membros essenciais em qualquer missão de extermínio.

Além de treinar seu corpo, o combatente também é perito em liderar seus aliados em batalha e cuidar de seu equipamento de combate, sempre preparado para assumir a linha de frente quando a coisa fica feia.''',
    famousCharacters:
        'Senhor Veríssimo, Joui Jouki, Gal, Antônio "Balu" Pontevedra, Tristan Monteiro e Ryder Staten.',
    stats: CharacterStats(
      initialHealth: 20,
      healthPerLevel: '4 PV (+Vig)',
      initialEffort: 2,
      effortPerLevel: '2 PE (+Pre)',
      initialSanity: 12,
      sanityPerLevel: '3 SAN',
    ),
    trainedSkills: ['Luta ou Pontaria', 'Fortitude ou Reflexos'],
    proficiencies: ['Armas simples', 'táticas', 'proteções leves'],
    abilities: [
      ClassAbility(
        name: 'Ataque Especial',
        description:
            'Quando faz um ataque, você pode gastar 2 PE para receber +5 no teste de ataque ou na rolagem de dano.',
        nexRequired: 5,
      ),
      ClassAbility(
        name: 'Habilidade de Trilha',
        description:
            'Em NEX 10% você escolhe uma das trilhas de combatente e recebe o primeiro poder da trilha escolhida.',
        nexRequired: 10,
      ),
      ClassAbility(
        name: 'Poder de Combatente',
        description:
            'Em NEX 15%, você recebe um poder de combatente à sua escolha.',
        nexRequired: 15,
      ),
    ],
    paths: [
      ClassPath(
        name: 'Aniquilador',
        description:
            'Você é treinado para abater alvos com eficiência e velocidade.',
        abilities: [
          PathAbility(name: 'A Favorita', description: '', nexRequired: 10),
          PathAbility(
            name: 'Técnica Secreta',
            description: '',
            nexRequired: 40,
          ),
          PathAbility(
            name: 'Técnica Sublime',
            description: '',
            nexRequired: 65,
          ),
          PathAbility(
            name: 'Máquina de Matar',
            description: '',
            nexRequired: 99,
          ),
        ],
      ),
      ClassPath(
        name: 'Comandante de Campo',
        description:
            'Você é treinado para coordenar e auxiliar seus companheiros em combate.',
        abilities: [
          PathAbility(
            name: 'Inspirar Confiança',
            description: '',
            nexRequired: 10,
          ),
          PathAbility(name: 'Estrategista', description: '', nexRequired: 40),
          PathAbility(
            name: 'Brecha na Guarda',
            description: '',
            nexRequired: 65,
          ),
          PathAbility(
            name: 'Oficial Comandante',
            description: '',
            nexRequired: 99,
          ),
        ],
      ),
      ClassPath(
        name: 'Guerreiro',
        description:
            'Você treinou sua musculatura e movimentos a ponto de transformar seu corpo em uma verdadeira arma.',
        abilities: [
          PathAbility(name: 'Técnica Letal', description: '', nexRequired: 10),
          PathAbility(name: 'Revidar', description: '', nexRequired: 40),
          PathAbility(
            name: 'Força Opressora',
            description: '',
            nexRequired: 65,
          ),
          PathAbility(
            name: 'Potência Máxima',
            description: '',
            nexRequired: 99,
          ),
        ],
      ),
      ClassPath(
        name: 'Operações Especiais',
        description:
            'Você é um combatente eficaz, e suas ações são calculadas e otimizadas.',
        abilities: [
          PathAbility(
            name: 'Iniciativa Aprimorada',
            description: '',
            nexRequired: 10,
          ),
          PathAbility(name: 'Ataque Extra', description: '', nexRequired: 40),
          PathAbility(
            name: 'Surto de Adrenalina',
            description: '',
            nexRequired: 65,
          ),
          PathAbility(name: 'Sempre Alerta', description: '', nexRequired: 99),
        ],
      ),
      ClassPath(
        name: 'Tropa de Choque',
        description:
            'Você é duro na queda. Treinou seu corpo para resistir a traumas físicos.',
        abilities: [
          PathAbility(name: 'Casca Grossa', description: '', nexRequired: 10),
          PathAbility(name: 'Cai Dentro', description: '', nexRequired: 40),
          PathAbility(name: 'Duro de Matar', description: '', nexRequired: 65),
          PathAbility(name: 'Inquebrável', description: '', nexRequired: 99),
        ],
      ),
    ],
  );

  static const especialista = CharacterClass(
    name: 'Especialista',
    description: 'Um agente que confia mais em esperteza do que em força bruta',
    detailedDescription:
        '''Um especialista se vale de conhecimento técnico, raciocínio rápido ou mesmo lábia para resolver mistérios e enfrentar o paranormal.

Cientistas, inventores, pesquisadores e técnicos de vários tipos são exemplos de especialistas, que são tão variados quanto as áreas do conhecimento e da tecnologia. Alguns ainda preferem estudar engenharia social e se tornam excelentes espiões infiltrados, ou mesmo estudam técnicas especiais de combate como artes marciais e tiro a distância, aliando conhecimento técnico e habilidade.

O que une todos os especialistas é sua incrível capacidade de aprender e improvisar usando seu intelecto e conhecimento avançado, que pode tirar o grupo todo dos mais diversos tipos de enrascadas.''',
    famousCharacters:
        'Aaron, Arthur Cervero, Rubens Naluti, Elizabeth Webber, Samuel Norte, Chizue Akechi.',
    stats: CharacterStats(
      initialHealth: 16,
      healthPerLevel: '3 PV (+Vig)',
      initialEffort: 3,
      effortPerLevel: '3 PE (+Pre)',
      initialSanity: 16,
      sanityPerLevel: '4 SAN',
    ),
    trainedSkills: ['7 + Intelecto perícias à escolha'],
    proficiencies: ['Armas simples', 'proteções leves'],
    abilities: [
      ClassAbility(
        name: 'Eclético',
        description:
            'Quando faz um teste de uma perícia, você pode gastar 2 PE para receber os benefícios de ser treinado nesta perícia.',
        nexRequired: 5,
      ),
      ClassAbility(
        name: 'Perito',
        description:
            'Escolha duas perícias nas quais você é treinado. Quando faz um teste de uma dessas perícias, você pode gastar 2 PE para somar +1d6 no resultado do teste.',
        nexRequired: 5,
      ),
      ClassAbility(
        name: 'Habilidade de Trilha',
        description:
            'Em NEX 10% você escolhe uma das trilhas de especialista e recebe o primeiro poder da trilha escolhida.',
        nexRequired: 10,
      ),
    ],
    paths: [
      ClassPath(
        name: 'Atirador de Elite',
        description:
            'Um tiro, uma morte. Você é perito em neutralizar ameaças de longe.',
        abilities: [
          PathAbility(name: 'Mira de Elite', description: '', nexRequired: 10),
          PathAbility(name: 'Disparo Letal', description: '', nexRequired: 40),
          PathAbility(
            name: 'Disparo Impactante',
            description: '',
            nexRequired: 65,
          ),
          PathAbility(
            name: 'Atirar para Matar',
            description: '',
            nexRequired: 99,
          ),
        ],
      ),
      ClassPath(
        name: 'Infiltrador',
        description:
            'Você é um perito em infiltração e sabe neutralizar alvos desprevenidos.',
        abilities: [
          PathAbility(name: 'Ataque Furtivo', description: '', nexRequired: 10),
          PathAbility(name: 'Gatuno', description: '', nexRequired: 40),
          PathAbility(name: 'Assassinar', description: '', nexRequired: 65),
          PathAbility(name: 'Sombra Fugaz', description: '', nexRequired: 99),
        ],
      ),
      ClassPath(
        name: 'Médico de Campo',
        description:
            'Você é treinado em técnicas de primeiros socorros e tratamento de emergência.',
        abilities: [
          PathAbility(name: 'Paramédico', description: '', nexRequired: 10),
          PathAbility(
            name: 'Equipe de Trauma',
            description: '',
            nexRequired: 40,
          ),
          PathAbility(name: 'Resgate', description: '', nexRequired: 65),
          PathAbility(name: 'Reanimação', description: '', nexRequired: 99),
        ],
      ),
      ClassPath(
        name: 'Negociador',
        description:
            'Você é um diplomata habilidoso e consegue influenciar outras pessoas.',
        abilities: [
          PathAbility(name: 'Eloquência', description: '', nexRequired: 10),
          PathAbility(
            name: 'Discurso Motivador',
            description: '',
            nexRequired: 40,
          ),
          PathAbility(
            name: 'Eu Conheço um Cara',
            description: '',
            nexRequired: 65,
          ),
          PathAbility(
            name: 'Truque de Mestre',
            description: '',
            nexRequired: 99,
          ),
        ],
      ),
      ClassPath(
        name: 'Técnico',
        description:
            'Sua principal habilidade é a manutenção e reparo do valioso equipamento.',
        abilities: [
          PathAbility(
            name: 'Inventário Otimizado',
            description: '',
            nexRequired: 10,
          ),
          PathAbility(name: 'Remendão', description: '', nexRequired: 40),
          PathAbility(name: 'Improvisar', description: '', nexRequired: 65),
          PathAbility(
            name: 'Preparado para Tudo',
            description: '',
            nexRequired: 99,
          ),
        ],
      ),
    ],
  );

  static const ocultista = CharacterClass(
    name: 'Ocultista',
    description:
        'Muitos estudiosos das entidades se perdem em seus reinos obscuros em busca de poder',
    detailedDescription:
        '''Mas existem aqueles que visam compreender e dominar os mistérios paranormais para usá-los para combater o próprio Outro Lado. Esse tipo de agente não é apenas um conhecedor do oculto, como também possui talento para se conectar com elementos paranormais.

Ao contrário da crendice popular, ocultistas não são intrinsecamente malignos. Seria como dizer que o cientista que inventou a pólvora é culpado pelo assassino que disparou o revólver. Para a Ordem, o Paranormal é uma força que pode ser usada para os mais diversos propósitos, de acordo com a intenção de seu usuário.

Ocultistas aplicam seu conhecimento acadêmico e suas capacidades de conjuração de rituais em missões para investigar e combater o Paranormal em todas as suas formas, principalmente quando munição convencional não é o suficiente para lidar com a tarefa.''',
    famousCharacters:
        'Agatha Volkomenn, Dante, Arnaldo Fritz, Marc Menet, Kian.',
    stats: CharacterStats(
      initialHealth: 12,
      healthPerLevel: '2 PV (+Vig)',
      initialEffort: 4,
      effortPerLevel: '4 PE (+Pre)',
      initialSanity: 20,
      sanityPerLevel: '5 SAN',
    ),
    trainedSkills: ['Ocultismo', 'Vontade', '3 + Intelecto perícias à escolha'],
    proficiencies: ['Armas simples'],
    abilities: [
      ClassAbility(
        name: 'Escolhido pelo Outro Lado',
        description:
            'Você pode lançar rituais de 1º círculo. À medida que aumenta seu NEX, pode lançar rituais de círculos maiores.',
        nexRequired: 5,
      ),
      ClassAbility(
        name: 'Habilidade de Trilha',
        description:
            'Em NEX 10% você escolhe uma das trilhas de ocultista e recebe o primeiro poder da trilha escolhida.',
        nexRequired: 10,
      ),
      ClassAbility(
        name: 'Poder de Ocultista',
        description:
            'Em NEX 15%, você recebe um poder de ocultista à sua escolha.',
        nexRequired: 15,
      ),
    ],
    paths: [
      ClassPath(
        name: 'Conduíte',
        description:
            'Você domina os aspectos fundamentais da conjuração de rituais.',
        abilities: [
          PathAbility(name: 'Ampliar Ritual', description: '', nexRequired: 10),
          PathAbility(
            name: 'Acelerar Ritual',
            description: '',
            nexRequired: 40,
          ),
          PathAbility(name: 'Anular Ritual', description: '', nexRequired: 65),
          PathAbility(
            name: 'Canalizar o Medo',
            description: '',
            nexRequired: 99,
          ),
        ],
      ),
      ClassPath(
        name: 'Flagelador',
        description:
            'Dor é um poderoso catalisador Paranormal e você aprendeu a transformá-la em poder.',
        abilities: [
          PathAbility(
            name: 'Poder do Flagelo',
            description: '',
            nexRequired: 10,
          ),
          PathAbility(name: 'Abraçar a Dor', description: '', nexRequired: 40),
          PathAbility(
            name: 'Absorver Agonia',
            description: '',
            nexRequired: 65,
          ),
          PathAbility(name: 'Medo Tangível', description: '', nexRequired: 99),
        ],
      ),
      ClassPath(
        name: 'Graduado',
        description:
            'Você foca seus estudos em se tornar um conjurador versátil e poderoso.',
        abilities: [
          PathAbility(name: 'Saber Ampliado', description: '', nexRequired: 10),
          PathAbility(
            name: 'Grimório Ritualístico',
            description: '',
            nexRequired: 40,
          ),
          PathAbility(
            name: 'Rituais Eficientes',
            description: '',
            nexRequired: 65,
          ),
          PathAbility(
            name: 'Conhecendo o Medo',
            description: '',
            nexRequired: 99,
          ),
        ],
      ),
      ClassPath(
        name: 'Intuitivo',
        description:
            'Você preparou sua mente para resistir aos efeitos do Outro Lado.',
        abilities: [
          PathAbility(name: 'Mente Sã', description: '', nexRequired: 10),
          PathAbility(
            name: 'Presença Poderosa',
            description: '',
            nexRequired: 40,
          ),
          PathAbility(name: 'Inabalável', description: '', nexRequired: 65),
          PathAbility(
            name: 'Presença do Medo',
            description: '',
            nexRequired: 99,
          ),
        ],
      ),
      ClassPath(
        name: 'Lâmina Paranormal',
        description:
            'Você aprendeu e dominou técnicas de luta mesclando suas habilidades de conjuração.',
        abilities: [
          PathAbility(name: 'Lâmina Maldita', description: '', nexRequired: 10),
          PathAbility(
            name: 'Gladiador Paranormal',
            description: '',
            nexRequired: 40,
          ),
          PathAbility(
            name: 'Conjuração Marcial',
            description: '',
            nexRequired: 65,
          ),
          PathAbility(name: 'Lâmina do Medo', description: '', nexRequired: 99),
        ],
      ),
    ],
  );

  static const List<CharacterClass> allClasses = [
    combatente,
    especialista,
    ocultista,
  ];
}
