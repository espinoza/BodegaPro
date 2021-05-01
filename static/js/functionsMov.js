

$(document).on("click", "[id^=btn-item-choose-]", function(){
    id = $(this).attr('id').substring(16);
    console.log($(`#modal-name-${id}`).html())
    $("#id_cod").val($(`#modal-cod-${id}`).html())
    $("#id_name").val($(`#modal-name-${id}`).html())
    $("#id_precio_unit").val($(`#modal-precio-unit-${id}`).html())

    if ($("#id_cant_solicitada").val() == ""){
        $("#id_cant_solicitada").val('1')
    }

    $('#movprodModal').modal('hide');
    return false;
});

$(document).on("click", "[id^=btn-del-item-]", function(){
    let id = $(this).attr('id').substring(13);
    delItem(id);
    return false;
})

$(document).on("click", "[id^=btn-edit-item-]", function(){
    let id = $(this).attr('id').substring(14);
    editItem(id);
    return false;
})

$(document).ready( function(){

    var miEl = document.getElementById("movprodModal")

    miEl.addEventListener('show.bs.modal', function (event) {      

        getProductos()
 
    })

    $("#search-prod").click( function(){
        return false
    })

    $("#id_cod").css({'width':'90px','font-weight':'500','color':'blue'});
    $("#id_cant_solicitada").css({'width':'55px','font-weight':'500','color':'blue'});
    $("#id_name").css({'width':'250px','font-weight':'500','color':'blue'});
    $("#id_precio_unit").css({'width':'70px','font-weight':'500','color':'blue'});
    $("ul.errorlist li").css('color','red');

})

function editItem(id_item){

    let data = $(`#form-edit-item-${id_item}`).serialize();
    let id_encabezado = $('#mov-encabezado-id').val();

    $.ajax({
        type:"POST",
        url: `/movs/view/${id_encabezado}/item/edit`,
        data: data,
        dataType:"JSON",
    })
    .done( function(response){
        
        if (response['status'] == 'OK'){

            $(`#btn-edit-item-${id_item}`).css('color','yellow')
            setTimeout(function () {
                $(`#btn-edit-item-${id_item}`).css('color','white')
            }, 2000);
            
            console.log(response['message'])

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

function delItem(id_item){

    let data = $(`#form-del-item-${id_item}`).serialize()

    $.ajax({
        type:"POST",
        url: 'item/delete',
        data: data,
        dataType:"JSON",
    })
    .done( function(response){
        
        if (response['status'] == 'OK'){

            removeItem(id_item)
            setTimeout(function () {
                alert(response['message']);
            }, 500);

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

function removeItem(id_item){
    $(`#tr-item-${id_item}`).remove();
}

function getProductos(){

    data = $('#form-search').serialize()

    $.ajax({
        type:"POST",
        url: "/productos/get/filter",
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

function cargarProductos(productos){
   
    let txt = "";

    if (Object.keys(productos).length > 0){ 

        for (p in productos){
            let prod = productos[p];
            txt += `<tr id="tr-modal-${prod.id}">`;
            txt += getFilaHtml(prod);
            txt += `</tr>`;
        }

    } else {


        txt = `<tr>
            <td></td>
            <td colspan="4">No hay productos para la búsqueda.</td>
            <td></td>
            </tr>`;

    }

    $('#modal-table-body').html(txt);

}

function getFilaHtml(producto){

    let txt = "";

    txt += `
    <td scope="col"><img class="avatar sm-avatar" src="${producto['img_url']}" alt="Prod Img"></td>
    <td scope="col" id="modal-cod-${producto.id}">${producto['cod']}</td>
    <td scope="col" id="modal-name-${producto.id}">${producto['name']}</td>
    <td scope="col">${producto['cantidad']}</td>
    <td scope="col" id="modal-precio-unit-${producto.id}">${Math.round(producto['precio_unit'])}</td>
    <td><button class="btn btn-success" id="btn-item-choose-${producto['id']}">Elegir</button></td>`;

    return txt

}