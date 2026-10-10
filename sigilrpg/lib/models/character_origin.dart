class CharacterOrigin {
  final String name;
  final String description;
  final List<String> trainedSkills;
  final String powerName;
  final String powerDescription;

  const CharacterOrigin({
    required this.name,
    required this.description,
    required this.trainedSkills,
    required this.powerName,
    required this.powerDescription,
  });
}

// Predefined origins data
class CharacterOrigins {
  // Origens do Livro "Iniciação"
  static const academico = CharacterOrigin(
    name: 'Acadêmico',
    description:
        'Você era um pesquisador ou professor universitário. De forma proposital ou não, seus estudos tocaram em assuntos misteriosos e chamaram a atenção da Ordo Realitas.',
    trainedSkills: ['Ciências', 'Investigação'],
    powerName: 'Saber é Poder',
    powerDescription:
        'Ao gastar 2 PE num teste de Intelecto, recebe +5 naquele teste',
  );

  static const agenteSaude = CharacterOrigin(
    name: 'Agente de Saúde',
    description:
        'Você era um profissional da saúde como um enfermeiro, farmacêutico, médico, psicólogo ou socorrista, treinado no atendimento e cuidado de pessoas.',
    trainedSkills: ['Intuição', 'Medicina'],
    powerName: 'Técnica Medicinal',
    powerDescription: 'Ao curar alguém, adiciona seu Intelecto aos PV curados',
  );

  static const amnesico = CharacterOrigin(
    name: 'Amnésico',
    description:
        'Você perdeu a maior parte da memória. Sabe apenas o próprio nome, ou nem isso. Sua amnésia pode ser resultado de um trauma paranormal ou mesmo de um ritual.',
    trainedSkills: ['Duas à escolha do mestre'],
    powerName: 'Vislumbres do Passado',
    powerDescription:
        'Uma vez por sessão pode fazer teste de Intelecto (DT 10) para reconhecer pessoas ou lugares familiares; se passar, ganha 1d4 PE temporários e informação útil a critério do mestre',
  );

  static const artista = CharacterOrigin(
    name: 'Artista',
    description:
        'Você era um ator, músico, escritor, dançarino, influenciador... Seu trabalho pode ter sido inspirado por uma experiência paranormal do passado.',
    trainedSkills: ['Artes', 'Enganação'],
    powerName: 'Magnum Opus',
    powerDescription:
        'É famoso por uma de suas obras; uma vez por missão pode determinar que um personagem reconheça você, ganhando +5 em testes de Presença e perícias baseadas em Presença contra ele',
  );

  static const atleta = CharacterOrigin(
    name: 'Atleta',
    description:
        'Você competia em um esporte individual ou por equipe, como natação ou futebol. Seu alto desempenho pode ser fruto de alguma influência paranormal.',
    trainedSkills: ['Acrobacia', 'Atletismo'],
    powerName: '110%',
    powerDescription:
        'Ao fazer um teste de perícia usando Força ou Agilidade (exceto Luta e Pontaria), pode gastar 2 PE para receber +5 nesse teste',
  );

  static const chef = CharacterOrigin(
    name: 'Chef',
    description:
        'Você é um cozinheiro amador ou profissional. Talvez trabalhasse em um restaurante, talvez simplesmente gostasse de cozinhar para a família e amigos.',
    trainedSkills: ['Fortitude', 'Profissão – cozinheiro'],
    powerName: 'Ingrediente Secreto',
    powerDescription:
        'Em Interlúdios, você pode usar a ação alimentar-se para cozinhar um prato especial; você e os aliados que fizerem essa ação recebem dois Benefícios de Refeição acumulados',
  );

  static const investigador = CharacterOrigin(
    name: 'Investigador',
    description:
        'Você era um investigador do governo, como um perito forense ou policial federal, ou privado, como um detetive particular.',
    trainedSkills: ['Investigação', 'Percepção'],
    powerName: 'Faro para Pistas',
    powerDescription:
        'Uma vez por cena, ao fazer teste para procurar pistas, pode gastar 1 PE para receber +5 nesse teste',
  );

