const express = require("express");
const cookieParser = require('cookie-parser');
const bodyParser = require('body-parser');
const path = require("path");
const User = require("./Models/user");
const Topic = require('./Models/topic');
const Answer = require('./Models/answer');
const sequelize = require('./Config/database-config');
const { name } = require("ejs");

const app = express();

const publicPath = path.join(__dirname, "Public");

const textsProfile = [`
  <a href='/login?mode=register'>CADASTRAR</a>
  <a href='/login?mode=login'>LOGIN</a>
`,
  "<a href='/' id='sign-out'>Sair da conta</a>"
]

const textsLogin = [
  "Bem-Vindo de Volta!",
  "Estamos felizes que você está de volta! Se você ainda não possui uma conta, cadastre-se.",
  "Cadastre-se"
];
const textsRegister = [
  "Olá, Amigo!",
  "Seja bem-vindo a LunarWay! O portal da informação do mundo espacial. Caso já tenha uma conta cadastrada acesse o login.",
  "Entre"
]
const numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

//Variáveis para checar se o usuário está logado

let visibilityProfile = "invisible";
let textProfile = textsProfile[0];

//Variáveis para página de adicionar tópico no fórum

let visibilityAddTopic = "invisible";
let visibilityErrorAddTopic = "invisible";

//Variável da página de tópico

let answersData = [];

//Variável da página de fórum

let topicsData = [];

//Variáveis da página de login/cadastro

let username;
let modeSide = "right";
let textLogin = textsLogin;
let visibilityErrorLogin = "invisible";
let visibilityErrorRegister = "invisible";
let visibilitySuccess = "invisible";
let msgError = "";

app.use(express.static(publicPath));
app.use(cookieParser('lunarWay'));
app.use(express.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.get("/", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  res.render("home", { username, visibilityProfile,textProfile });
});

app.get("/home", (req, res) => {
  res.redirect("/");
});

app.get("/artemis", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  res.render("artemis", { username, visibilityProfile, textProfile });
});

app.get("/apollo", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  res.render("apollo", { username, visibilityProfile, textProfile });
});

app.get("/gateway", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  res.render("gateway", { username, visibilityProfile, textProfile });
});

app.get("/news/artemis1", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  res.render("News/artemis1", { username, visibilityProfile,textProfile });
});

app.get("/news/artemis2", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  res.render("News/artemis2", { username, visibilityProfile,textProfile });
});

app.get("/news/artemis3", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  res.render("News/artemis3", { username, visibilityProfile,textProfile });
});

app.get("/news/apollo1", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  res.render("News/apollo1", { username, visibilityProfile,textProfile });
});

app.get("/news/apollo2", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  res.render("News/apollo2", { username, visibilityProfile,textProfile });
});

app.get("/news/apollo3", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  res.render("News/apollo3", { username, visibilityProfile,textProfile });
});

app.get("/news/gateway1", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  res.render("News/gateway1", { username, visibilityProfile,textProfile });
});

app.get("/news/gateway2", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  res.render("News/gateway2", { username, visibilityProfile,textProfile });
});

app.get("/news/gateway3", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  res.render("News/gateway3", { username, visibilityProfile,textProfile });
});

app.get("/forum", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    visibilityAddTopic = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    visibilityAddTopic = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }

  let topicsRegistered = await Topic.findAll();
  topicsRegistered.forEach(async (topic) => {
    if (topicsData.some(item => item.id == topic.dataValues.id) == false){
      const creationDate = new Date(topic.dataValues.createdAt);
      const formattedDate = creationDate.toLocaleString('pt-BR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric'
      });

      const author = await User.findOne({
        where: {
          id: topic.dataValues.authorId
        }
      });

      topicsData.push({
        id: topic.dataValues.id,
        name: topic.dataValues.name,
        description: topic.dataValues.description,
        authorId: topic.dataValues.authorId,
        author: author.username,
        createdAt: formattedDate
      });
    }
  });

  res.render("forum", { username, visibilityAddTopic, topicsData, visibilityProfile, textProfile });
});

app.get("/forum/add-topic", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    visibilityErrorAddTopic = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  
  res.render("add-topic", { username, visibilityProfile, visibilityErrorAddTopic, msgError, textProfile })
});

