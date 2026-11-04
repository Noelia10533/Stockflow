# Stockflow

En este proyecto se ha desarrollado Stockflow, una aplicación en Python cuyo objetivo es simular la gestión de un inventario en un establecimiento comercial mediante la programación concurrente.

A lo largo de las diferentes fases se han implementado distintos mecanismos de sincronización para gestionar el trabajo simultáneo de varias cajas, controlar las ventas y las reposiciones de productos y garantizar que los datos del inventario se mantengan correctamente actualizados.

## Estructura del proyecto

```
Stockflow/
├── datos.py
├── practica.py
├── README.md
└──.gitignore
```

## Archivo datos.py

La información utilizada durante la simulación se encuentra organizada de forma independiente a la lógica del programa. De esta manera, los datos se almacenan en el archivo `datos.py`, mientras que el código principal se encarga de gestionar las operaciones.

### STOCK_INICIAL

Es un diccionario que contiene los diferentes productos del inventario junto con la cantidad de unidades disponibles al comenzar la simulación.

```python
STOCK_INICIAL = {
    "Teclado mecanico": 18,
    "Monitor 24 pulgadas": 10,
    ...
}
```

Antes de comenzar a trabajar, el programa realiza una copia de este diccionario. Así, los cambios que se producen durante las ventas y reposiciones no modifican los datos originales.

### PEDIDOS

Contiene los pedidos que deben procesar las distintas cajas. Cada uno está formado por tres datos: el identificador del pedido, el producto solicitado y el número de unidades.

Ejemplo:

```python
("PED-001", "Teclado mecanico", 4)
```

### REPOSICIONES

Incluye las entradas de productos que realiza el almacén para aumentar las existencias del inventario. Cada registro indica el número de albarán, el producto que se repone y la cantidad de unidades añadidas.

Ejemplo:

```python
("ALB-001", "Monitor 24 pulgadas", 8)
```

### Configuración de la simulación

También se definen varias constantes que permiten establecer cómo se ejecutará el programa:

- `NUM_CAJAS`: indica cuántas cajas trabajarán al mismo tiempo.
- `NUM_TERMINALES`: establece cuántos terminales de pago pueden utilizarse simultáneamente como máximo.
- `NUM_REVISORES`: determina cuántos hilos se encargarán de revisar el inventario al finalizar la simulación.

## 1. Prueba de concurrencia y condición de carrera

La sección crítica comprende la consulta del stock, la comprobación de las unidades disponibles y la actualización del inventario. Estas operaciones no están protegidas, por lo que varias cajas pueden tomar decisiones basadas en información que deja de ser válida.

Se ejecuta la aplicación varias veces y se comprueba el stock final. Si varias cajas aceptan pedidos basándose en las mismas existencias iniciales, pueden venderse más unidades de las disponibles y el inventario puede quedar en negativo.

Este comportamiento constituye una condición de carrera, ya que el resultado depende de cómo se intercalan las operaciones de los distintos hilos.

## 2. Corrección de la condición de carrera mediante Lock

Se ha utilizado threading.Lock() para proteger el acceso al inventario compartido. El bloqueo se crea una sola vez y es utilizado por todas las cajas.

El uso de Lock evita que varias cajas comprueben simultáneamente el mismo stock y acepten pedidos que no pueden satisfacerse. De esta forma, se mantiene la coherencia del inventario compartido.

## 3. Control de concurrencia con Lock y Semaphore

La utilización de Lock y Semaphore permite controlar el acceso a los recursos compartidos y organizar el procesamiento concurrente de los pedidos. El bloqueo evita condiciones de carrera en el inventario, mientras que el semáforo limita el uso simultáneo de las terminales.

## 4. Gestión de reposiciones del almacén con Condition

La utilización de Condition permite coordinar las cajas y el almacén de forma eficiente, evitando la espera activa. Las cajas permanecen bloqueadas mientras no hay suficientes unidades y vuelven a comprobar el inventario cuando reciben una notificación. De esta forma, se mejora la sincronización entre los hilos y se gestiona correctamente el stock compartido.

## 5. Revisión del inventario mediante Barrier

En esta fase se incorporan varios hilos revisores cuya función es comprobar el inventario final una vez que todas las cajas han terminado de procesar los pedidos y el almacén ha realizado las reposiciones.

## 6. Refactorización con RLock

