

$(document).on("click", "[id^=btn-item-choose-]", function(){
    id = $(this).attr('id').substring(16);
    console.log($(`#modal-name-${id}`).html())
    $("#id_cod").val($(`#modal-cod-${id}`).html())
    $("#id_name").val($(`#modal-name-${id}`).html())

    if ($("#id_cant_solicitada").val() == ""){
        $("#id_cant_solicitada").val('1')
    }

    $('#movprodModal').modal('hide');
    return false;
});

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
    $("ul.errorlist li").css('color','red');

})

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
    <td scope="col">${Math.round(producto['precio_unit'])}</td>
    <td><button class="btn btn-success" id="btn-item-choose-${producto['id']}">Elegir</button></td>`;

    return txt

}