from datos import *
import threading

inventario = STOCK_INICIAL.copy()


def trabajar_caja(numero_caja):
    siguiente_pedido = 0

    while siguiente_pedido < len(PEDIDOS):
        pedido = PEDIDOS[siguiente_pedido]
        siguiente_pedido += 1

        numero, producto, unidades = pedido

        stock = inventario[producto] 

        if stock >= unidades:
            inventario[producto] -= unidades
            print(
                f"Caja {numero_caja}: pedido {numero} procesado. "
                f"Producto: {producto}. "
                f"Unidades vendidas: {unidades}. "
                f"Stock restante: {inventario[producto]}"
            )
        else:
            print(
                f"Caja {numero_caja}: pedido {numero} rechazado "
                f"por falta de stock."
            )

hilos = []

for i in range(NUM_CAJAS):
    hilo = threading.Thread(
        target=trabajar_caja,
        args=(i + 1,)
    )
    hilos.append(hilo)

for hilo in hilos:
    hilo.start()

for hilo in hilos:
    hilo.join()

print('\n==========\nINVENTARIO\n==========')

for producto, cantidad in inventario.items():
    print(f'{producto}: {cantidad} unidades')