from datos import *
import threading
import time

estados_pedidos = {}
tiempo_cobro = float(TIEMPO_COBRO)
longitud_cancelaciones = len(CANCELACIONES)

class GestorInventario:
    def __init__(self, inventario):
        self.inventario = inventario
        self.lock = threading.RLock() #Puede adquirir el mismo hilo varias veces y debe liberarlo el mismo número de veces
        self.condicion_stock = threading.Condition(self.lock) 

    def consultar_stock(self, producto):
        '''Lee el stock de un producto'''
        with self.lock: #Como máximo un hilo puede poseer el bloqueo a la vez
            return self.inventario[producto]

    def comprobar_stock_suficiente(self, producto, unidades):
        '''Comprobar si hay unidades. Llama a consultar_stock'''
        with self.lock:
            cantidad = self.consultar_stock(producto)

            return cantidad >= unidades #Si la cantidad es mayor a las unidades que se quieren vender, significa que hay stock suficiente

    def vender_producto(self, producto, unidades):
        '''Esperar hasta tener stock, restar unidades y devolver stock restante'''
        with self.condicion_stock: 

            while not self.comprobar_stock_suficiente(producto, unidades):
                self.condicion_stock.wait() #Espera si no hay stock suficiente

            self.inventario[producto] -= unidades

            return self.inventario[producto] #Devuelve el stock restante

    def reponer_producto(self, producto, unidades):
        '''Sumar unidades, guardar stock actual y despertar esperas'''
        with self.condicion_stock:

            self.inventario[producto] += unidades

            stock_actual = self.inventario[producto]

            self.condicion_stock.notify_all() #Indica que se vuelva a reevaluar la condición

            return stock_actual

    def obtener_inventario(self):
        '''Devolver una lista de items'''
        with self.lock:
            return list(self.inventario.items())

    def cancelar(self, cancelaciones, estado):
        with self.lock:
            rechazados = 0
            cancelados = 0
            lista_cancelacion = []
            for id_cancelacion, id_pedido, tiempo in cancelaciones:
                if id_pedido in estados_pedidos:
                    if estado[id_pedido] == 'PENDIENTE' or estado[id_pedido] == 'ESPERANDO_STOCK':
                        cancelados += 1
                        estado[id_pedido] = 'CANCELADO'
                        lista_cancelacion.append((id_pedido, estado[id_pedido]))
                        print(f'PEDIDO CANCELADO: {id_cancelacion} - {id_pedido}')
                        return
                    else:
                        rechazados += 1  
                        return
            return 


inventario = GestorInventario(STOCK_INICIAL.copy()) 
terminales = threading.Semaphore(NUM_TERMINALES) #El semáforo permite que hasta 3 cajas tengan un terminal a la vez. La cuarta caja que intente adquirir uno debe esperar a que otra lo libere
barrera = threading.Barrier(NUM_REVISORES) #La barrera se crea para 4 participantes
barrera_cancelaciones = threading.Barrier(longitud_cancelaciones)

def trabajar_caja(numero_caja, pedidos, inventario):
     for pedido in pedidos:
        numero, producto, unidades = pedido

        terminales.acquire() # Espera hasta que haya una terminal disponible. Toma los permiso. Sin permisos, bloquea al hilo hasta que alguien libere uno
        print(f"Caja {numero_caja}: obtiene un terminal para {numero}")
        estados_pedidos[numero] = 'PENDIENTE'

        try:
            tiempo_inicial = time.monotonic()
            estados_pedidos[numero] = 'EN_COBRO'
            tiempo_acabado = tiempo_inicial + tiempo_cobro

            if tiempo_acabado:
                estados_pedidos[numero] = 'PENDIENTE'
                return
        
            stock_restante = inventario.vender_producto(producto, unidades) #Vende el pedido y devuelve el stock que quedó restante
            estados_pedidos[numero] = 'COMPLETADO'

        finally:
            terminales.release() # Libera el terminal aunque ocurra un error. Devuelve los permisos
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


def comprobar_cancelacion(cancelaciones, estado):
    for pedido in estados_pedidos:
        cancelar_funcion = cancelaciones.cancelar(CANCELACIONES, pedido[estado]) 


hilos = []

for i in range(NUM_CAJAS): #Se procesan tanto pedidos como número de cajas
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

hilos_cancelar = []
for i in range(NUM_CAJAS):
    cancelaciones_caja = CANCELACIONES[i::NUM_CAJAS]
    hilo_cancelar = threading.Thread(
        target=comprobar_cancelacion,
        args=(cancelaciones_caja,)
    )
    hilos_cancelar.append(hilo_cancelar)

hilo_almacen.start()

for hilo in hilos:
    hilo.start()

for hilo in hilos:
    hilo.join()

for hilo in hilos_revisores:
    hilo.start()

for hilo in hilos_revisores:
    hilo.join()

for hilo in hilos_cancelar:
    hilo.start()

for hilo in hilos_cancelar:
    hilo.join()

hilo_almacen.join()

print("\n================\nInventario final\n================")
for producto, cantidad in productos:
    print(f"{producto}: {cantidad} unidades")
