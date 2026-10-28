from datos import *
import threading

inventario = STOCK_INICIAL.copy()
terminales = threading.Semaphore(NUM_TERMINALES)
condicion_stock = threading.Condition()


def trabajar_caja(numero_caja, pedidos, inventario):
     for pedido in pedidos:
        numero, producto, unidades = pedido

        terminales.acquire() # Espera hasta que haya una terminal disponible
        print(f"Caja {numero_caja}: obtiene un terminal para {numero}")

        try:
            with condicion_stock:
                while inventario[producto] < unidades:
                    print(
                        f"Caja {numero_caja}: pedido {numero} "
                        f"esperando reposición de {producto}"
                    )
                    condicion_stock.wait()

                    print(
                        f"Caja {numero_caja}: vuelve a comprobar "
                        f"el stock de {producto}"
                    )

                inventario[producto] -= unidades

                print(
                    f"Caja {numero_caja}: pedido {numero} procesado. "
                    f"Vendidas: {unidades} unidades de {producto}. "
                    f"Stock restante: {inventario[producto]}"
                )

        finally:
            terminales.release() # Libera el terminal aunque ocurra un error
            print(f"Caja {numero_caja}: libera el terminal de {numero}")

def trabajar_almacen(reposiciones, inventario):
    for reposicion in reposiciones:
        codigo, producto, unidades = reposicion

        with condicion_stock:
            inventario[producto] += unidades

            print(
                f"ALMACÉN: reposición {codigo}: "
                f"ALMACÉN: repone {unidades} unidades de {producto}. "
                f"Stock actual: {inventario[producto]}"
            )

            condicion_stock.notify_all()

hilos = []

for i in range(NUM_CAJAS):
    pedidos_caja = PEDIDOS[i::NUM_CAJAS]
    hilo = threading.Thread(
        target=trabajar_caja,
        args=(i + 1, pedidos_caja, inventario)
    )
    hilos.append(hilo)

hilo_almacen = threading.Thread(
    target=trabajar_almacen,
    args=(REPOSICIONES, inventario)
)

hilo_almacen.start()

for hilo in hilos:
    hilo.start()

for hilo in hilos:
    hilo.join()

hilo_almacen.join()

print("\n================\nInventario final\n================")
for producto, cantidad in inventario.items():
    print(f"{producto}: {cantidad} unidades")