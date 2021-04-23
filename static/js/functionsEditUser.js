$(document).ready( function(){

    $("#email").focusout( function(){
        console.log("focusout")
        verificarEmail(false)
    })

    //$("[id^=btn-submit-]").click( function(){
    $("#btn-submit-datagral").click( function(){
        if(verificarEmail(true) == false){
            return false;
        }
    })

    $(window).keydown(function(event){ //prevent users hitting click and submmitting
        if(event.keyCode == 13) {
          event.preventDefault();
          return false;
        }
    });

})

function corrigeNextNumRdc(){

    let numcta = $("#next_num_rdc").val();
    $("#next_num_rdc").val(numcta.replace(/\D/g,''))

}

function corrigeNumCta(){

    let numcta = $("#banco_num_cuenta").val();
    $("#banco_num_cuenta").val(numcta.replace(/\D/g,''))

}

function corrigeRut(){

    let rut = $("#rut").val();

    let hasDigitoVerif = false

    let miArr = rut.split("-")
    rut0 = miArr[0].replace(/\D/g,''); //dejar sólo números
    if (rut0.length>0 && rut0.length<4){
        //siga
    } else if (rut0.length>3 && rut0.length<7){
        rut0 =  rut0.substring(0,rut0.length-3) + '.' + rut0.substring(rut0.length-3);
    } else if (rut0.length>6 && rut0.length<9){
        rut0 =  rut0.substring(0,rut0.length-6) + '.' + rut0.substring(rut0.length-6,rut0.length-3) + '.' + rut0.substring(rut0.length-3);
    } else if (rut0.length==9){
        rut0 =  rut0.substring(0,rut0.length-1-6) + '.' + rut0.substring(rut0.length-1-6,rut0.length-1-3) + '.' + rut0.substring(rut0.length-1-3,rut0.length-1) + '-' + rut0.substring(rut0.length-1);
        hasDigitoVerif = true
    } else {
        $("#rut").val("")
        return
    }

    if (miArr.length == 2 && !hasDigitoVerif){
        rut0 += "-" + miArr[1].substring(0,1)
    }

    $("#rut").val(rut0);

}

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
    
    var data = $("#form_datagral").serialize();

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
                $("#form_datagral").submit();
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
            console.log('revisando apellido 2')
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
