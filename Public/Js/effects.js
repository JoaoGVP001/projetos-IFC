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

//Redirecionamento para a página de notícia

if(document.querySelector("div#news-artemis1")){
  const divNewsArtemis = document.querySelector("div#news-artemis1");
  divNewsArtemis.addEventListener("click", () => {
    window.location.href = "/news/artemis1";
  })
};

if(document.querySelector("div#news-artemis2")){
  const divNewsArtemis = document.querySelector("div#news-artemis2");
  divNewsArtemis.addEventListener("click", () => {
    window.location.href = "/news/artemis2";
  })
};

if(document.querySelector("div#news-artemis3")){
  const divNewsArtemis = document.querySelector("div#news-artemis3");
  divNewsArtemis.addEventListener("click", () => {
    window.location.href = "/news/artemis3";
  })
};

if(document.querySelector("div#news-apollo1")){
  const divNewsApollo = document.querySelector("div#news-apollo1");
  divNewsApollo.addEventListener("click", () => {
    window.location.href = "/news/apollo1";
  })
};

if(document.querySelector("div#news-apollo2")){
  const divNewsApollo = document.querySelector("div#news-apollo2");
  divNewsApollo.addEventListener("click", () => {
    window.location.href = "/news/apollo2";
  })
};

if(document.querySelector("div#news-gateway1")){
  const divNewsGateway = document.querySelector("div#news-gateway1");
  divNewsGateway.addEventListener("click", () => {
    window.location.href = "/news/gateway1";
  })
};

if(document.querySelector("div#news-gateway2")){
  const divNewsGateway = document.querySelector("div#news-gateway2");
  divNewsGateway.addEventListener("click", () => {
    window.location.href = "/news/gateway2";
  })
};

if(document.querySelector("div#news-gateway3")){
  const divNewsGateway = document.querySelector("div#news-gateway3");
  divNewsGateway.addEventListener("click", () => {
    window.location.href = "/news/gateway3";
  })
};

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
    window.location.href = `/forum/add-answer?id=${urlParams.get("id")}`;
  })
};

//Envio de id de tópico ao enviar resposta

if(document.querySelector("button#button-add-answer")){
  const buttonAddAnswer = document.querySelector("button#button-add-answer");
  const divMsgError = document.querySelector("div#msgError");
  const urlParams = new URLSearchParams(window.location.search);
  const url = '/add-answer';
  const topicId = urlParams.get("id");

  buttonAddAnswer.addEventListener("click", () => {
    let answerText = document.querySelector("textarea#answer-text").value;
    if(answerText.length == 0){
      if (divMsgError.classList.contains("invisible")) {
        divMsgError.classList.remove("invisible");
        divMsgError.classList.add("visible");
      }
      else{
        divMsgError.classList.remove("visible");
        divMsgError.classList.add("invisible");
      }
    }
    else{
      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ answerText, topicId })
      }).then(response => {
        if (response.redirected) {
          alert("Resposta registrada com sucesso!")
          window.location.href = response.url;
        }
      })
      .catch(error => {
        console.error('Erro ao registrar a resposta:', error);
        alert('Erro ao enviar à resposta');
      });
    }
  });
};

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