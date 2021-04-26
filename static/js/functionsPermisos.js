$(document).ready( function(){

    $("[id$=-solicita]").click( function(){
        id = $(this).attr('id').substr(0, $(this).attr('id').indexOf('-'));
        tipomov_id = $('#tipo_mov').val();
        toggle_solicita(`${id}-${tipomov_id}`);
    })

    $("[id$=-autoriza]").click( function(){
        id = $(this).attr('id').substr(0, $(this).attr('id').indexOf('-')); 
        tipomov_id = $('#tipo_mov').val();
        toggle_autoriza(`${id}-${tipomov_id}`);
    })

    $("[id$=-ejecuta]").click( function(){
        id = $(this).attr('id').substr(0, $(this).attr('id').indexOf('-')); 
        tipomov_id = $('#tipo_mov').val();
        toggle_ejecuta(`${id}-${tipomov_id}`);
    })

    $('#tipo_mov').change( function(){
        showCurrentTablaPermisos();
    })


})

function showCurrentTablaPermisos(){
    tipomov_id = $('#tipo_mov').val();
    $('[id^=table-body-]').hide()
    $(`#table-body-${tipomov_id}`).show()
    $('#btn-submit').html('Guardar Permisos ' + $('#tipo_mov option:selected').text())
}

function toggle_solicita(id){
    miInput = $(`#input-${id}`)
    valor_old = miInput.val().substr(0,1)
    resto = miInput.val().substring(1)
    miBtn = $(`#${id}-solicita`)
    if (valor_old == 0){
        miInput.val("1"+resto)
        miBtn.html("SI")
        miBtn.removeClass( "btn-outline-danger" ).addClass( "btn-success" );
    } else {
        miInput.val("0"+resto)
        miBtn.html("NO")
        miBtn.removeClass( "btn-success" ).addClass( "btn-outline-danger" );
    } 
}

function toggle_ejecuta(id){
    miInput = $(`#input-${id}`)
    valor_old = miInput.val().substring(2)
    resto = miInput.val().substr(0,2)
    miBtn = $(`#${id}-ejecuta`)
    if (valor_old == 0){
        miInput.val(resto+"1")
        miBtn.html("SI")
        miBtn.removeClass( "btn-outline-danger" ).addClass( "btn-success" );
    } else {
        miInput.val(resto+"0")
        miBtn.html("NO")
        miBtn.removeClass( "btn-success" ).addClass( "btn-outline-danger" );
    } 
}

function toggle_autoriza(id){
    miInput = $(`#input-${id}`)
    valor_old = miInput.val().substr(1,1)
    resto1 = miInput.val().substr(0,1)
    resto2 = miInput.val().substring(2)
    miBtn = $(`#${id}-autoriza`)
    if (valor_old == 0){
        miInput.val(resto1+"1"+resto2)
        miBtn.html("SI")
        miBtn.removeClass( "btn-outline-danger" ).addClass( "btn-success" );
    } else {
        miInput.val(resto1+"0"+resto2)
        miBtn.html("NO")
        miBtn.removeClass( "btn-success" ).addClass( "btn-outline-danger" );
    } 
}