  static const lutador = CharacterOrigin(
    name: 'Lutador',
    description:
        'Você pratica uma arte marcial ou esporte de luta, ou cresceu em um bairro perigoso onde aprendeu briga de rua.',
    trainedSkills: ['Luta', 'Reflexos'],
    powerName: 'Mão Pesada',
    powerDescription: 'Recebe +2 em rolagens de dano com ataques corpo a corpo',
  );

  static const magnata = CharacterOrigin(
    name: 'Magnata',
    description:
        'Você possui muito dinheiro ou patrimônio. Pode ser o herdeiro de uma família antiga ligada ao oculto, ter criado e vendido uma empresa.',
    trainedSkills: ['Diplomacia', 'Pilotagem'],
    powerName: 'Patrocinador da Ordem',
    powerDescription:
        'Seu limite de crédito é sempre considerado 1 acima do atual',
  );

  static const mercenario = CharacterOrigin(
    name: 'Mercenário',
    description:
        'Você é um soldado de aluguel, que trabalha sozinho ou como parte de alguma organização que vende serviços militares.',
    trainedSkills: ['Iniciativa', 'Intimidação'],
    powerName: 'Posição de Combate',
    powerDescription:
        'No primeiro turno de cada cena de ação, pode gastar 2 PE para receber uma ação de movimento adicional',
  );

  static const militar = CharacterOrigin(
    name: 'Militar',
    description:
        'Você serviu em uma força militar, como o exército ou a marinha. Passou muito tempo treinando com armas de fogo, até se tornar um perito no uso delas.',
    trainedSkills: ['Pontaria', 'Tática'],
    powerName: 'Para Bellum',
    powerDescription: 'Recebe +2 em rolagens de dano com armas de fogo',
  );

  static const operario = CharacterOrigin(
    name: 'Operário',
    description:
        'Pedreiro, operário de fábrica ou operador de máquinas: você passou parte da vida em emprego braçal, atividades práticas que lhe deram visão pragmática do mundo.',
    trainedSkills: ['Fortitude', 'Profissão'],
    powerName: 'Ferramentas de Trabalho',
    powerDescription:
        'Escolha uma arma simples ou tática; você sabe usá-la e recebe +1 em ataque, dano e margem de ameaça com essa arma',
  );

  static const policial = CharacterOrigin(
    name: 'Policial',
    description:
        'Você fez parte de uma força de segurança pública, civil ou militar. Em alguma patrulha ou chamado se deparou com um caso paranormal.',
    trainedSkills: ['Percepção', 'Pontaria'],
    powerName: 'Patrulha',
    powerDescription: 'Recebe +2 em Defesa',
  );

  static const religioso = CharacterOrigin(
    name: 'Religioso',
    description:
        'Você é devoto ou sacerdote de uma fé. Independentemente da religião que pratica, se dedica a auxiliar as pessoas com problemas espirituais.',
    trainedSkills: ['Religião', 'Vontade'],
    powerName: 'Acalentar',
    powerDescription:
        'Recebe +5 em testes de Religião para acalmar; ao acalmar alguém, ela recupera 1d6 + sua Presença em Sanidade',
  );

  static const servidorPublico = CharacterOrigin(
    name: 'Servidor Público',
    description:
        'Você possuía carreira em um órgão do governo, lidando com burocracia e atendendo pessoas. Sua rotina foi quebrada quando você viu que o prefeito era um cultista.',
    trainedSkills: ['Intuição', 'Vontade'],
    powerName: 'Espírito Cívico',
    powerDescription:
        'Ao ajudar alguém em missão, pode gastar 1 PE para aumentar em +2 o bônus concedido nesse teste',
  );

  // Novas Origens do Suplemento "Sobrevivendo ao Horror"
  static const amigoAnimais = CharacterOrigin(
    name: 'Amigo dos Animais',
    description:
        'Você desenvolveu uma conexão muito forte com outros seres: os animais. Seja por nunca ter se dado muito bem com humanos ou por preferir a companhia de um melhor amigo de quatro patas.',
    trainedSkills: ['Adestramento', 'Percepção'],
    powerName: 'Conexão Animal',
    powerDescription:
        'Você pode se comunicar basicamente com animais e recebe +2 em testes de Adestramento',
  );

