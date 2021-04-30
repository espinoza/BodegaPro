from .models import MovEncabezado, MovItem

mov = MovEncabezado.objects.get(id=2)


def modificarStock(mov):
    ponderador = mov.tipo_mov.folio.signo_stock
    print(ponderador)
    items = mov.mov_items
    for item in items:
        producto_a_modificar = Producto.objects.get(id=item.producto.id)
        stock_a_modificar = Stock.objects.get(id=producto_a_modificar.id)
        print(producto_a_modificar)
        print(
            f"{stock_a_modificar.producto} tiene cantidad {stock_a_modificar.cantidad}")
        # Sacamos precio
        if stock_a_modificar.cantidad != 0:
            precio_actual = stock_a_modificar.monto_total/stock_a_modificar.cantidad
        else:
            precio_actual = 0
        # Modificamos cantidad. Si es entrada, el ponderador será +1. Si es salida restar+a
        stock_a_modificar.cantidad += item.producto.stock_data.cantidad*ponderador
        # Modificamos monto total
        if ponderador == 1:
            stock_a_modificar.monto_total += item.precio_unit*item.cant_ejecutada
        else:
            stock_a_modificar.monto_total -= precio_actual*item.cant_ejecutada


modificarStock(mov)
