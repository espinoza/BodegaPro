function getToken(){
    return document.querySelectorAll('[name="csrfmiddlewaretoken"]')[0].value;
  }

$(document).on("click", "[id^=desactivar-]", function(){
    id_user = $(this).attr('id').substring(11)
    toggleUser('desactivar',id_user)
    return false;
});

$(document).on("click", "[id^=activar-]", function(){
    id_user = $(this).attr('id').substring(8)
    toggleUser('activar',id_user)
    return false;
});

function toggleUser(tipo,id_user){

    var token = getToken();

    if (tipo == 'activar'){
        is_active = true;
    } else {
        is_active = false;
    }

    data = 'csrfmiddlewaretoken=' + token + '&'
    data += 'is_active=' + is_active + '&'
    data += 'id=' + id_user

    $.ajax({
        type:"POST",
        url: `/rdcadmin/user/${tipo}`,
        data: data,
        dataType:"JSON",
    })
    .done( function(response){
        
        if (response['status'] == 'OK'){
            //actualizar el item directo:

            let txt = "A";
            if (tipo == 'desactivar'){
                txt = "I"
            }
            
            //actualizar texto en 4ta columna de la fila del usuario
            $(`#tr-${id_user} td:nth-child(4)`).text(txt)

            //cambiar el botón
            if (txt == "A"){
                $(`#activar-${id_user}`).after(
                `<button class='btn btn-outline-danger' id='desactivar-${id_user}'>Desactivar</button>`
                )
                $(`#activar-${id_user}`).remove()
            } else {
                $(`#desactivar-${id_user}`).after(
                `<button class="btn btn-outline-success" id="activar-${id_user}">Activar</button>`
                )
                $(`#desactivar-${id_user}`).remove()
            } 


        } else {
            alert(response['status'])
        }

    })
    .fail( function(){
        alert("FALLA...")
    })
    .always( function(){
        //nada
    })

}