  static const astronauta = CharacterOrigin(
    name: 'Astronauta',
    description:
        'Outrora limitada a membros de algumas agências espaciais estatais, a profissão de explorador espacial se tornou mais acessível. E foi na escuridão do espaço que você descobriu que não estamos sozinhos.',
    trainedSkills: ['Ciências', 'Fortitude'],
    powerName: 'Acostumado ao Extremo',
    powerDescription:
        'Ao sofrer dano de fogo, frio ou mental, pode gastar 1 PE para reduzir esse dano em 5; cada uso extra na mesma cena aumenta o custo em +1 PE',
  );

  static const chefOutroLado = CharacterOrigin(
    name: 'Chef do Outro Lado',
    description:
        'Você nunca foi muito bom na culinária convencional. Depois de sobreviver ao paranormal, entretanto, descobriu um talento que é considerado um grande tabu até mesmo pelos ocultistas mais experientes: cozinhar e ingerir entidades do Outro Lado.',
    trainedSkills: ['Ocultismo', 'Profissão – cozinheiro'],
    powerName: 'Fome do Outro Lado',
    powerDescription:
        'Pode usar partes de criaturas do Outro Lado como ingredientes. No início de cada missão, consegue ingredientes de Categoria I (0,5 espaço cada)',
  );

  static const colegial = CharacterOrigin(
    name: 'Colegial',
    description:
        'Você era um aluno do colegial e tinha uma rotina baseada nos estudos, nas amizades e nos dramas típicos de alguém da sua idade, até que um encontro com o paranormal mudou sua vida.',
    trainedSkills: ['Atualidades', 'Tecnologia'],
    powerName: 'Poder da Amizade',
    powerDescription:
        'Escolha um aliado como melhor amigo; quando estiverem em alcance médio um do outro e puderem trocar olhares, você recebe +2 em todos os testes de perícia',
  );

  static const cosplayer = CharacterOrigin(
    name: 'Cosplayer',
    description:
        'Você é apaixonado pela arte do cosplay e dedicou sua vida a criar a melhor fantasia possível. Confrontado com o paranormal, você colocou sua arte, e sua resiliência, a serviço da Ordem.',
    trainedSkills: ['Artes', 'Vontade'],
    powerName: 'Não É Fantasia, É Cosplay!',
    powerDescription:
        'Você pode fazer testes de Disfarce usando Artes em vez de Enganação; além disso, se estiver vestido com um cosplay relacionado à perícia que estiver testando, recebe +2 neste teste',
  );

  static const diplomata = CharacterOrigin(
    name: 'Diplomata',
    description:
        'Você atuava em uma área onde as habilidades sociais e políticas eram ferramentas indispensáveis. Em algum momento, entretanto, você teve uma experiência paranormal que revelou entidades com as quais não se é possível negociar.',
    trainedSkills: ['Atualidades', 'Diplomacia'],
    powerName: 'Conexões',
    powerDescription:
        'Recebe +2 em testes de Diplomacia. Além disso, se puder contatar um NPC capaz de auxiliar, pode gastar 10 minutos e 2 PE para substituir um teste de perícia relacionado ao conhecimento desse NPC por um teste de Diplomacia',
  );

  static const explorador = CharacterOrigin(
    name: 'Explorador',
    description:
        'Você é uma pessoa que se interessa muito por história ou geografia, frequentemente embarcando em trilhas e explorações para enriquecer seus estudos.',
    trainedSkills: ['Fortitude', 'Sobrevivência'],
    powerName: 'Manual do Sobrevivente',
    powerDescription:
        'Ao fazer teste para resistir a armadilhas, clima, doenças, fome, sede, fumaça, sono, sufocamento ou veneno, pode gastar 2 PE para receber +5 nesse teste',
  );

  static const experimento = CharacterOrigin(
    name: 'Experimento',
    description:
        'Você foi uma cobaia em um experimento físico. Qualquer que seja a natureza desse evento, causou alterações permanentes em seu corpo, como um cheiro forte de químicos, cicatrizes ou manchas estranhas.',
    trainedSkills: ['Atletismo', 'Fortitude'],
    powerName: 'Mutação',
    powerDescription:
        'Você recebe Resistência a dano 2 e +2 em uma perícia escolhida originalmente baseada em Força, Agilidade ou Vigor; entretanto, sofre –2 em Diplomacia',
  );

