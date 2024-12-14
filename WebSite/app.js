const express = require("express");
const path = require("path");
const User = require("./Models/user");
const sequelize = require('./Config/database-config');

const app = express();

const publicPath = path.join(__dirname, "Public");

const textLogin = [
  "Bem-Vindo de Volta!",
  "Estamos felizes que você está de volta! Se você ainda não possui uma conta, cadastre-se.",
  "Cadastre-se"
];
const textRegister = [
  "Olá, Amigo!",
  "Seja bem-vindo a LunarWay! O portal da informação do mundo espacial. Caso já tenha uma conta cadastrada acesse o login.",
  "Entre"
]
const numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

let username = undefined;
let modeSide = "right";
let text = textLogin;
let visibilityErrorLogin = "invisible";
let visibilityErrorRegister = "invisible";
let visibilitySuccess = "invisible";
let msgError = "";

app.use(express.static(publicPath));
app.use(express.urlencoded({ extended: true }));

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.get("/", (req, res) => {
    res.render("home");
});

app.get("/home", (req, res) => {
  res.render("home");
});

app.get("/news", (req, res) => {
    res.render("news");
});

app.get("/news2", (req, res) => {
  res.render("news2");
});

app.get("/news3", (req, res) => {
  res.render("news3");
});

app.get("/forum", (req, res) => {
    res.render("forum");
})

app.get("/login", (req, res) => {
  const modeParameter = req.query.mode;
  if(modeParameter == "successful"){
    res.render("successful-login", { username });
  }
  else{
    if(modeParameter == "register"){
      modeSide = "left";
      text = textRegister
    }
    else{
      modeSide = "right";
      text = textLogin
    }
    res.render("login", { modeSide, text, visibilityErrorLogin, visibilityErrorRegister, visibilitySuccess, msgError });
  }
  });

app.post("/login/:mode", (req, res) => {
  const modeParameter = req.params.mode;
  visibilityErrorLogin = "invisible";
  visibilityErrorRegister = "invisible";
  visibilitySuccess = "invisible";
  msgError = "";

  if (modeParameter == "login") {
    let {username, password} = req.body;
    res.redirect("/login?mode=successful");
  }
  else if(modeParameter == "register"){
    let name = req.body.name;
    let username = req.body.username;
    let password = req.body.password;
    let confirmPassword = req.body.confirmPassword;

    if(parseInt(username[0]) in numbers){
      visibilityErrorRegister = "visible";
      msgError = "O nome de usuário não deve iniciar com um número.";
      res.redirect("/login?mode=register");
    }
    else if(username.length < 3){
      visibilityErrorRegister = "visible";
      msgError = "O nome de usuário deve conter pelo menos 3 dígitos.";
      res.redirect("/login?mode=register");
    }
    else if(password.length < 6){
      visibilityErrorRegister = "visible";
      msgError = "A senha deve conter pelo menos 6 dígitos.";
      res.redirect("/login?mode=register");
    }
    else if(password != confirmPassword){
      visibilityErrorRegister = "visible";
      msgError = "As senhas não são iguais";
      res.redirect("/login?mode=register");
    }
    else{
      visibilityErrorRegister = "invisible";
      visibilitySuccess = "visible";
      msgError = "";
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