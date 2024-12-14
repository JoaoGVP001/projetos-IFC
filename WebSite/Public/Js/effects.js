//Redirecionamento para página inicial através do click no logo

const logo = document.querySelector("img#logo");
logo.addEventListener("click", () => {
  window.location.href = "/";
})

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