En esta fase se reorganiza la gestión del inventario mediante la creación de una clase llamada GestorInventario. Su objetivo es centralizar las operaciones relacionadas con la consulta y modificación del stock, evitando que las diferentes partes del programa accedan directamente al diccionario del inventario.

Se utiliza `threading.RLock()` para proteger las operaciones del inventario.

La principal diferencia respecto a Lock es que RLock permite que un mismo hilo adquiera varias veces el mismo bloqueo sin quedarse bloqueado.

Esto es necesario en nuestro diseño porque el método `comprobar_stock_suficiente()` llama a `consultar_stock()`. Ambos métodos utilizan el mismo bloqueo, por lo que el hilo necesita poder adquirirlo de nuevo mientras todavía lo tiene adquirido.

Con un Lock normal se produciría un bloqueo, ya que el hilo intentaría adquirir un bloqueo que él mismo mantiene ocupado. Con RLock, esta situación se resuelve permitiendo la reentrada del mismo hilo.

## 7. Prevención de deadlock

En esta fase se ha revisado el uso de los mecanismos de sincronización del programa para prevenir posibles situaciones de deadlock o interbloqueo.

Se han identificado los recursos utilizados por cada operación:

**RLock:** protege las operaciones relacionadas con el acceso y la modificación del inventario.

**Condition:** permite que las cajas esperen cuando no existe suficiente stock y que el almacén las notifique cuando realiza una reposición.

**Semaphore:** limita el número de cajas que pueden utilizar simultáneamente los terminales de pago.

**Barrier:** sincroniza los hilos revisores para que continúen cuando todos hayan llegado al punto de espera.

Para prevenir interbloqueos, se mantiene un orden coherente al adquirir los recursos y se evita mantener bloqueos durante operaciones que no necesitan protección, liberándolos lo antes posible.

Un posible deadlock podría producirse si dos hilos adquiriesen varios recursos en órdenes diferentes y cada uno esperase a que el otro liberase el recurso que necesita. Para evitarlo, se establece un orden único de adquisición y liberación de recursos.

Con estas medidas se mejora la seguridad de la ejecución concurrente y se reduce el riesgo de que los hilos queden bloqueados indefinidamente.

## Ejecución del programa

El proyecto no necesita instalar dependencias adicionales, ya que utiliza las herramientas incluidas en Python.

Para iniciar la simulación, basta con ejecutar el siguiente comando desde la terminal, situándose previamente en la carpeta del proyecto:

```
python main.py
```

Si se utiliza Windows, también es posible iniciarlo mediante:

```
py main.py
```

Durante la ejecución se muestran por pantalla diferentes mensajes que permiten seguir el funcionamiento del programa y observar cómo interactúan los distintos hilos:

1. Las cajas que esperan a que haya un terminal disponible.
2. Las cajas que consiguen acceder a los terminales de pago.
3. El procesamiento simultáneo de los pedidos y las ventas.
4. Las situaciones en las que una caja debe esperar porque no hay suficiente stock.
5. Las reposiciones realizadas por el almacén y los albaranes correspondientes.
6. Las cajas que se despiertan tras recibir una notificación de `Condition`.
7. El trabajo realizado por los diferentes hilos revisores.
8. Los revisores que esperan a que todos los demás lleguen a la `Barrier`.
9. El estado final del inventario una vez terminadas las operaciones.

## GitFlow utilizado

```
main
└── develop
    ├── feature/fase1
    ├── feature/fase2
    ├── feature/fase3
    ├── feature/fase4
    ├── feature/fase5
    ├── feature/fase6
    └── feature/fase7
```

## Conclusión

La realización de este proyecto ha permitido poner en práctica los conceptos de programación concurrente en Python mediante el desarrollo de Stockflow, una simulación de gestión de inventario en la que varias cajas, un almacén y diferentes revisores trabajan de forma simultánea.

A lo largo de las distintas fases se han implementado diferentes mecanismos de sincronización, como Lock, RLock, Semaphore, Condition y Barrier, comprendiendo la función de cada uno y cómo ayudan a coordinar los hilos y proteger los recursos compartidos.

Además, se han podido identificar y solucionar problemas habituales de la concurrencia, como las condiciones de carrera, los accesos simultáneos al inventario y los posibles interbloqueos (deadlocks). Esto ha permitido mejorar progresivamente la organización y la seguridad del programa.