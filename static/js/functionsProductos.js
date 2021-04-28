function getToken(){
    return document.querySelectorAll('[name="csrfmiddlewaretoken"]')[0].value;
}

$(document).on("click", "[id^=desactivar-]", function(){
    id = $(this).attr('id').substring(11);
    toggleItem('desactivar',id);
    return false;
});

$(document).on("click", "[id^=activar-]", function(){
    id = $(this).attr('id').substring(8);
    toggleItem('activar',id);
    return false;
});

$(document).on("change", "#modal-image_url", function(){
    img_url = $(this).val();
    $("#modal-img_src").attr('src',URL.createObjectURL(event.target.files[0]));
});


$(document).ready( function(){

    var miEl = document.getElementById("editModal")

    miEl.addEventListener('hide.bs.modal', function (event) {

        var button = event.target; 

    })

    miEl.addEventListener('show.bs.modal', function (event) {      
        var button = event.relatedTarget;

        fila_id = button.id;
        cod = $(`#cod-${fila_id}`).text();
        prod_name = $(`#name-${fila_id}`).text();
        unidad_medida = $(`#unidad_medida-${fila_id}`).text();
        familia = $(`#familia-${fila_id}`).text();
        img_url = $(`#img_url-${fila_id}`).attr('src');

        //$("#id-to-edit").val(fila_id)
        $("#modal-id-to-edit").val(fila_id);
        $("#editModalLabel").html(`Producto - ${prod_name}`);

        $("#modal-cod").val(cod);
        $("#modal-name").val(prod_name);
        $(`#modal-unidad_medida option:contains('${unidad_medida}')`).attr('selected',true) ;
        $(`#modal-familia option:contains('${familia}')`).attr('selected',true);

        $("#modal-img_src").attr('src',img_url);

        $('#modal-image_url').val(''); 

    })  

    $('#modal-edit-btn').on('click', function() {
        //alert(`Remove now ${ $("#id-to-edit").val() }!!`);
        editData($("#modal-id-to-edit").val());
        $('#editModal').modal('hide');
    });

    $("#btn-filter").click( function(){
        getProductos();
        return false;
    })

    $("#btn-filter-reset").click( function(){
        $("#filter-isactive").val('1');
        $("#filter-contains").val('')
        $("#filter-familia").val('0')
        getProductos();
        return false;
    })
    

})


function getProductos(){

    data = $('#form-filter').serialize()
    //console.log(data)

    $.ajax({
        type:"POST",
        url: "get/filter",
        data: data,
        dataType:"JSON",
    })
    .done( function(response){
        
        if (response['status'] == 'OK'){
            cargarProductos(response['productos']);
        } else {
            alert(response['status']);
        }

    })
    .fail( function(){
        alert("FALLA...")
    })
    .always( function(){
        //nada
    })



}


function editData(id_item){

    //let data = $('#form-modal').serialize();

    var formdata = new FormData($('#form-modal')[0]); //archivos

    $.ajax({
        type:"POST",
        url:'item/update',
        data: formdata,
        dataType:"JSON",
        processData: false, //archivos
        contentType: false, //archivos
    })
    .done( function(response){

        if (response['status'] == 'OK'){
            //actualizar el item directo:
            $(`#tr-${id_item}`).html(getFilaHtml(id_item,response['product'],'edit'));
        } else {
            alert(response['status']);
        }

    })
    .fail( function(){
        alert("FALLA...")
    })
    .always( function(response){

    })
    

}


function toggleItem(tipo_ac,id_item){

    var token = getToken();

    if (tipo_ac == 'activar'){
        is_active = true;
    } else {
        is_active = false;
    }

    data = 'csrfmiddlewaretoken=' + token + '&';
    data += 'is_active=' + is_active + '&';
    data += 'id=' + id_item;

    $.ajax({
        type:"POST",
        url: `item/${tipo_ac}`,
        data: data,
        dataType:"JSON",
    })
    .done( function(response){
        
        if (response['status'] == 'OK'){
            //actualizar el item directo
            $(`#tr-${id_item}`).html(getFilaHtml(id_item,response['product'],'edit'));
        } else {
            alert(response['status']);
        }

    })
    .fail( function(){
        alert("FALLA...")
    })
    .always( function(){
        //nada
    })


}

function getFilaHtml(id_item,producto,tipo){

    let txt = "";

    txt += `
    <td scope="col"><img id="img_url-${id_item}" class="avatar" src="${producto['img_url']}" alt="Prod Img"></td>
    <td scope="col" id="cod-${id_item}">${producto['cod']}</td>
    <td scope="col" id="name-${id_item}">${producto['name']}</td>
    <td scope="col">${producto['cantidad']}</td>
    <td scope="col" id="unidad_medida-${id_item}">${producto['unidad_medida']}</td>
    <td scope="col" id="familia-${id_item}">${producto['familia']}</td>
    <td scope="col">${producto['precio_unit']}</td>`;

    if (tipo=='edit'){

        let is_active_txt = "";
        let txt_btn = "";

        if (producto['is_active']){
            is_active_txt = "A";
            txt_btn = `<button class="btn btn-outline-danger" id="desactivar-${id_item}">Desactivar</button>`;
        } else {
            is_active_txt = "I";
            txt_btn = `<button class="btn btn-outline-success" id="activar-${id_item}">Activar</button>`;
        }

        txt += `<td>${is_active_txt}</td>
        <td scope="col">
        <button class="btn btn-outline-secondary" id="${id_item}" 
        data-bs-toggle="modal" data-bs-target="#editModal">Edit</button> |
        ${txt_btn}
        </td>`;
        
    }

    return txt

}


function cargarProductos(productos){
   
    let tipo = $('#template-tipo').val()
   
    let txt = "";

    if (Object.keys(productos).length > 0){ 

        for (p in productos){
            let prod = productos[p];
            txt += `<tr id="tr-${prod.id}">`;
            txt += getFilaHtml(prod.id,prod,tipo);
            txt += `</tr>`;
        }

    } else {

        let numCols
        if (tipo == 'view'){
            numCols = 7;
        } else {
            numCols = 8;
        };

        txt = `<tr>
            <td></td>
            <td colspan="${numCols}">
            Sin productos en esta clasificación.
            </td></tr>`;

    }

    $('#table-body').html(txt);

}

//ERRORES

function eraseErrores(){
    $(".ajax-err").remove();
}  

function eraseMessages(){
    $(".messages").remove();
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

function chkErrores(elId) {

    eraseMessages();

    var x = document.getElementById(elId);
    var valor = x.value
    var errores = []
    switch(elId){
        //[via AJAX ]case "cod":
        case "cod":
        case "modal-cod":
            let valor_txt = valor.replace(/\./g,"")
            let cod_num = Number(valor_txt)
            if (cod_num){
                if (valor_txt.length != 8){
                    errores.push("Código fuera de rango (mínimo 10000000, 8 dígitos)")
                }
            } else {
                errores.push("Formato inválido (sólo 8 dígitos)")
            }
            break;
        case "name":
        case "modal-name":
            if (valor.length == 0){
                errores.push("Descripción requerida!")
            } else if (valor.length <= 5 | valor.length > 100){
                errores.push("Descripción debe estar entre 6 y 100 caracteres")
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