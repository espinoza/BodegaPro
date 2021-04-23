
$(document).ready( function(){

    $("#email").focusout( function(){
        console.log("focusout")
        verificarEmail(false)
    })
    $("#btn-submit").click( function(){
        if(verificarEmail(true) == false){
            return false;
        }
    })
})

function eraseErrores(){
    $(".ajax-err").remove();
}  

function renderErrorIn(elId,errores){
    txt = "" 
    i = 0
    for (var error in errores){
        txt += "<li class='error err'>" + errores[error] + "</li>"
        i++
    }
    if (i > 0){
        $("#"+elId).after("<ul class='ajax-err messages'>" + txt + "</ul>")
    }
}  


function verificarEmail(presionado){

    //console.log("verificando")

    var data = $("#formulario").serialize();

    console.log(data)

    $.ajax({
        type:"POST",
        url: "/users/register/checkEmail",
        data: data,
        dataType:"JSON",
    })
    .done( function(response){
        //console.log(response)
        //error = response["errors"]
        //console.log("PRESIONADO=" + presionado + "; SIZE =" + Object.keys(response).length) 
        var size = Object.keys(response).length;
        eraseErrores()
        if(size == 0){
            if (presionado == true){
                $("#formulario").submit();
            }
        } else {
            renderErrorIn("email",response)
        }
    })
    .fail( function(){
        alert("FALLA...")
    })
    .always( function(){
        //nada
    })
    return false
};

//DIRECT JAVASCRIPT
function chkErrores(elId) {

    var x = document.getElementById(elId);
    var valor = x.value
    var errores = []
    switch(elId){
        //[via AJAX ]case "email":
        case "name1":
            if (valor.length == 0){
                errores.push("Primer nombre requerido!")
            }
            else if (valor.length < 2 | valor.length > 50){
                errores.push("El nombre debe estar entre 2 y 50 caracteres")
            }
            break;
        case "last_name1":
            if (valor.length == 0){
                errores.push("Apellido 1 requerido!")
            } else if (valor.length < 2 | valor.length > 50){
                errores.push("El apellido debe estar entre 2 y 50 caracteres")
            }
            break;
        case "last_name2":
            if (valor.length == 0){
                errores.push("Apellido 2 requerido!")
            } else if (valor.length < 2 | valor.length > 50){
                errores.push("El segundo apellido debe estar entre 2 y 50 caracteres")
            }
            break;
        case "password":
            if (valor.length == 0){
                errores.push("Contraseña requerida!")
            } else if (valor.length < 8){
                errores.push("La contraseña debe tener al menos 8 caracteres")
            }
            break;
        case "confirm_password":
            var pass = document.getElementById("password").value
            if (valor.length == 0){
                errores.push("Confirmar contraseña por favor!")
            } else if (pass != valor){
                errores.push("La confirmación no coincide con la contraseña entregada. Revisar!")
            }
            break;
    }

    if (errores.length > 0){
        txt = "" 
        i = 0
        for (var error in errores){
            txt += "<li class='error err'>" + errores[error] + "</li>"
            i++
        }
        if (i > 0){
            $("#"+elId).after("<ul class='err_"+elId+"'>" + txt + "</ul>")
        }
    }
    
}

function eraseError(elId){
    $(".err_"+elId).remove();
}  
