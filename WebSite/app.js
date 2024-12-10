const express = require("express");
const path = require("path");
const User = require("./Models/user");
const sequelize = require('./config/database-config');

const app = express();

const publicPath = path.join(__dirname, "Public");

app.use(express.static(publicPath));

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.get("/", (req, res) => {
    res.render("home");
});

app.get("/news", (req, res) => {
    res.sendFile(path.join(publicPath, "news.html"));
});

app.get("/forum", (req, res) => {
    res.sendFile(path.join(publicPath, "forum.html"));
})

app.get('/test', async (req, res) => {
    try {
      // Recupera todos os produtos do banco de dados
      const users = await User.findAll();
      
      // Renderiza a página EJS com os produtos
      res.render('index', { users });
    } catch (error) {
      console.error('Erro ao recuperar produtos:', error);
      res.status(500).send('Erro ao recuperar produtos');
    }
  });

sequelize.sync().then(() => {
    console.log('Banco de dados sincronizado!');
    const port = 3000;
    app.listen(port, () => {
      console.log(`Servidor rodando na porta ${port}`);
    });
  });