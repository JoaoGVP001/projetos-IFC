const express = require("express");
const path = require("path");
const User = require("./Models/user");
const sequelize = require('./Config/database-config');

const app = express();

const publicPath = path.join(__dirname, "Public");

app.use(express.static(publicPath));

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
  const modeParameter = req.query.mode || null;
  let mode = "right";
  let text = textLogin;

  if(modeParameter === "register"){
    mode = "left"
    text = textRegister;
  }

  res.render("login", { mode, text });
})

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