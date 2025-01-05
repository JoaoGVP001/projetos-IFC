## 1. **Requisitos para rodar o projeto**

1. Possuir o NodeJS instalado
2. Possuir o MySQL instalado
3. Possuir o XAMPP instalado
4. Possuir o Git instalado

## 2. **Passo a Passo para rodar o projeto**

Para rodar este projeto localmente, siga os passos abaixo:

1. Abra o programa XAMPP e inicie o Apache e MySQL

2. Caso seja a primeira vez executando o projeto em sua máquina siga o passo a passo abaixo:

    2.1. Abra o MySQL Workbench
    2.2. Clique na conexão "local"
    2.3. Digite e execute o comando:
        ```sql
        create user 'lunarWay'@'%' identified by 'SENHA';
        grant all on lunarWay.* to 'lunarWay'@'%';
    2.4. Apague o que foi digitado anteriormente, digite e execute:
        ```sql
        create database lunarWay;

3. Clone o repositório do github em uma pasta:

    ```bash
    git clone https://github.com/JoaoGVP001/Projeto-Integrador-II---2024

3. Crie um arquivo chamado .env dentro do caminho *Projeto-Integrador-II---2024\Config*

4. Dentro do arquivo .env copie e cole o conteúdo do arquivo *.env.HOMOLOG*

5. Acesse a pasta do projeto através do terminal do Windows:

    ```bash
    cd caminho\Projeto-Integrador-II---2024\

6. Digite o comando:

    ```bash
    npx nodemon app.js

7. Acesse no seu navegador web a URL:

    ```bash
    localhost:3000
