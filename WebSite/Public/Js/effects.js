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
    document.cookie = `idUser=${null}; path=/`;
  }
}

if(document.querySelector("a#sign-out")){
  const buttonSignOut = document.querySelector("a#sign-out");
  buttonSignOut.addEventListener("click", signOut);
}

//Redirecionamento para a página de adicionar tópico

if(document.querySelector("div#add-topic")){
  const divAddTopic = document.querySelector("div#add-topic");
  divAddTopic.addEventListener("click", () => {
    window.location.href = "/forum/add-topic";
  })
}

//Redirecionamento para a página inicial após adicionar tópico

if(document.querySelector("button#button-add-topic")){
  const buttonAddTopic = document.querySelector("button#button-add-topic");
  buttonAddTopic.addEventListener("click", () => {
    window.location.href = "/";
  })
}

//Redirecionamento para a página de tópico ao clicar no link

if(document.querySelector("div.topic-container")){
  const divsTopicContainer = document.querySelectorAll("div.topic-container");
  divsTopicContainer.forEach(element => {
    element.addEventListener("click", () => {
      window.location.href = `/forum/topic?id=${element.id}`;
    });
  });
};

//Redirecionamento para a página de resposta ao clicar no link

if(document.querySelector("button#button-answer")){
  const buttonAnswer = document.querySelector("button#button-answer");
  const urlParams = new URLSearchParams(window.location.search);
  buttonAnswer.addEventListener("click", () => {
    window.location.href = `/forum/answer?id=${urlParams.get("id")}`;
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