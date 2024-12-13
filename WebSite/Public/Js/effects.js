//Redirecionamento para página inicial através do click no logo

const logo = document.querySelector("img#logo");
logo.addEventListener("click", () => {
  window.location.href = "/";
})

//Efeitos da tela de login/cadastro

const url = new URL(window.location.href);

const divGreetingsContainer = document.querySelector("div#greetings-container");
const divGreetings = document.querySelector("div#greetings");
const greetingsElements = divGreetings.children;
const buttonChangeMode = document.querySelector("button#change-mode");

const inputPasswordLogin = document.querySelector("div#login input#password-login");
const buttonSeePasswordLogin = document.querySelector("div#login i#see-password-login");

const inputPasswordRegister = document.querySelector("div#register input#password-register");
const buttonSeePasswordRegister = document.querySelector("div#register i#see-password-register");

const inputConfirmPassword = document.querySelector("div#register input#confirm-password");
const buttonSeeConfirmPassword = document.querySelector("div#register i#see-confirm-password");

const transitionMode = "0.7s";

function changeModeLogin(){
  if (divGreetingsContainer.classList.contains("right")) {
    divGreetingsContainer.classList.remove("right");
    divGreetingsContainer.classList.add("left");

    greetingsElements[0].innerText = "Olá, Amigo!";
    greetingsElements[1].innerText = "Seja bem-vindo a LunarWay! O portal da informação do mundo espacial. Caso já tenha uma conta cadastrada acesse o login.";
    greetingsElements[2].innerText = "Entre";

    divGreetingsContainer.style.transition = transitionMode;

    url.searchParams.set("mode", "register");
    window.history.pushState({}, '', url);
  }
  else if(divGreetingsContainer.classList.contains("left")){
    divGreetingsContainer.classList.remove("left");
    divGreetingsContainer.classList.add("right");

    greetingsElements[0].innerText = "Bem-Vindo de Volta!";
    greetingsElements[1].innerText = "Estamos felizes que você está de volta! Se você ainda não possui uma conta, cadastre-se.";
    greetingsElements[2].innerText = "Cadastre-se";

    divGreetingsContainer.style.transition = transitionMode;

    url.searchParams.set("mode", "login");
    window.history.pushState({}, '', url);
  }
}

function changeModeForm(mode){
  if(mode == "password-login"){
    if(inputPasswordLogin.type == "password"){
      inputPasswordLogin.type = "text";
    }
    else{
      inputPasswordLogin.type = "password";
    }
  }
  else if(mode == "password-register"){
    if(inputPasswordRegister.type == "password"){
      inputPasswordRegister.type = "text";
    }
    else{
      inputPasswordRegister.type = "password";
    }
  }
  else if(mode == "confirm-password"){
    if(inputConfirmPassword.type == "password"){
      inputConfirmPassword.type = "text";
    }
    else{
      inputConfirmPassword.type = "password";
    }
  }
}

buttonChangeMode.addEventListener("click", changeModeLogin);
buttonSeePasswordLogin.addEventListener("click", () => {
  changeModeForm("password-login");
});
buttonSeePasswordRegister.addEventListener("click", () => {
  changeModeForm("password-register");
});
buttonSeeConfirmPassword.addEventListener("click", () => {
  changeModeForm("confirm-password");
});

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