//Caixa de login/cadastrar no menu

function toggleDropdown() {
    const dropdown = document.getElementById('dropdown');
    const overlay = document.getElementById('overlay');
    dropdown.classList.toggle('hidden');
    overlay.classList.toggle('hidden');
}

//Efeito para subir a página quando apertar o botão de voltar para cima

if(document.getElementById('back-to-top') != null){
  document.getElementById('back-to-top').addEventListener('click', function(e) {
      e.preventDefault();
      window.scrollTo({
          top: 0,
          behavior: 'smooth'
      });
  });
}

//Efeitos da tela de login/cadastro

const divGreetingsContainer = document.querySelector("div#greetings-container");
const divGreetings = document.querySelector("div#greetings");
const greetingsElements = divGreetings.children;
const buttonChangeMode = document.querySelector("button#change-mode");

const transitionMode = "0.7s";

function changeMode(){
  if (divGreetingsContainer.classList.contains("right")) {
    divGreetingsContainer.classList.remove("right");
    divGreetingsContainer.classList.add("left");

    greetingsElements[0].innerText = "Olá, Amigo!";
    greetingsElements[1].innerText = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua";
    greetingsElements[2].innerText = "Entre";

    divGreetingsContainer.style.transition = transitionMode;
  }
  else if(divGreetingsContainer.classList.contains("left")){
    divGreetingsContainer.classList.remove("left");
    divGreetingsContainer.classList.add("right");

    greetingsElements[0].innerText = "Bem-Vindo de Volta!";
    greetingsElements[1].innerText = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua";
    greetingsElements[2].innerText = "Cadastre-se";

    divGreetingsContainer.style.transition = transitionMode;
  }
}

buttonChangeMode.addEventListener("click", changeMode);