app.post("/add-topic", async (req, res) => {
  let nameTopicTyped = req.body.topicName;
  let descriptionTopicTyped = req.body.topicDescription;

  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityErrorAddTopic = "visible";
    msgError = "Você não está logado. Por favor faça login e tente novamente.";
    res.redirect("/forum/add-topic")
  }
  else{
    if (nameTopicTyped.length < 5){
      visibilityErrorAddTopic = "visible";
      msgError = "O nome do tópico deve conter pelo menos 5 caracteres.";
      res.redirect("/forum/add-topic")
    }
    else if (descriptionTopicTyped < 10){
      visibilityErrorAddTopic = "visible";
      msgError = "A descrição do tópico deve conter pelo menos 10 caracteres.";
      res.redirect("/forum/add-topic")
    }
    else {
      try{
        visibilityErrorAddTopic = "invisible";
        msgError = "";
        const topic = await Topic.create({
          name: nameTopicTyped,
          description: descriptionTopicTyped,
          authorId: req.cookies.idUser
        });
        res.redirect("/forum")
      }
      catch(error){
        visibilityErrorAddTopic = "visible";
        msgError = "Algo deu errado. Tente novamente mais tarde.";
        console.log(error)
        res.redirect("/forum/add-topic")
      }
  }
  }
});

app.get("/forum/topic", async (req, res) => {
  let visibilityAnswer;
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityAnswer = "invisible";
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityAnswer = "visible";
    visibilityProfile = "visible";
    visibilityErrorAddTopic = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }

  const topicAccessed = await Topic.findOne({
    where: {
      id: req.query.id
    }
  });

  const authorTopic = await User.findOne({
    where: {
      id: topicAccessed.authorId
    }
  });

  let topicName = topicAccessed.name;
  let topicDescription = topicAccessed.description;
  let authorTopicName = authorTopic.username;

  const answers = Answer.findAll({
    where: {
      topicId: req.query.id
    }
  }).then(async (answers) => {
    // Declarar answersData fora do loop
    const answersData = [];
    
    // Usando um loop assíncrono para garantir que todas as promessas sejam resolvidas
    for (let answer of answers) {
      // Se a resposta ainda não foi processada
      if (!answersData.some(item => item.id == answer.dataValues.id)) {
        const creationDate = new Date(answer.dataValues.createdAt);
        const formattedDate = creationDate.toLocaleString('pt-BR', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: 'numeric',
          minute: 'numeric',
          second: 'numeric'
        });
  
        // Espera pela promessa do autor
        const author = await User.findOne({
          where: {
            id: answer.dataValues.authorId
          }
        });

        // Adiciona a resposta formatada e o autor no answersData
        answersData.push({
          id: answer.dataValues.id,
          text: answer.dataValues.text,
          authorId: answer.dataValues.authorId,
          authorName: author.username,
          createdAt: formattedDate,
        });
      }
    }
  
    // Após processar todas as respostas, renderize a página
    res.render("topic", { 
      username, 
      topicName, 
      topicDescription, 
      authorTopicName, 
      answersData, 
      visibilityAnswer, 
      visibilityProfile, 
      textProfile 
    });
  
  }) 
});

app.get("/forum/add-answer", async (req, res) => {
  if(req.cookies.idUser == "null" || req.cookies.idUser == undefined){
    visibilityProfile = "invisible";
    textProfile = textsProfile[0];
  }
  else{
    visibilityProfile = "visible";
    textProfile = textsProfile[1];

    const userLogged = await User.findOne({
      where: {
        id: req.cookies.idUser
      }
    });
    username = userLogged.username;
  }
  res.render("add-answer", { username, visibilityProfile, textProfile });
});

app.post("/add-answer", async (req, res) => {
  let answerTyped = req.body.answerText;
  let topicId = req.body.topicId;
  if (req.body.topicId != undefined && req.body.answerText != undefined){
    const answer = await Answer.create({
      text: answerTyped,
      authorId: req.cookies.idUser,
      topicId: topicId
    });
  }
  res.redirect("/forum");
});

