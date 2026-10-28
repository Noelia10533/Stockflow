from datos import *
import threading

inventario = STOCK_INICIAL.copy()
lock_inventario = threading.Lock()
terminales = threading.Semaphore(NUM_TERMINALES)


def trabajar_caja(numero_caja, pedidos, inventario):
     for pedido in pedidos:
        numero, producto, unidades = pedido

        terminales.acquire() # Espera hasta que haya una terminal disponible
        print(f"Caja {numero_caja}: obtiene un terminal para {numero}")

        try:
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
        finally:
            terminales.release() # Libera el terminal aunque ocurra un error
            print(f"Caja {numero_caja}: libera el terminal de {numero}")

hilos = []

for i in range(NUM_CAJAS):
    pedidos_caja = PEDIDOS[i::NUM_CAJAS]
    hilo = threading.Thread(
        target=trabajar_caja,
        args=(i + 1, pedidos_caja, inventario)
    )
    hilos.append(hilo)

for hilo in hilos:
    hilo.start()

for hilo in hilos:
    hilo.join()

print("\n================\nInventario final\n================")
for producto, cantidad in inventario.items():
    print(f"{producto}: {cantidad} unidades")