  static const fanaticoCriaturas = CharacterOrigin(
    name: 'Fanático por Criaturas',
    description:
        'Você sempre foi obcecado pelo sobrenatural. Desde que pode se lembrar, a ideia de encontrar uma criatura o fascina tanto quanto o assusta.',
    trainedSkills: ['Investigação', 'Ocultismo'],
    powerName: 'Conhecimento Oculto',
    powerDescription:
        'Ao fazer teste de Ocultismo para identificar uma criatura, se passar descobre características da criatura mas não seu tipo. Além disso, ao passar nesse teste de Ocultismo, recebe +2 em todos os testes contra aquela criatura até o fim da missão',
  );

  static const fotografo = CharacterOrigin(
    name: 'Fotógrafo',
    description:
        'Você é um artista visual que usa câmeras para capturar momentos e transmitir histórias através de imagens estáticas. Você não fazia ideia de que encontraria elementos paranormais através de sua lente.',
    trainedSkills: ['Artes', 'Percepção'],
    powerName: 'Através da Lente',
    powerDescription:
        'Ao fazer teste de Investigação ou Percepção para adquirir pistas olhando através de uma câmera ou analisando fotos, pode gastar 2 PE para receber +5 nesse teste',
  );

  static const inventorParanormal = CharacterOrigin(
    name: 'Inventor Paranormal',
    description:
        'A curiosidade e a criatividade fizeram de você uma pessoa que busca constantemente desafiar limites e criar soluções inovadoras, sendo mais de uma vez intitulado como um "cientista louco".',
    trainedSkills: ['Profissão – engenheiro', 'Vontade'],
    powerName: 'Invenção Paranormal',
    powerDescription:
        'Escolha um ritual de 1º círculo; você possui um invento (item categoria 0) que permite executar o efeito desse ritual',
  );

  static const jovemMistico = CharacterOrigin(
    name: 'Jovem Místico',
    description:
        'Você possui uma profunda conexão com sua espiritualidade, suas crenças ou o próprio universo. Essa conexão faz com que você veja o mundo e viva sua vida de forma diferente e peculiar.',
    trainedSkills: ['Ocultismo', 'Religião'],
    powerName: 'A Culpa é das Estrelas',
    powerDescription:
        'Escolha um número de sorte entre 1 e 6; no início de cada cena, pode gastar 1 PE e rolar 1d6; se for seu número da sorte, recebe +2 em testes de perícia até o fim da cena',
  );

  static const legistaTurnoNoite = CharacterOrigin(
    name: 'Legista do Turno da Noite',
    description:
        'Em um trabalho como o seu, é de se esperar que você já tenha visto muita coisa. No entanto, quando o sol se põe, seus colegas vão embora e a luz artificial deixa cantos sombrios do necrotério, talvez você veja mais do que gostaria.',
    trainedSkills: ['Ciências', 'Medicina'],
    powerName: 'Luto Habitual',
    powerDescription:
        'Sofre apenas metade do dano mental por presenciar cenas relacionadas à rotina de um legista; além disso, em testes de Medicina para primeiros socorros ou necropsia pode gastar 2 PE para receber +5 naquele teste',
  );

  static const mateiro = CharacterOrigin(
    name: 'Mateiro',
    description:
        'Você conhece áreas rurais e selvagens. Você pode ser um guia florestal, um biólogo de campo ou simplesmente um entusiasta da vida selvagem.',
    trainedSkills: ['Percepção', 'Sobrevivência'],
    powerName: 'Mapa Celeste',
    powerDescription:
        'Desde que possa ver o céu, você sempre sabe as direções dos pontos cardeais e chega sem se perder em qualquer lugar que tenha visitado pelo menos uma vez',
  );

  static const mergulhador = CharacterOrigin(
    name: 'Mergulhador',
    description:
        'Seja por profissão ou por hobby, você é um aventureiro subaquático que explora os mistérios e maravilhas do mundo submerso.',
    trainedSkills: ['Atletismo', 'Fortitude'],
    powerName: 'Fôlego de Nadador',
    powerDescription:
        'Recebe +5 PV e pode prender a respiração por um número de rodadas igual ao dobro do seu Vigor',
  );