app.get("/login", (req, res) => {
  const modeParameter = req.query.mode;
  if(modeParameter == "successful"){
    res.render("successful-login", { username });
  }
  else{
    if(modeParameter == "register"){
      modeSide = "left";
      textLogin = textsRegister;
    }
    else{
      modeSide = "right";
      textLogin = textsLogin;
    }
    res.render("login", { modeSide, textLogin, visibilityErrorLogin, visibilityErrorRegister, visibilitySuccess, msgError });
  }
});

app.post("/login/:mode", async (req, res) => {
  const modeParameter = req.params.mode;
  visibilityErrorLogin = "invisible";
  visibilityErrorRegister = "invisible";
  visibilitySuccess = "invisible";
  msgError = "";

  if (modeParameter == "login") {
    let usernameTyped = req.body.username;
    let passwordTyped = req.body.password;
    const existingUser = await User.findOne({
      where: {
        username: usernameTyped
      }
    });
    if(existingUser == null){
      visibilityErrorLogin = "visible";
      msgError = `Não existe nenhuma conta com o nome de usuário de ${usernameTyped}`;
      res.redirect("/login?mode=login");
    }
    else{
      if(passwordTyped != existingUser.password){
        visibilityErrorLogin = "visible";
        msgError = "Nome de usuário e senha não correspondem.";
        res.redirect("/login?mode=login");
      }
      else{
        res.cookie("idUser", existingUser.id);
        res.redirect("/login?mode=successful");
      }
    }
  }
  else if(modeParameter == "register"){
    let usernameTyped = req.body.username;
    let emailTyped = req.body.email;
    let passwordTyped = req.body.password;
    let confirmPassword = req.body.confirmPassword;

    const existingUser = await User.findOne({
      where: {
        username: usernameTyped
      }
    });

    const existingEmail = await User.findOne({
      where: {
        email: emailTyped
      }
    });

    if(parseInt(usernameTyped[0]) in numbers){
      visibilityErrorRegister = "visible";
      msgError = "O nome de usuário não deve iniciar com um número.";
      res.redirect("/login?mode=register");
    }
    else if(usernameTyped.length < 3){
      visibilityErrorRegister = "visible";
      msgError = "O nome de usuário deve conter pelo menos 3 dígitos.";
      res.redirect("/login?mode=register");
    }
    else if(passwordTyped.length < 6){
      visibilityErrorRegister = "visible";
      msgError = "A senha deve conter pelo menos 6 dígitos.";
      res.redirect("/login?mode=register");
    }
    else if(passwordTyped != confirmPassword){
      visibilityErrorRegister = "visible";
      msgError = "As senhas não são iguais.";
      res.redirect("/login?mode=register");
    }
    else if(existingUser){
      visibilityErrorRegister = "visible";
      msgError = "Usuário já cadastrado. Tente algo diferente.";
      res.redirect("/login?mode=register");
    }
    else if(existingEmail){
      visibilityErrorRegister = "visible";
      msgError = "E-mail já cadastrado. Tente entrar na sua conta.";
      res.redirect("/login?mode=register");
    }
    else{
      try{
        visibilityErrorRegister = "invisible";
        visibilitySuccess = "visible";
        msgError = "";
        const user = await User.create({
          username: usernameTyped,
          email: emailTyped,
          password: passwordTyped
        });
      }
      catch(error){
        visibilityErrorRegister = "visible";
        visibilitySuccess = "invisible";
        msgError = "Ocorreu um erro. Tente novamente mais tarde.";
        console.log(error)
      }
      res.redirect("/login?mode=register");
    }
  }
});

/* app.get('/test', async (req, res) => {
    try {
      // Recupera todos os produtos do banco de dados
      const users = await User.findAll();
      
      // Renderiza a página EJS com os produtos
      res.render('test', { users });
    } catch (error) {
      console.error('Erro ao recuperar produtos:', error);
      res.status(500).send('Erro ao recuperar produtos');
    }
  }); */

sequelize.sync().then(() => {
    console.log('Banco de dados sincronizado!');
    const port = 3000;
    app.listen(port, () => {
      console.log(`Servidor rodando na porta ${port}`);
    });
  });

/* const port = 3000;
  app.listen(port, () => {
    console.log(`Servidor rodando na porta ${port}`);
  }); */