
function getToken(){
  return document.querySelectorAll('[name="csrfmiddlewaretoken"]')[0].value;
}

$(document).on("click", "[id^=desactivar-]", function(){
    id = $(this).attr('id').substring(11)
    toggleItem('desactivar',id)
    return false;
});

$(document).on("click", "[id^=activar-]", function(){
    id = $(this).attr('id').substring(8)
    toggleItem('activar',id)
    return false;
});

$(document).ready( function(){

    var miEl = document.getElementById("editModal")

    miEl.addEventListener('hide.bs.modal', function (event) {

        var button = event.target; 

    })

    miEl.addEventListener('show.bs.modal', function (event) {      
        var button = event.relatedTarget;
        
        fila_id = button.id
        descrip = $(`#name-${fila_id}`).text()
        pos = $(`#pos-${fila_id}`).text()
        tabla_name = $('#select-tabla option:selected').html()

        $("#id-to-edit").val(fila_id)
        $("#editModalLabel").html(`Editar de "${tabla_name}" - Fila: ${descrip}`);

        $("#modal-pos").val(pos)
        $("#modal-name").val(descrip)

    })  

    $('#modal-edit-btn').on('click', function() {
        //alert(`Remove now ${ $("#id-to-edit").val() }!!`);
        editUser($("#id-to-edit").val());
        $('#editModal').modal('hide');
    });

    $("#btn-tabla").click( function(){
        cargarTablaActiva()
        return false;
    });

    $("#btn-add-item").click( function(){
        addNewItem()
        return false;
    })

    $('#select-tabla').change(function(e) {
        cargarTablaActiva()
    });

})

function editUser(id_user){

    let data = $('#form-modal').serialize();

    console.log(data)

    data += `&id=${id_user}`;
    var tabla = $('#select-tabla').val();
    data += `&tabla_name=${tabla}`;

    data = data.replaceAll('modal_','')

    $.ajax({
        type:"POST",
        url:'tabla/item/update',
        data: data,
        dataType:"JSON",
    })
    .done( function(response){

        if (response['status'] == 'OK'){

            cargarTablaActiva()

        } else {

            console.log(response)
            alert(response['errores'])

        }

    })
    .fail( function(){
        alert("FALLA...")
    })
    .always( function(){
        //nada
    })
    

}


function addNewItem(){

    pos = $('#add-pos').val()
    descrip = $('#add-name').val()

    if (pos == ""){
        pos = 0;
    }

    if (descrip == ""){
        alert("La descripción no puede ser vacía!")
        return false
    }

    var data = $("#form-add-item").serialize();
    var tabla = $('#select-tabla').val()

    data += `&tabla_name=${tabla}`
    if (pos == 0){
        data += `&pos=${pos}`
    }

    $.ajax({
        type:"POST",
        url: "tabla/item/add",
        data: data ,
        dataType:"JSON",
    })
    .done( function(response){

        if (response['status'] == 'OK'){

            cargarTablaActiva()
            resetAgregarItem()

        } else {

            console.log(response)
            alert(response['errores'])

        }

    })
    .fail( function(){
        alert("FALLA...");
    })
    .always( function(){
        //nada
    })

};

function toggleItem(tipo,id_item){

    var tabla = $('#select-tabla').val();
    var token = getToken();

    if (tipo == 'activar'){
        is_active = true;
    } else {
        is_active = false;
    }

    data = 'csrfmiddlewaretoken=' + token + '&'
    data += 'tabla_name=' + tabla + '&'
    data += 'is_active=' + is_active + '&'
    data += 'id=' + id_item

    $.ajax({
        type:"POST",
        url: `tabla/item/${tipo}`,
        data: data,
        dataType:"JSON",
    })
    .done( function(response){
        
        if (response['status'] == 'OK'){
            //actualizar el item directo:
            $(`#tr-${id_item}`).html(getFilaHtml(id_item,response['pos'],response['name'],is_active))
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
function cargarTablaActiva(){

    if ($('#select-tabla').val() == 'notable'){

        txt = "<tr><td colspan='4'>ELIJA UNA TABLA...</td></tr>"
        $('#table-body').html(txt);
        $('#table-add-item').hide;

    } else {

        var data = $("#form-table-name").serialize();

        $.ajax({
            type:"POST",
            url: "tabla/load",
            data: data,
            dataType:"JSON",
        })
        .done( function(response){

            var size = Object.keys(response).length;
            if (size > 0){

                txt = '';
                for (var i=0;i<size;i++){

                    txt += `<tr id="tr-${response[i]['id']}">`
                    txt += getFilaHtml(
                        response[i]['id'],
                        response[i]['pos'],
                        response[i]['name'],
                        response[i]['is_active'],
                    );
                    txt += "</tr>"
                }


            } else {

                txt = "<tr><td colspan='4'>TABLA SIN DATOS</td></tr>";
                
            }

            $('#table-body').html(txt);
            $('#table-add-item').show;

        })
        .fail( function(){
            alert("FALLA...");
        })
        .always( function(){
            //nada
        })
    
    }
};

function resetAgregarItem(){
    $('#add-pos').val('');
    $('#add-name').val('');
}

function getFilaHtml(id_item,pos,descrip,is_active){

    let txt = "";
    let is_active_txt = "";
    let txt_btn = "";

    if (is_active){
        is_active_txt = "A";
        txt_btn = `<button class="btn btn-outline-danger" id="desactivar-${id_item}">Desactivar</button>`;
    } else {
        is_active_txt = "I";
        txt_btn = `<button class="btn btn-outline-success" id="activar-${id_item}">Activar</button>`;
    }

    txt = txt + `<td id="pos-${id_item}">${pos}</td>
    <td id="name-${id_item}">${descrip}</td>
    <td>${is_active_txt}</td>
    <td scope="col">
    <button class="btn btn-outline-secondary" id=${id_item}
    data-bs-toggle="modal" data-bs-target="#editModal">Edit</button> |
    ${txt_btn}
    </td>`

    return txt

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
                errores.push("LA contraseña debe tener al menos 8 caracteres")
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
