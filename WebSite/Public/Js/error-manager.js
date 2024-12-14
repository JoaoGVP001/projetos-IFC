//Tratamento de erros do login

const buttonLogin = document.querySelector("button#button-login");

let userValue = document.querySelector("input#user").value;

function loginManager(mode){
    if(mode == "login"){
        if(!isNaN(parseFloat(userValue[0]))){
            console.log("olaa")
        }
    }
}

buttonLogin.addEventListener("click", () => {
    loginManager("login")
});