  static const motorista = CharacterOrigin(
    name: 'Motorista',
    description:
        'Você é um caminhoneiro, motorista de aplicativo, motoboy, piloto de corrida, motorista de ambulância ou qualquer outro tipo de condutor profissional.',
    trainedSkills: ['Pilotagem', 'Reflexos'],
    powerName: 'Mãos no Volante',
    powerDescription:
        'Você não sofre penalidades em testes de ataque por estar em um veículo em movimento; e sempre que precisar fazer teste de Pilotagem ou resistência enquanto pilota, pode gastar 2 PE para receber +5 nesse teste',
  );

  static const nerdEntusiasta = CharacterOrigin(
    name: 'Nerd Entusiasta',
    description:
        'Você dedicou muito do seu tempo aprendendo sobre videogames, RPGs de mesa, ficção científica ou qualquer outro assunto considerado "nerd".',
    trainedSkills: ['Ciências', 'Tecnologia'],
    powerName: 'O Inteligentão',
    powerDescription:
        'O bônus que você recebe ao utilizar a ação de interlúdio "ler" aumenta em +1 dado – de +1d6 para +2d6',
  );

  static const psicologo = CharacterOrigin(
    name: 'Psicólogo',
    description:
        'Você se especializou no estudo e tratamento das questões mentais do ser humano. Em sua prática profissional, você teve contato com o paranormal.',
    trainedSkills: ['Intuição', 'Profissão – psicólogo'],
    powerName: 'Terapia',
    powerDescription:
        'Você pode usar Profissão(psicólogo) no lugar de Diplomacia; além disso, uma vez por rodada, quando você ou um aliado em curto alcance falha em um teste de resistência contra dano mental, pode gastar 2 PE para fazer um teste de Profissão(psicólogo)',
  );

  static const profetizado = CharacterOrigin(
    name: 'Profetizado',
    description:
        'Como qualquer pessoa, você vai morrer. Entretanto, diferente delas, você sabe como isso vai acontecer. De algum jeito, seja por pesadelos, pensamentos intrusivos ou até visões inesperadas.',
    trainedSkills: [
      'Vontade',
      'Mais uma à sua escolha relacionada à premonição',
    ],
    powerName: 'Luta ou Fuga',
    powerDescription:
        'Conhecer os sinais da sua morte o deixa mais confiante; recebe +2 em Vontade. Quando surge referência à sua premonição, além do bônus de Vontade você recebe +2 PE temporários até o fim da cena',
  );

  static const reporterInvestigativo = CharacterOrigin(
    name: 'Repórter Investigativo',
    description:
        'Você está sempre em busca de histórias significativas, investigando eventos, entrevistando fontes e analisando dados para descobrir a verdade por trás dos acontecimentos.',
    trainedSkills: ['Atualidades', 'Investigação'],
    powerName: 'Encontrar a Verdade',
    powerDescription:
        'Você pode usar Investigação no lugar de Diplomacia ao fazer testes para persuadir ou mudar atitude; além disso, ao fazer teste de Investigação pode gastar 2 PE para receber +5 nesse teste',
  );

  static const List<CharacterOrigin> allOrigins = [
    // Origens do Livro "Iniciação"
    academico,
    agenteSaude,
    amnesico,
    artista,
    atleta,
    chef,
    investigador,
    lutador,
    magnata,
    mercenario,
    militar,
    operario,
    policial,
    religioso,
    servidorPublico,
    // Novas Origens do Suplemento "Sobrevivendo ao Horror"
    amigoAnimais,
    astronauta,
    chefOutroLado,
    colegial,
    cosplayer,
    diplomata,
    explorador,
    experimento,
    fanaticoCriaturas,
    fotografo,
    inventorParanormal,
    jovemMistico,
    legistaTurnoNoite,
    mateiro,
    mergulhador,
    motorista,
    nerdEntusiasta,
    psicologo,
    profetizado,
    reporterInvestigativo,
  ];
}
