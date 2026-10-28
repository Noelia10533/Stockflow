from datos import *
import threading

inventario = STOCK_INICIAL.copy()
lock_inventario = threading.Lock()


def trabajar_caja(numero_caja, pedido, inventario):
    numero, producto, unidades = pedido

    with lock_inventario:

        stock = inventario[producto] 

        if stock >= unidades:
            print(
                f"Caja {numero_caja}: {numero} comprueba "
                f"{stock} unidades disponibles"
            )
            inventario[producto] -= unidades

            print(
                f"Caja {numero_caja}: {numero} vende {unidades} unidades. "
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
        args=(i + 1, PEDIDOS[i], inventario)
    )
    hilos.append(hilo)

for hilo in hilos:
    hilo.start()

for hilo in hilos:
    hilo.join()

print("\n================\nInventario final\n================")
for producto, cantidad in inventario.items():
    print(f"{producto}: {cantidad} unidades")