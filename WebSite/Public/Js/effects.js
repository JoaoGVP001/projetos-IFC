//Redirecionamento para página inicial através do click no logo

const logo = document.querySelector("img#logo");
logo.addEventListener("click", () => {
  window.location.href = "/";
});

//Caixa de login/cadastrar no menu

function toggleDropdown() {
    const dropdown = document.getElementById('dropdown');
    const overlay = document.getElementById('overlay');
    dropdown.classList.toggle('hidden');
    overlay.classList.toggle('hidden');
}

//Caixa de sair da conta no menu

function signOut(){
  const cookie = document.cookie;
  if (cookie.indexOf("idUser=") !== -1) {
    document.cookie = `idUser=${null}`;
  }
}

if(document.querySelector("a#sign-out")){
  let buttonSignOut = document.querySelector("a#sign-out");
  buttonSignOut.addEventListener("click", signOut);
}

//Redirecionamento para a página de adicionar tópico

if(document.querySelector("div#add-topic")){
  let divAddTopic = document.querySelector("div#add-topic");
  divAddTopic.addEventListener("click", () => {
    window.location.href = "/forum/add-topic";
  })
}

//Redirecionamento para a página inicial após adicionar tópico

if(document.querySelector("button#button-add-topic")){
  let buttonAddTopic = document.querySelector("button#button-add-topic");
  buttonAddTopic.addEventListener("click", () => {
    window.location.href = "/";
  })
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