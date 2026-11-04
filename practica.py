from datos import *
import threading

class GestorInventario:
    def __init__(self, inventario):
        self.inventario = inventario
        self.lock = threading.RLock()
        self.condicion_stock = threading.Condition(self.lock)

    def consultar_stock(self, producto):
        with self.lock:
            return self.inventario[producto]

    def comprobar_stock_suficiente(self, producto, unidades):
        with self.lock:
            cantidad = self.consultar_stock(producto)

            return cantidad >= unidades #Si la cantidad es mayor a las unidades que se quieren vender, significa que hay stock suficiente

    def vender_producto(self, producto, unidades):
        with self.condicion_stock: 

            while not self.comprobar_stock_suficiente(producto, unidades):
                self.condicion_stock.wait() #Espera si no hay stock suficiente

            self.inventario[producto] -= unidades

            return self.inventario[producto] #Devuelve el stock restante

    def reponer_producto(self, producto, unidades):
        with self.condicion_stock:

            self.inventario[producto] += unidades

            stock_actual = self.inventario[producto]

            self.condicion_stock.notify_all()

            return stock_actual

    def obtener_inventario(self):
        with self.lock:
            return list(self.inventario.items())

inventario = GestorInventario(STOCK_INICIAL.copy())
terminales = threading.Semaphore(NUM_TERMINALES)
barrera = threading.Barrier(NUM_REVISORES)

def trabajar_caja(numero_caja, pedidos, inventario):
     for pedido in pedidos:
        numero, producto, unidades = pedido

        terminales.acquire() # Espera hasta que haya una terminal disponible
        print(f"Caja {numero_caja}: obtiene un terminal para {numero}")

        try:
            stock_restante = inventario.vender_producto(producto, unidades) #Vende el pedido y devuelve el stock que quedó restante

        finally:
            terminales.release() # Libera el terminal aunque ocurra un error
            print(f"Caja {numero_caja}: libera el terminal de {numero}")

        print(
            f"Caja {numero_caja}: pedido {numero} procesado. "
            f"Vendidas: {unidades} unidades de {producto}. "
            f"Stock restante: {stock_restante}"
        )

def trabajar_almacen(reposiciones, inventario):
    for reposicion in reposiciones:
        codigo, producto, unidades = reposicion

        stock_actual = inventario.reponer_producto(producto, unidades)

        print(
            f"ALMACÉN: reposición {codigo}: "
            f"ALMACÉN: repone {unidades} unidades de {producto}. "
            f"Stock actual: {stock_actual}"
        )

def revisar_catalogo(numero_revisor, productos):
    print(f"Revisor {numero_revisor}: comienza la revisión")

    for producto, cantidad in productos:
        print(
            f"Revisor {numero_revisor}: revisa {producto} - "
            f"Stock: {cantidad} unidades"
        )

    print(f"Revisor {numero_revisor}: termina la revisión")
    barrera.wait() #Espera a que todos los revisores hayan termiando antes de continuar

    print(f'Revisor {numero_revisor}: supera la barrera')


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

hilos_revisores = []
productos = inventario.obtener_inventario()

for i in range(NUM_REVISORES):
    hilo_revision = threading.Thread(
        target=revisar_catalogo,
        args=(i + 1, productos[1::NUM_REVISORES])
    )
    hilos_revisores.append(hilo_revision)

hilo_almacen.start()

for hilo in hilos:
    hilo.start()

for hilo in hilos:
    hilo.join()

for hilo in hilos_revisores:
    hilo.start()

for hilo in hilos_revisores:
    hilo.join()

hilo_almacen.join()

print("\n================\nInventario final\n================")
for producto, cantidad in productos:
    print(f"{producto}: {cantidad} unidades")